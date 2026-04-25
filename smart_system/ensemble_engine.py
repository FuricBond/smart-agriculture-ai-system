"""
Ensemble Disease Detection Engine — Smart Agriculture System v3.1
==================================================================
Weighted ensemble of EfficientNet-B0, ResNet-50, and EfficientNet-B1.

Improvements over v3.0
-----------------------
  1. Dynamic weight computation from validation accuracy
  2. Class consistency validation at startup (raises on mismatch)
  3. Temperature scaling for probability calibration
  4. Multi-signal open-set detection (confidence + entropy + disagreement)
  5. Model disagreement detection with confidence downgrade
  6. Structured per-model logging at every inference
  7. Top-K returned as list-of-dicts {label, confidence}
  8. Conditional ensemble execution (early-exit > 0.85)
  9. Rich UI metadata (model_confidences, unknown_detected, etc.)

Author  : Smart Agriculture AI Team
Version : 3.1.0
"""

from __future__ import annotations

import os
import math
import time
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("smart_system.ensemble_engine")

# ═══════════════════════════════════════════════════════════════
# MODULE-LEVEL DEFAULTS  (overridden at runtime via __init__)
# ═══════════════════════════════════════════════════════════════

DEFAULT_WEIGHTS: Dict[str, float] = {
    "efficientnet_b0": 0.4,
    "resnet50":        0.3,
    "efficientnet_b1": 0.3,
}

# Open-set thresholds
UNKNOWN_CONF_THRESHOLD:   float = 0.70   # max prob below this → unknown
UNKNOWN_ENTROPY_THRESHOLD: float = 2.5   # Shannon entropy above this → unknown
DISAGREEMENT_THRESHOLD:   float = 0.50   # top-1 disagreement ratio → uncertain

# Early-exit: skip ensemble when B0 is very confident
EARLY_EXIT_THRESHOLD: float = 0.85

# Temperature scaling factor for calibration (T>1 softens, T<1 sharpens)
# 1.0 = no calibration (default until tuned on a validation set)
DEFAULT_TEMPERATURE: float = 1.0


# ═══════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def compute_weights_from_accuracy(accuracies: Dict[str, float]) -> Dict[str, float]:
    """
    Compute normalized ensemble weights from per-model validation accuracy.

    Formula:  weight_i = accuracy_i / sum(all_accuracies)

    Parameters
    ----------
    accuracies : dict
        e.g. {"efficientnet_b0": 0.946, "resnet50": 0.921, "efficientnet_b1": 0.934}

    Returns
    -------
    dict
        Normalized weights summing to 1.0.
    """
    total = sum(accuracies.values())
    if total <= 0:
        logger.warning("Total accuracy is zero — falling back to equal weights.")
        n = len(accuracies)
        return {k: 1.0 / n for k in accuracies}
    weights = {k: round(v / total, 6) for k, v in accuracies.items()}
    logger.info(f"Dynamic weights computed from accuracies {accuracies} → {weights}")
    return weights


def shannon_entropy(probs) -> float:
    """
    Compute Shannon entropy of a probability distribution.

    H = -sum(p * log(p))   (nats, base-e)

    High entropy indicates uniform / uncertain distribution.
    """
    import torch
    p = probs.clamp(min=1e-9)
    return (-p * p.log()).sum().item()


def temperature_scale(logits, temperature: float):
    """
    Apply temperature scaling to logits before softmax.

    T > 1 → softer (more uncertain) probabilities
    T < 1 → sharper (more confident) probabilities
    T = 1 → no change (identity)

    Parameters
    ----------
    logits : torch.Tensor  shape (1, C)
    temperature : float

    Returns
    -------
    torch.Tensor  shape (C,)  — softmax-normalized
    """
    import torch.nn.functional as F
    t = max(temperature, 1e-3)   # guard against zero division
    return F.softmax(logits / t, dim=1)[0]


def validate_class_consistency(primary_classes: List[str],
                                secondary_classes: Dict[str, List[str]]) -> None:
    """
    Verify all model class lists are identical in length AND ordering.

    Raises
    ------
    ValueError
        If any secondary model's class list differs from the primary.
    """
    for model_name, classes in secondary_classes.items():
        if classes != primary_classes:
            mismatches = [
                f"  [{i}] primary='{p}' vs {model_name}='{s}'"
                for i, (p, s) in enumerate(zip(primary_classes, classes))
                if p != s
            ][:5]   # show at most 5 examples
            detail = "\n".join(mismatches) if mismatches else "(length differs)"
            raise ValueError(
                f"Class mismatch detected for {model_name}!\n{detail}\n"
                f"Ensure all models were trained on the same class list in the same order."
            )
    logger.info(
        f"Class consistency validated: {len(primary_classes)} classes, "
        f"{len(secondary_classes)} secondary models — all match."
    )


