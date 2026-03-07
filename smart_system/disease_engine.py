"""
Disease Detection Engine — Smart Agriculture System v2.0
===========================================================
Loads the trained ResNet50 CNN model and predicts plant disease
from leaf images. Handles both new (Dropout+FC) and legacy
(simple FC) model architectures automatically.

Features
--------
    • Dual architecture support (new Dropout+FC / legacy FC)
    • ImageNet normalization for accurate inference
    • Top-K predictions with confidence scores
    • Confidence level classification
    • Image format validation
    • Corrupted model detection
    • Professional error handling and logging

Author  : Smart Agriculture AI Team
Version : 2.0.0
"""

from __future__ import annotations

import os
import json
import time
from typing import Dict, List, Optional, Tuple

from . import config
from . import logger


class DiseaseEngine:
    """
    Plant Disease Detection Engine.

    Wraps the trained ResNet50 CNN and provides prediction
    capabilities with top-K results and confidence scoring.

    Attributes
    ----------
    model : torch.nn.Module or None
        The loaded PyTorch model.
    class_names : list[str]
        Ordered list of disease class names.
    num_classes : int
        Number of disease classes.
    device : torch.device
        Computation device (CPU or CUDA).
    _loaded : bool
        Whether the model has been loaded successfully.
    """

    def __init__(self) -> None:
        self.model = None
        self.class_names: List[str] = []
        self.num_classes: int = 0
        self.device = None
        self.transform = None
        self._loaded: bool = False
        self._architecture: str = 'unknown'

    def load(self) -> bool:
        """
        Load the disease detection model and class names.

        Attempts to load the new architecture (Dropout+FC head)
        first, then falls back to legacy (single Linear).

        Returns
        -------
        bool
            True if model loaded successfully.
        """
        try:
            import torch
            import torch.nn as nn
            from torchvision import transforms, models
        except ImportError as e:
            logger.log_error("DISEASE",
                             f"Missing dependency: {e}. "
                             f"Install: pip install torch torchvision")
            return False

        load_start = time.time()

        try:
            self.device = torch.device(
                "cuda" if torch.cuda.is_available() else "cpu")

            # ── Load Class Names ──────────────────────────────
            if os.path.isfile(config.DISEASE_CLASS_MAP):
                with open(config.DISEASE_CLASS_MAP, 'r') as f:
                    class_data = json.load(f)
                self.class_names = class_data.get(
                    'class_names', class_data.get('classes', []))
            elif os.path.isdir(config.DISEASE_DATA_DIR):
                self.class_names = sorted([
                    d for d in os.listdir(config.DISEASE_DATA_DIR)
                    if os.path.isdir(
                        os.path.join(config.DISEASE_DATA_DIR, d))
                ])
            else:
                logger.log_error(
                    "DISEASE",
                    "Cannot find class names JSON or dataset directory")
                return False

            self.num_classes = len(self.class_names)

            if self.num_classes == 0:
                logger.log_error("DISEASE", "No disease classes found")
                return False

            # ── Validate model file ───────────────────────────
            if not os.path.isfile(config.DISEASE_MODEL_PATH):
                logger.log_error(
                    "DISEASE",
                    f"Model file not found: {config.DISEASE_MODEL_PATH}")
                return False

            file_size = os.path.getsize(config.DISEASE_MODEL_PATH)
            if file_size < 1024:  # < 1 KB is definitely corrupted
                logger.log_error(
                    "DISEASE",
                    f"Model file appears corrupted ({file_size} bytes)")
                return False

            # ── D4: Try EfficientNet-B0 first ─────────────────
            state_dict = torch.load(
                config.DISEASE_MODEL_PATH,
                map_location=self.device,
                weights_only=True)

            try:
                model = models.efficientnet_b0(weights=None)
                num_features = model.classifier[1].in_features
                model.classifier = nn.Sequential(
                    nn.Dropout(0.3),
                    nn.Linear(num_features, self.num_classes)
                )
                model.load_state_dict(state_dict)
                self._architecture = 'EfficientNet-B0'

            except (RuntimeError, Exception):
                # ── Fallback: ResNet50 (Dropout+FC head) ──────
                try:
                    model = models.resnet50(weights=None)
                    num_features = model.fc.in_features
                    model.fc = nn.Sequential(
                        nn.Dropout(0.3),
                        nn.Linear(num_features, 512),
                        nn.ReLU(),
                        nn.Dropout(0.2),
                        nn.Linear(512, self.num_classes)
                    )
                    model.load_state_dict(state_dict)
                    self._architecture = 'ResNet50 (Dropout+FC)'
                except (RuntimeError, Exception):
                    # ── Fallback: ResNet50 legacy (single FC) ─
                    try:
                        model = models.resnet50(weights=None)
                        model.fc = nn.Linear(
                            model.fc.in_features, self.num_classes)
                        model.load_state_dict(state_dict)
                        self._architecture = 'ResNet50 (legacy)'
                    except Exception as e:
                        logger.log_error(
                            "DISEASE",
                            f"Model is corrupted or incompatible: {e}")
                        return False

            self.model = model.to(self.device)
            self.model.eval()

            # ── Image Transform (standard ImageNet validation) ──
            self.transform = transforms.Compose([
                transforms.Resize(256),              # Preserve aspect ratio
                transforms.CenterCrop(config.IMAGE_SIZE),  # Standard 224×224 crop
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=config.IMAGENET_MEAN,
                    std=config.IMAGENET_STD),
            ])

            self._loaded = True
            elapsed = time.time() - load_start
            logger.log_model_load("DISEASE", True, elapsed)
            logger.log_info(
                "DISEASE",
                f"Loaded: {self.num_classes} classes, "
                f"arch={self._architecture}, device={self.device}")
            return True

        except Exception as e:
            logger.log_error(
                "DISEASE", f"Failed to load model: {str(e)}")
            return False

    def predict(
        self, image_path: str, top_k: int = 5
    ) -> Dict:
        """
        Predict disease from a leaf image.

        Parameters
        ----------
        image_path : str
            Path to the leaf image file.
        top_k : int
            Number of top predictions to return.

        Returns
        -------
        dict
            success          : bool
            disease_name     : str  (full class name)
            plant            : str  (extracted plant name)
            condition        : str  (extracted disease name)
            confidence       : float (percentage 0–100)
            confidence_level : str  (HIGH/MODERATE/LOW)
            top_predictions  : list[(name, confidence)]
            image_path       : str
            error            : str  (only if success is False)
        """
        if not self._loaded:
            return {
                'success': False,
                'error': 'Disease model not loaded. Call load() first.'
            }

        # ── Validate image path ───────────────────────────────
        if not os.path.isfile(image_path):
            return {
                'success': False,
                'error': f'Image file not found: {image_path}'
            }

        ext = os.path.splitext(image_path)[1].lower()
        if ext not in config.VALID_IMAGE_EXTENSIONS:
            logger.log_warning(
                "DISEASE",
                f"Non-standard image extension: {ext}")

        try:
            import torch
            from PIL import Image

            # ── Load and transform image (D5: Test-Time Augmentation) ──
            img = Image.open(image_path).convert('RGB')
            
            # 1. Original image
            img_tensor = self.transform(img).unsqueeze(0).to(self.device)
            
            # 2. Horizontally flipped image
            import torchvision.transforms.functional as TF
            img_flipped = TF.hflip(img)
            img_flipped_tensor = self.transform(img_flipped).unsqueeze(0).to(self.device)

            # ── Run inference ─────────────────────────────────
            with torch.no_grad():
                out1 = self.model(img_tensor)
                out2 = self.model(img_flipped_tensor)
                
                # Average probabilities from both augmented views
                prob1 = torch.softmax(out1, dim=1)[0]
                prob2 = torch.softmax(out2, dim=1)[0]
                probabilities = (prob1 + prob2) / 2.0
                
                top_probs, top_indices = torch.topk(
                    probabilities, min(top_k, self.num_classes))

            # ── Extract results ───────────────────────────────
            top_class = self.class_names[top_indices[0].item()]
            top_confidence = top_probs[0].item() * 100

            # Parse disease name (format: Plant___Condition)
            parts = top_class.split('___')
            plant = (parts[0].replace('_', ' ')
                     if len(parts) > 0 else 'Unknown')
            condition = (parts[1].replace('_', ' ')
                         if len(parts) > 1
                         else top_class.replace('_', ' '))

            # Classify confidence level
            if top_confidence >= config.CONFIDENCE_HIGH:
                confidence_level = 'HIGH'
            elif top_confidence >= config.CONFIDENCE_MODERATE:
                confidence_level = 'MODERATE'
            else:
                confidence_level = 'LOW'

            # Build top predictions list
            top_predictions: List[Tuple[str, float]] = []
            for prob, idx in zip(top_probs, top_indices):
                name = self.class_names[idx.item()]
                conf = prob.item() * 100
                top_predictions.append((name, conf))

            result = {
                'success':          True,
                'disease_name':     top_class,
                'plant':            plant,
                'condition':        condition,
                'confidence':       top_confidence,
                'confidence_level': confidence_level,
                'top_predictions':  top_predictions,
                'image_path':       image_path,
            }

            logger.log_info(
                "DISEASE",
                f"Predicted: {top_class} ({top_confidence:.1f}%, "
                f"{confidence_level})")
            return result

        except Exception as e:
            error_msg = f"Prediction failed: {str(e)}"
            logger.log_error("DISEASE", error_msg)
            return {'success': False, 'error': error_msg}
