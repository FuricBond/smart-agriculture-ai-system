"""
Plant Doctor Pipeline v3.0 — Master Orchestrator
=====================================================
Chains all modular post-processing stages into a single
unified prediction pipeline with decision support.

Pipeline Stages (13 total)
---------------------------
   1. Image Quality Check (pre-processing)
   2. Core Model Inference (Ensemble: EfficientNet-B0 + ResNet-50 + EfficientNet-B1)
   3. Confidence Calibration (temperature scaling + soft cap)
   4. Label Parsing (Plant + Disease)
   5. Open-World Detection
   6. Multi-Label Top-K Output
   7. Grad-CAM Heatmap Generation (EfficientNet-B0 ONLY)
   8. Severity Estimation
   9. Risk Assessment
  10. Explanation Engine
  11. Treatment Recommendations
  12. Similarity Search
  13. Final Output Enhancement (user-centric polish)

Author  : Smart Agriculture AI Team
Version : 3.0.0
"""

from __future__ import annotations

import os
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

logger = logging.getLogger("plant_doctor.pipeline")


class PlantDoctorPipeline:
    """
    End-to-end AI Plant Doctor prediction and decision support pipeline.

    Wraps the existing DiseaseEngine and adds modular
    post-processing stages WITHOUT modifying the core model.

    Parameters
    ----------
    disease_engine : DiseaseEngine
        The pre-loaded disease detection engine.
    output_dir : str
        Directory for saving Grad-CAM overlays and artifacts.
    enable_gradcam : bool
        Whether to generate Grad-CAM heatmaps (default True).
    enable_similarity : bool
        Whether to perform FAISS similarity search (default True).
    unknown_threshold : float
        Confidence threshold for open-world detection (0-100).
    """

    def __init__(
        self,
        disease_engine,
        output_dir: str = None,
        enable_gradcam: bool = True,
        enable_similarity: bool = True,
        unknown_threshold: float = 60.0,
        ensemble_engine=None,        # NEW: optional EnsembleEngine instance
    ) -> None:
        from .image_quality import ImageQualityChecker
        from .confidence_calibrator import ConfidenceCalibrator
        from .open_world import OpenWorldDetector
        from .severity import SeverityEstimator
        from .risk_assessor import RiskAssessor
        from .explanation_engine import ExplanationEngine
        from .treatment_engine import TreatmentEngine
        from .label_parser import LabelParser
        from .display_formatter import DisplayFormatter
        from .final_output_enhancer import FinalOutputEnhancer

        self.disease_engine = disease_engine
        self.output_dir = output_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "tmp", "plant_doctor_output"
        )
        os.makedirs(self.output_dir, exist_ok=True)

        # ── Ensemble Engine (optional) ─────────────────────────
        # When provided, Stage 2 uses ensemble inference.
        # Grad-CAM (Stage 7) always uses EfficientNet-B0 only.
        self._ensemble_engine = ensemble_engine
        self._ensemble_predictor = None
        if ensemble_engine is not None:
            try:
                from .ensemble_predictor import EnsemblePredictor
                self._ensemble_predictor = EnsemblePredictor(ensemble_engine)
                logger.info("EnsemblePredictor initialized — Stage 2 will use ensemble inference")
            except Exception as ep_err:
                logger.warning(f"EnsemblePredictor init failed: {ep_err} — falling back to single model")
                self._ensemble_predictor = None

        # -- Initialize sub-modules --
        self.quality_checker = ImageQualityChecker()
        self.calibrator = ConfidenceCalibrator()
        self.open_world = OpenWorldDetector(
            confidence_threshold=unknown_threshold
        )
        self.severity_estimator = SeverityEstimator()
        self.risk_assessor = RiskAssessor()
        self.explanation_engine = ExplanationEngine()
        self.treatment_engine = TreatmentEngine()
        self.label_parser = LabelParser()
        self.display_formatter = DisplayFormatter()
        self.output_enhancer = FinalOutputEnhancer()

        # -- CLIP open-world fallback (safe init) --
        self._clip_model = None
        try:
            from .clip_model import CLIPModel
            self._clip_model = CLIPModel()
            logger.info("CLIP open-world model loaded")
        except ImportError:
            logger.info("CLIP not installed -- open-world fallback disabled")
        except Exception as e:
            logger.warning(f"CLIP init failed: {e}")

        # -- PlantNet API --
        self._plantnet = None
        try:
            from .plantnet_api import PlantNetAPI
            # Fetch API key from env or use a default one
            api_key = os.getenv("PLANTNET_API_KEY")
            self._plantnet = PlantNetAPI(api_key=api_key)
            logger.info("PlantNet API integration loaded")
        except Exception as e:
            logger.warning(f"PlantNet init failed: {e}")

        # -- Conditional modules (require model internals) --
        self._gradcam = None
        self._feature_extractor = None
        self._similarity_search = None
        self._enable_gradcam = enable_gradcam
        self._enable_similarity = enable_similarity

        # Lazy-initialize Grad-CAM and similarity search
        self._modules_initialized = False

    def _lazy_init_modules(self):
        """Initialize Grad-CAM and similarity search modules lazily."""
        if self._modules_initialized:
            return

        if not self.disease_engine._loaded:
            logger.warning("Disease engine not loaded -- skipping module init")
            return

        model = self.disease_engine.model
        arch = self.disease_engine._architecture
        device = self.disease_engine.device

        # -- Grad-CAM --
        if self._enable_gradcam:
            try:
                from .gradcam import GradCAMGenerator
                self._gradcam = GradCAMGenerator(model, arch, device)
                logger.info("Grad-CAM module initialized")
            except Exception as e:
                logger.warning(f"Grad-CAM init failed: {e}")
                self._gradcam = None

        # -- Similarity Search --
        if self._enable_similarity:
            try:
                from .similarity import DiseaseSimilaritySearch, FeatureExtractor
                self._feature_extractor = FeatureExtractor(model, arch, device)
                self._similarity_search = DiseaseSimilaritySearch()
                if not self._similarity_search.load_index():
                    logger.info(
                        "FAISS index not available. Similarity search will "
                        "return empty results. Run build_faiss_index.py to create it."
                    )
            except ImportError:
                logger.info(
                    "FAISS not installed -- similarity search disabled. "
                    "Install: pip install faiss-cpu"
                )
            except Exception as e:
                logger.warning(f"Similarity search init failed: {e}")

        self._modules_initialized = True

    # ==============================================================
    # MAIN PIPELINE ENTRY POINT
    # ==============================================================

    def diagnose(
        self,
        image_path: str,
        top_k: int = 5,
    ) -> Dict:
        """
        Run the full plant doctor diagnostic pipeline.

        Parameters
        ----------
        image_path : str
            Absolute path to the leaf image.
        top_k : int
            Number of top predictions to include.

        Returns
        -------
        dict
            The complete structured diagnosis result, formatted
            for frontend consumption.
        """
        start_time = time.time()
        self._lazy_init_modules()

        result = {
            "plant": "Unknown",
            "disease": "Unknown",
            "disease_description": "",
            "confidence": 0.0,
            "confidence_info": {},
            "status": "Unknown",
            "severity": {
                "percentage": 0.0,
                "level": "Unknown",
            },
            "risk": {},
            "explanation": {},
            "treatment": {},
            "top_predictions": [],
            "similar_cases": [],
            "warnings": [],
            "heatmap_path": "",
            "diagnosis_time_ms": 0,
            "final_source": "CNN Model",
            "clip_predictions": [],
            "ensemble_meta": {},   # NEW: populated when ensemble is used
        }

        # ==============================================================
        # STAGE 1: Image Quality Check
        # ==============================================================
        logger.info("Stage 1/13: Image Quality Check")
        quality = self.quality_checker.check(image_path)
        result["warnings"] = quality.get("warnings", [])

        if not quality["passed"]:
            logger.warning(f"Image quality issues: {quality['warnings']}")

        # ==============================================================
        # STAGE 2: Core Model Inference
        # ==============================================================
        # When ensemble_engine is available, use the ensemble predictor.
        # Otherwise fall back to the original single-model DiseaseEngine.
        # Grad-CAM (Stage 7) is ALWAYS driven by EfficientNet-B0 only.
        # ==============================================================
        if self._ensemble_predictor is not None:
            logger.info("Stage 2/13: Ensemble Inference (EfficientNet-B0 + ResNet-50 + EfficientNet-B1)")
            prediction = self._ensemble_predictor.predict(image_path, top_k=top_k)
            # Surface ensemble metadata in final result
            result["ensemble_meta"] = prediction.get("ensemble_meta", {})
            if prediction["ensemble_meta"].get("used_ensemble"):
                result["final_source"] = "Ensemble (B0 + R50 + B1)"
        else:
            logger.info("Stage 2/13: Core Model Inference (EfficientNet-B0 single model)")
            prediction = self.disease_engine.predict(image_path, top_k=top_k)

        if not prediction.get("success"):
            result["warnings"].append(
                f"Model prediction failed: {prediction.get('error', 'Unknown error')}"
            )
            result["diagnosis_time_ms"] = round(
                (time.time() - start_time) * 1000, 1
            )
            return result

        raw_label = prediction["disease_name"]
        top_preds = prediction.get("top_predictions", [])

        # ==============================================================
        # STAGE 3: Confidence Calibration
        # ==============================================================
        logger.info("Stage 3/13: Confidence Calibration")
        calibrated_preds = self.calibrator.calibrate(top_preds)
        calibrated_confidence = calibrated_preds[0][1] if calibrated_preds else 0.0

        # ==============================================================
        # STAGE 4: Label Parsing (Plant + Disease)
        # ==============================================================
        logger.info("Stage 4/13: Label Parsing")
        parsed = self.label_parser.parse(raw_label)
        result["plant"] = parsed["plant"]
        result["disease"] = parsed["disease"]
        result["confidence"] = calibrated_confidence

        # ==============================================================
        # STAGE 4.5: PlantNet Identification
        # ==============================================================
        if self._plantnet is not None:
            logger.info("Stage 4.5/13: PlantNet Identification")
            pn_res = self._plantnet.identify_plant(image_path)
            
            if pn_res.get("plant_name") and pn_res.get("plant_name") not in ("Unknown", "Error"):
                pn_conf = pn_res.get("confidence", 0.0)
                
                # Only override if PlantNet is confident enough (> 50%)
                if pn_conf > 50.0 and pn_res["plant_name"] != "Unknown":
                    result["plant"] = pn_res["plant_name"]
                    logger.info(f"PlantNet identified plant: {result['plant']} ({pn_conf}%) - Overriding CNN")
                else:
                    logger.info(f"PlantNet confidence ({pn_conf}%) too low. Falling back to CNN plant label: {result['plant']}")
                
                # Keep the response in info regardless of confidence, for reference
                result["plantnet_info"] = pn_res
            elif pn_res.get("error"):
                logger.warning(f"PlantNet error: {pn_res['error']}")

        # ==============================================================
        # STAGE 5: Open-World Detection
        # ==============================================================
        logger.info("Stage 5/13: Open-World Detection")
        ow_result = self.open_world.detect(calibrated_preds)
        result["status"] = ow_result["status"]

        if ow_result["status"] == "Unknown":
            result["disease"] = "Unknown Disease"
            result["warnings"].append(ow_result["reason"])

        if ow_result.get("is_ambiguous"):
            result["warnings"].append(
                "Prediction is ambiguous -- top candidates are very close. "
                "Consider manual verification."
            )

        # ==============================================================
        # STAGE 5.5: CLIP Fallback (Open-World)
        # ==============================================================
        if result["status"] == "Unknown" and self._clip_model is not None:
            logger.info("Stage 5.5/13: CLIP Open-World Fallback")
            try:
                clip_results = self._clip_model.predict(image_path)
                # Normalize confidence to percentage and limit to top 3
                formatted_clip = []
                for pred in clip_results[:3]:
                    conf_val = pred.get("confidence", 0.0)
                    # Convert 0-1 range to percentage if needed
                    if conf_val <= 1.0:
                        conf_val = round(conf_val * 100, 1)
                    formatted_clip.append({
                        "label": pred.get("label", "Unknown"),
                        "confidence": conf_val,
                    })
                result["clip_predictions"] = formatted_clip
                result["final_source"] = "CLIP (Open-world)"
                logger.info(
                    f"CLIP fallback: {len(formatted_clip)} predictions, "
                    f"top='{formatted_clip[0]['label']}' ({formatted_clip[0]['confidence']}%)"
                    if formatted_clip else "CLIP returned no results"
                )
            except Exception as e:
                logger.warning(f"CLIP prediction failed: {e}")
                result["clip_predictions"] = []
        else:
            result["final_source"] = "CNN Model"

        # ==============================================================
        # STAGE 6: Multi-Label Top-K Output
        # ==============================================================
        logger.info("Stage 6/13: Multi-Label Top-K Output")
        result["top_predictions"] = []
        
        # Determine if we should universally override the plant name in the list
        pn_overrode = ("plantnet_info" in result) and (result["plantnet_info"].get("confidence", 0.0) > 50.0)
        
        for name, conf in calibrated_preds:
            parsed_pred = self.label_parser.parse(name)
            desc = self.display_formatter.get_disease_description(
                parsed_pred["disease"]
            )
            # Use the global PlantNet override if available and > 50%, else use CNN's parsed prediction
            display_plant = result["plant"] if pn_overrode else parsed_pred["plant"]
            result["top_predictions"].append({
                "name": f"{display_plant} - {parsed_pred['disease']}",
                "raw_label": name,
                "confidence": round(conf, 1),
                "description": desc,
            })

        # ==============================================================
        # STAGE 7: Grad-CAM Heatmap
        # ==============================================================
        heatmap = None
        is_healthy = parsed.get("is_healthy", False)

        # Decide whether to generate Grad-CAM:
        #   • Always run for diseased predictions
        #   • Run even for "healthy" predictions when model confidence < 90%
        #     (borderline / ambiguous cases like subtle disease on grape leaf)
        run_gradcam = (
            self._gradcam is not None
            and (
                not is_healthy
                or calibrated_confidence < 90.0   # low-confidence healthy → still show
            )
        )

        # For borderline healthy predictions: target the 2nd-best non-healthy class
        # so the user sees what region triggered the disease suspicion
        gradcam_class_idx = None
        try:
            if is_healthy and calibrated_confidence < 90.0:
                # Find best non-healthy class from top predictions
                for pred_name, _ in calibrated_preds[1:]:
                    if "healthy" not in pred_name.lower():
                        gradcam_class_idx = self.disease_engine.class_names.index(pred_name)
                        logger.info(
                            f"Stage 7/13: Borderline healthy ({calibrated_confidence:.1f}%) "
                            f"— running Grad-CAM on 2nd class: {pred_name}"
                        )
                        break
                if gradcam_class_idx is None:
                    # All top predictions are healthy — truly healthy
                    run_gradcam = False
            else:
                gradcam_class_idx = self.disease_engine.class_names.index(raw_label)
        except (ValueError, IndexError):
            gradcam_class_idx = None   # generate() will auto-select predicted class

        if run_gradcam:
            logger.info("Stage 7/13: Grad-CAM Heatmap Generation")
            try:
                import torch
                from PIL import Image

                img = Image.open(image_path).convert("RGB")
                img_tensor = self.disease_engine.transform(img).unsqueeze(0)

                heatmap = self._gradcam.generate(
                    img_tensor, class_idx=gradcam_class_idx
                )

                if heatmap is not None:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    overlay_name = f"gradcam_{timestamp}.jpg"
                    overlay_path = os.path.join(self.output_dir, overlay_name)
                    saved = self._gradcam.create_overlay(
                        image_path, heatmap, overlay_path
                    )
                    result["heatmap_path"] = saved

            except Exception as e:
                logger.warning(f"Grad-CAM generation failed: {e}")
                result["warnings"].append(
                    "Grad-CAM heatmap generation failed -- skipping."
                )
        else:
            logger.info("Stage 7/13: Skipping Grad-CAM -- plant is healthy (high confidence)")

        # ==============================================================
        # STAGE 8: Severity Estimation
        # ==============================================================
        severity_pct = 0.0
        if heatmap is not None:
            logger.info("Stage 8/13: Severity Estimation")
            severity = self.severity_estimator.estimate(heatmap)
            severity_pct = severity["percentage"]
            result["severity"] = {
                "percentage": severity["percentage"],
                "level": severity["level"],
            }
        elif parsed.get("is_healthy", False):
            result["severity"] = {
                "percentage": 0.0,
                "level": "None (Healthy)",
            }

        # ==============================================================
        # STAGE 9: Risk Assessment
        # ==============================================================
        logger.info("Stage 9/13: Risk Assessment")
        risk = self.risk_assessor.assess(
            severity_percentage=severity_pct,
            is_healthy=parsed.get("is_healthy", False),
        )
        result["risk"] = risk
        # Embed risk level into severity for backwards compatibility
        result["severity"]["risk"] = risk["level"]

        # ==============================================================
        # STAGE 10: Explanation Engine
        # ==============================================================
        logger.info("Stage 10/13: Explanation Engine")
        explanation = self.explanation_engine.explain(
            disease_name=parsed["disease"],
            plant_name=parsed["plant"],
        )
        result["explanation"] = explanation

        # ==============================================================
        # STAGE 11: Treatment Recommendations
        # ==============================================================
        logger.info("Stage 11/13: Treatment Recommendations")
        treatment = self.treatment_engine.recommend(
            disease_name=parsed["disease"],
            disease_type=explanation.get("type", "unknown"),
        )
        result["treatment"] = treatment

        # ==============================================================
        # STAGE 12: Similarity Search (FAISS)
        # ==============================================================
        if (
            self._feature_extractor is not None
            and self._similarity_search is not None
            and self._similarity_search._loaded
        ):
            logger.info("Stage 12/13: Similarity Search")
            try:
                from PIL import Image

                img = Image.open(image_path).convert("RGB")
                img_tensor = self.disease_engine.transform(img).unsqueeze(0)
                query_vec = self._feature_extractor.extract(img_tensor)
                similar_raw = self._similarity_search.search(query_vec, top_k=3)

                # Clean similarity labels for readability
                similar_clean = []
                for case in similar_raw:
                    parsed_label = self.label_parser.parse(case.get("label", ""))
                    similar_clean.append({
                        "image": case.get("image", ""),
                        "label": f"{parsed_label['plant']} - {parsed_label['disease']}",
                        "raw_label": case.get("label", ""),
                        "score": case.get("score", 0.0),
                    })
                result["similar_cases"] = similar_clean
            except Exception as e:
                logger.warning(f"Similarity search failed: {e}")
        else:
            logger.info("Stage 12/13: Similarity search skipped (index not available)")

        # ==============================================================
        # FINALIZE: Display Formatting
        # ==============================================================
        elapsed_ms = round((time.time() - start_time) * 1000, 1)
        result["diagnosis_time_ms"] = elapsed_ms

        # Add disease description
        result["disease_description"] = self.display_formatter.get_disease_description(
            parsed["disease"]
        )

        # Add confidence info
        from .display_formatter import confidence_descriptor
        result["confidence_info"] = confidence_descriptor(calibrated_confidence)

        # ==============================================================
        # STAGE 13: Final Output Enhancement (user-centric polish)
        # ==============================================================
        logger.info("Stage 13/13: Final Output Enhancement")
        result = self.output_enhancer.enhance(result)

        logger.info(
            f"Diagnosis complete: {result['plant']} - {result['disease']} "
            f"({result['confidence']:.1f}%) "
            f"Risk={result['risk'].get('level', '?')} "
            f"in {elapsed_ms}ms"
        )

        return result

    # ==============================================================
    # CLEANUP
    # ==============================================================

    def cleanup(self):
        """Release hooks and resources."""
        if self._gradcam is not None:
            self._gradcam.remove_hooks()
        if self._feature_extractor is not None:
            self._feature_extractor.remove_hook()
        logger.info("Plant Doctor pipeline resources released")