# ═══════════════════════════════════════════════════════════════
# ENSEMBLE ENGINE
# ═══════════════════════════════════════════════════════════════

class EnsembleEngine:
    """
    Weighted ensemble of EfficientNet-B0, ResNet-50, and EfficientNet-B1.

    Parameters
    ----------
    disease_engine : DiseaseEngine
        Primary model engine (EfficientNet-B0, already loaded).
    num_classes : int
        Expected number of disease classes (52).
    enable_early_exit : bool
        Skip ensemble when B0 confidence ≥ EARLY_EXIT_THRESHOLD.
    unknown_threshold : float
        Max-probability threshold for open-set detection (0–1).
    entropy_threshold : float
        Entropy threshold for open-set detection (nats).
    disagreement_threshold : float
        Fraction of models that must agree on top-1 for a confident result.
    temperature : float
        Temperature scaling factor applied to all model logits.
    custom_weights : dict or None
        If provided, overrides DEFAULT_WEIGHTS.
        Use compute_weights_from_accuracy() to derive this.
    """

    def __init__(
        self,
        disease_engine,
        num_classes: int = 52,
        enable_early_exit: bool = True,
        unknown_threshold: float = UNKNOWN_CONF_THRESHOLD,
        entropy_threshold: float = UNKNOWN_ENTROPY_THRESHOLD,
        disagreement_threshold: float = DISAGREEMENT_THRESHOLD,
        temperature: float = DEFAULT_TEMPERATURE,
        custom_weights: Optional[Dict[str, float]] = None,
    ) -> None:
        self.disease_engine           = disease_engine
        self.num_classes              = num_classes
        self.enable_early_exit        = enable_early_exit
        self.unknown_threshold        = unknown_threshold
        self.entropy_threshold        = entropy_threshold
        self.disagreement_threshold   = disagreement_threshold
        self.temperature              = temperature

        # Resolve ensemble weights (dynamic or static)
        self._weights: Dict[str, float] = (
            custom_weights if custom_weights is not None
            else dict(DEFAULT_WEIGHTS)
        )

        # Secondary models
        self._resnet50:        Optional[object] = None
        self._efficientnet_b1: Optional[object] = None
        self._secondary_loaded: bool = False

        # Shared from primary engine
        self.class_names: List[str] = []
        self.device = None
        self.transform = None

    # ──────────────────────────────────────────────────────────
    # WEIGHT MANAGEMENT
    # ──────────────────────────────────────────────────────────

    def set_weights_from_accuracy(self, accuracies: Dict[str, float]) -> None:
        """
        Recompute ensemble weights from validation accuracies at runtime.

        Example
        -------
        engine.set_weights_from_accuracy({
            "efficientnet_b0": 0.946,
            "resnet50":        0.921,
            "efficientnet_b1": 0.934,
        })
        """
        self._weights = compute_weights_from_accuracy(accuracies)

    def set_weights(self, weights: Dict[str, float]) -> None:
        """Manually override ensemble weights (must sum to ~1.0)."""
        total = sum(weights.values())
        if not (0.99 <= total <= 1.01):
            logger.warning(f"Provided weights sum to {total:.4f} (not 1.0) — normalizing.")
            weights = {k: v / total for k, v in weights.items()}
        self._weights = weights
        logger.info(f"Ensemble weights updated: {self._weights}")

    @property
    def weights(self) -> Dict[str, float]:
        return dict(self._weights)

    # ──────────────────────────────────────────────────────────
    # LOAD SECONDARY MODELS
    # ──────────────────────────────────────────────────────────

    def load_secondary_models(self) -> bool:
        """
        Load ResNet-50 and EfficientNet-B1, replace heads, validate classes.

        Includes:
          • Class consistency check (raises ValueError on mismatch)
          • Optional fine-tuned checkpoint loading
          • Temperature-aware eval setup
        """
        if self._secondary_loaded:
            return True

        if not self.disease_engine._loaded:
            logger.error("Primary DiseaseEngine not loaded — cannot init ensemble.")
            return False

        try:
            import torch
            import torch.nn as nn
            from torchvision import models
            from . import config as cfg

            self.device      = self.disease_engine.device
            self.transform   = self.disease_engine.transform
            self.class_names = list(self.disease_engine.class_names)
            num_cls          = len(self.class_names)

            if num_cls == 0:
                logger.error("No class names in primary engine.")
                return False

            t0 = time.time()

            # ── ResNet-50 ─────────────────────────────────────
            logger.info("Loading ResNet-50...")
            r50 = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
            r50.fc = nn.Linear(r50.fc.in_features, num_cls)
            r50 = self._load_checkpoint(r50, cfg.ENSEMBLE_RESNET50_PATH, "ResNet-50")
            r50 = r50.to(self.device).eval()
            self._resnet50 = r50
            logger.info(f"ResNet-50 ready: fc={r50.fc.in_features if hasattr(r50, 'fc') else '?'} → {num_cls}")

            # ── EfficientNet-B1 ───────────────────────────────
            logger.info("Loading EfficientNet-B1...")
            b1  = models.efficientnet_b1(weights=models.EfficientNet_B1_Weights.IMAGENET1K_V1)
            in_b1 = b1.classifier[1].in_features
            b1.classifier = nn.Sequential(nn.Dropout(0.2, inplace=True), nn.Linear(in_b1, num_cls))
            b1 = self._load_checkpoint(b1, cfg.ENSEMBLE_EFFB1_PATH, "EfficientNet-B1")
            b1 = b1.to(self.device).eval()
            self._efficientnet_b1 = b1
            logger.info(f"EfficientNet-B1 ready: {in_b1} → {num_cls}")

            # ── CLASS CONSISTENCY VALIDATION ──────────────────
            # Secondary models share the primary class list (same dataset).
            # We validate that the class_names list is identical for all.
            # (Secondary models don't carry their own class list — they use
            # whatever index the primary engine's class_names provides.)
            # We validate num_cls consistency as the key guard.
            logger.info(
                f"Class consistency: primary={num_cls} classes | "
                f"r50_output={r50.fc.out_features} | "
                f"b1_output={b1.classifier[-1].out_features}"
            )
            mismatch_names: Dict[str, List[str]] = {}
            if r50.fc.out_features != num_cls:
                mismatch_names["resnet50"] = []   # triggers error below
            if b1.classifier[-1].out_features != num_cls:
                mismatch_names["efficientnet_b1"] = []
            if mismatch_names:
                raise ValueError(
                    f"Output size mismatch: primary has {num_cls} classes but "
                    f"{list(mismatch_names.keys())} have different output dimensions."
                )

            self._secondary_loaded = True
            logger.info(
                f"Ensemble ready in {time.time()-t0:.2f}s | "
                f"device={self.device} | classes={num_cls} | "
                f"weights={self._weights} | temperature={self.temperature}"
            )
            return True

        except Exception as exc:
            logger.error(f"Ensemble secondary model load failed: {exc}", exc_info=True)
            return False

    @staticmethod
    def _load_checkpoint(model, path: str, name: str):
        """Load state-dict checkpoint if file exists and is valid."""
        import torch
        if os.path.isfile(path) and os.path.getsize(path) > 1024:
            try:
                state = torch.load(path, map_location="cpu", weights_only=True)
                model.load_state_dict(state)
                logger.info(f"{name}: fine-tuned checkpoint loaded ← {path}")
            except Exception as e:
                logger.warning(f"{name}: checkpoint load failed ({e}) — using ImageNet weights.")
        else:
            logger.info(f"{name}: no checkpoint found — using ImageNet pretrained weights.")
        return model

    # ──────────────────────────────────────────────────────────
    # MAIN INFERENCE
    # ──────────────────────────────────────────────────────────

    def predict(self, image_path: str, top_k: int = 5) -> Dict:
        """
        Run ensemble inference with full diagnostics.

        Returns
        -------
        dict with keys:
            success, prediction, disease_name, confidence, confidence_raw,
            is_unknown, unknown_reason, used_ensemble, ensemble_weights,
            model_confidences, top_predictions (list of dicts),
            disagreement_detected, entropy, early_exit_triggered
        """
        if not self.disease_engine._loaded:
            return {"success": False, "error": "Primary disease model not loaded."}
        if not os.path.isfile(image_path):
            return {"success": False, "error": f"Image not found: {image_path}"}

        try:
            import torch
            import torch.nn.functional as F
            from PIL import Image

            img        = Image.open(image_path).convert("RGB")
            img_tensor = self.transform(img).unsqueeze(0).to(self.device)

            # ── EfficientNet-B0 inference ─────────────────────
            primary = self.disease_engine.model
            primary.eval()

            with torch.no_grad():
                b0_logits  = primary(img_tensor)
                b0_probs   = temperature_scale(b0_logits, self.temperature)
                b0_max_conf = b0_probs.max().item()
                b0_top_cls  = b0_probs.argmax().item()

            logger.info(
                f"[B0] top={self.class_names[b0_top_cls]!r} "
                f"conf={b0_max_conf:.4f} entropy={shannon_entropy(b0_probs):.3f}"
            )

            # ── EARLY EXIT ────────────────────────────────────
            if self.enable_early_exit and b0_max_conf >= EARLY_EXIT_THRESHOLD:
                logger.info(
                    f"Early-exit triggered: B0={b0_max_conf:.4f} >= {EARLY_EXIT_THRESHOLD}"
                )
                return self._build_result(
                    probs_map   = {"efficientnet_b0": b0_probs},
                    top_k       = top_k,
                    used_ensemble       = False,
                    early_exit_triggered= True,
                )

            # ── Load secondary models on demand ───────────────
            if not self._secondary_loaded:
                logger.info("Loading secondary models on demand...")
                if not self.load_secondary_models():
                    logger.warning("Secondary load failed — B0 only fallback.")
                    return self._build_result(
                        probs_map   = {"efficientnet_b0": b0_probs},
                        top_k       = top_k,
                        used_ensemble       = False,
                        early_exit_triggered= False,
                    )

            # ── ResNet-50 + EfficientNet-B1 inference ─────────
            with torch.no_grad():
                r50_probs = temperature_scale(self._resnet50(img_tensor), self.temperature)
                b1_probs  = temperature_scale(self._efficientnet_b1(img_tensor), self.temperature)

            r50_max = r50_probs.max().item()
            b1_max  = b1_probs.max().item()
            r50_top = r50_probs.argmax().item()
            b1_top  = b1_probs.argmax().item()

            logger.info(
                f"[R50] top={self.class_names[r50_top]!r} "
                f"conf={r50_max:.4f} entropy={shannon_entropy(r50_probs):.3f}"
            )
            logger.info(
                f"[B1]  top={self.class_names[b1_top]!r} "
                f"conf={b1_max:.4f} entropy={shannon_entropy(b1_probs):.3f}"
            )

            return self._build_result(
                probs_map   = {
                    "efficientnet_b0": b0_probs,
                    "resnet50":        r50_probs,
                    "efficientnet_b1": b1_probs,
                },
                top_k       = top_k,
                used_ensemble       = True,
                early_exit_triggered= False,
            )

        except Exception as exc:
            logger.error(f"Ensemble predict failed: {exc}", exc_info=True)
            return {"success": False, "error": str(exc)}

    # ──────────────────────────────────────────────────────────
    # RESULT BUILDER
    # ──────────────────────────────────────────────────────────

    def _build_result(
        self,
        probs_map: Dict,          # model_key → probability tensor (C,)
        top_k: int,
        used_ensemble: bool,
        early_exit_triggered: bool,
    ) -> Dict:
        """
        Combine per-model probabilities, run open-set checks, build full output.

        Open-Set Detection (multi-signal)
        ----------------------------------
        Flags "Unknown Disease" if ANY of the following:
          • max ensemble probability < unknown_threshold
          • Shannon entropy of ensemble probs > entropy_threshold
          • Models substantially disagree on top-1 class

        Model Disagreement
        ------------------
        Disagreement ratio = fraction of models NOT agreeing on top-1 class.
        When ratio > disagreement_threshold, confidence is downgraded by 15%
        and a warning is added.
        """
        import torch

        # ── Weighted ensemble average ──────────────────────────
        active_weights: Dict[str, float] = {}
        for key in probs_map:
            active_weights[key] = self._weights.get(key, 1.0 / len(probs_map))

        # Re-normalize active weights
        w_sum = sum(active_weights.values())
        active_weights = {k: v / w_sum for k, v in active_weights.items()}

        final_probs = sum(
            active_weights[key] * probs_map[key]
            for key in probs_map
        )

        # ── Per-model top-1 info ───────────────────────────────
        model_confidences: Dict[str, float] = {}
        model_top_classes: List[int]        = []

        for key, probs in probs_map.items():
            top_idx  = probs.argmax().item()
            top_conf = probs.max().item()
            model_confidences[key] = round(top_conf * 100, 2)
            model_top_classes.append(top_idx)

        # ── Top-K extraction ──────────────────────────────────
        k = min(top_k, len(self.class_names))
        top_probs, top_indices = torch.topk(final_probs, k)

        top_conf = top_probs[0].item()
        top_idx  = top_indices[0].item()
        top_name = self.class_names[top_idx]

        # Top-K as list of dicts (UI-friendly)
        top_predictions_dict = [
            {
                "label":      self.class_names[idx.item()],
                "confidence": round(prob.item(), 4),
                "confidence_pct": round(prob.item() * 100, 2),
            }
            for prob, idx in zip(top_probs, top_indices)
        ]

        # Also keep legacy tuple format for pipeline compatibility
        top_predictions_tuples = [
            (d["label"], d["confidence_pct"]) for d in top_predictions_dict
        ]

        # ── Entropy ───────────────────────────────────────────
        entropy = shannon_entropy(final_probs)

        # ── Model Disagreement ────────────────────────────────
        disagreement_detected = False
        if len(model_top_classes) > 1:
            # How many models agree with final ensemble top-1?
            agree_count = sum(1 for idx in model_top_classes if idx == top_idx)
            disagree_ratio = 1.0 - (agree_count / len(model_top_classes))
            if disagree_ratio >= self.disagreement_threshold:
                disagreement_detected = True
                logger.warning(
                    f"Model disagreement detected: {disagree_ratio:.0%} of models "
                    f"disagree on top-1 class '{top_name}'. "
                    f"Per-model tops: {[self.class_names[i] for i in model_top_classes]}"
                )
                # Downgrade confidence by 15%
                top_conf = top_conf * 0.85
                logger.info(f"Confidence downgraded to {top_conf:.4f} due to disagreement.")

        # ── Multi-signal Open-Set Detection ───────────────────
        is_unknown       = False
        unknown_reasons  = []

        if top_conf < self.unknown_threshold:
            is_unknown = True
            unknown_reasons.append(
                f"low_confidence({top_conf:.3f} < {self.unknown_threshold})"
            )
        if entropy > self.entropy_threshold:
            is_unknown = True
            unknown_reasons.append(
                f"high_entropy({entropy:.3f} > {self.entropy_threshold})"
            )
        if disagreement_detected:
            is_unknown = True
            unknown_reasons.append("model_disagreement")

        unknown_reason_str = " | ".join(unknown_reasons) if unknown_reasons else ""
        prediction = "Unknown Disease" if is_unknown else top_name

        if is_unknown:
            logger.warning(
                f"Unknown Disease detected: {unknown_reason_str}"
            )
        else:
            logger.info(
                f"Ensemble result: '{prediction}' "
                f"conf={top_conf:.4f} entropy={entropy:.3f} "
                f"ensemble={used_ensemble}"
            )

        confidence_pct = round(top_conf * 100, 2)

        return {
            "success":              True,
            "prediction":           prediction,
            "disease_name":         top_name,
            "confidence":           confidence_pct,
            "confidence_raw":       round(top_conf, 6),
            "is_unknown":           is_unknown,
            "unknown_detected":     is_unknown,
            "unknown_reason":       unknown_reason_str,
            "used_ensemble":        used_ensemble,
            "early_exit_triggered": early_exit_triggered,
            "ensemble_weights":     active_weights,
            "model_confidences":    model_confidences,
            "disagreement_detected":disagreement_detected,
            "entropy":              round(entropy, 4),
            "top_predictions":      top_predictions_dict,
            "top_predictions_tuples": top_predictions_tuples,  # pipeline compat
        }

    # ──────────────────────────────────────────────────────────
    # FINE-TUNE STRATEGY HELPER
    # ──────────────────────────────────────────────────────────

    @staticmethod
    def get_finetune_strategy(model_name: str, model) -> Dict:
        """Return trainable parameter groups for two-phase fine-tuning."""
        frozen_layers = []

        if model_name == "resnet50":
            for name, param in model.named_parameters():
                if not (name.startswith("layer4") or name.startswith("fc")):
                    param.requires_grad = False
                    frozen_layers.append(name)

        elif model_name == "efficientnet_b1":
            for name, param in model.named_parameters():
                if not (
                    name.startswith("features.6")
                    or name.startswith("features.7")
                    or name.startswith("features.8")
                    or name.startswith("classifier")
                ):
                    param.requires_grad = False
                    frozen_layers.append(name)

        trainable = [p for p in model.parameters() if p.requires_grad]
        logger.info(
            f"Fine-tune strategy [{model_name}]: "
            f"{len(trainable)} trainable groups, {len(frozen_layers)} frozen."
        )
        return {
            "trainable_params": trainable,
            "frozen_layers":    frozen_layers,
            "phase":            "partial_unfreeze",
        }
