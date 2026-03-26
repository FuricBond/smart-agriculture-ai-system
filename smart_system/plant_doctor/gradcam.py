"""
Grad-CAM Generator — Disease Localization Module
====================================================
Generates Gradient-weighted Class Activation Maps to visualize
which regions of the leaf image the model focuses on.

Works non-invasively with the existing EfficientNet/ResNet model
by hooking into the last convolutional layer.

Features
--------
  • Auto-detects the final conv layer for EfficientNet-B0 and ResNet50
  • Generates heatmap overlay on the original image
  • Returns the raw activation mask for downstream severity analysis
  • Saves the overlay as a JPEG file

Author  : Smart Agriculture AI Team
Version : 1.0.0
"""

from __future__ import annotations

import os
import logging
from typing import Dict, Optional, Tuple

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

logger = logging.getLogger("plant_doctor.gradcam")


class GradCAMGenerator:
    """
    Produces Grad-CAM heatmaps from an existing trained model.

    This class hooks into the last convolutional layer of the model
    to extract feature gradients, then computes a class-discriminative
    localization map.

    Parameters
    ----------
    model : torch.nn.Module
        The loaded PyTorch model (EfficientNet or ResNet).
    architecture : str
        Architecture identifier ('EfficientNet-B0' or 'ResNet50 ...').
    device : torch.device
        Computation device.
    """

    def __init__(
        self,
        model: torch.nn.Module,
        architecture: str,
        device: torch.device,
    ) -> None:
        self.model = model
        self.architecture = architecture
        self.device = device

        # Storage for hooked activations & gradients
        self._activations: Optional[torch.Tensor] = None
        self._gradients: Optional[torch.Tensor] = None

        # Register hooks on the target layer
        self._target_layer = self._find_target_layer()
        self._forward_hook = self._target_layer.register_forward_hook(
            self._hook_activations
        )
        self._backward_hook = self._target_layer.register_full_backward_hook(
            self._hook_gradients
        )

    # ── Auto-detect the last convolutional layer ──────────────

    def _find_target_layer(self) -> torch.nn.Module:
        """
        Return the last convolutional block appropriate for the
        model architecture.
        """
        if "efficientnet" in self.architecture.lower():
            # EfficientNet-B0: features[-1] is the last MBConv block
            return self.model.features[-1]
        elif "resnet" in self.architecture.lower():
            # ResNet50: layer4 is the last residual block
            return self.model.layer4[-1]
        else:
            # Fallback: walk the model and find the last Conv2d
            last_conv = None
            for module in self.model.modules():
                if isinstance(module, torch.nn.Conv2d):
                    last_conv = module
            if last_conv is None:
                raise RuntimeError(
                    "Cannot auto-detect target layer for Grad-CAM. "
                    f"Unsupported architecture: {self.architecture}"
                )
            logger.warning(
                f"Using fallback conv layer for Grad-CAM (arch={self.architecture})"
            )
            return last_conv

    # ── Hook callbacks ────────────────────────────────────────

    def _hook_activations(self, module, input, output):
        self._activations = output.detach()

    def _hook_gradients(self, module, grad_input, grad_output):
        self._gradients = grad_output[0].detach()

    # ── Core Grad-CAM computation ─────────────────────────────

    def generate(
        self,
        image_tensor: torch.Tensor,
        class_idx: Optional[int] = None,
    ) -> np.ndarray:
        """
        Compute the Grad-CAM heatmap for a given input tensor.

        Parameters
        ----------
        image_tensor : torch.Tensor
            Preprocessed image tensor (1, C, H, W).
        class_idx : int or None
            Target class index. If None, uses the predicted class.

        Returns
        -------
        np.ndarray
            Normalized heatmap (H, W) with values in [0, 1].
        """
        # Enable grad computation temporarily
        self.model.eval()
        image_tensor = image_tensor.to(self.device).requires_grad_(True)

        # Forward pass
        output = self.model(image_tensor)

        if class_idx is None:
            class_idx = output.argmax(dim=1).item()

        # Zero all existing gradients
        self.model.zero_grad()

        # Backward pass for the target class
        target_score = output[0, class_idx]
        target_score.backward(retain_graph=False)

        # Compute Grad-CAM weights
        gradients = self._gradients  # (1, C, h, w)
        activations = self._activations  # (1, C, h, w)

        if gradients is None or activations is None:
            logger.error("Grad-CAM hooks failed to capture activations/gradients")
            return np.zeros((224, 224), dtype=np.float32)

        # Global average pooling of gradients → channel weights
        weights = gradients.mean(dim=(2, 3), keepdim=True)  # (1, C, 1, 1)

        # Weighted combination of forward activation maps
        cam = (weights * activations).sum(dim=1, keepdim=True)  # (1, 1, h, w)
        cam = F.relu(cam)  # Only positive contributions

        # Resize to input image dimensions
        cam = F.interpolate(
            cam,
            size=(224, 224),
            mode="bilinear",
            align_corners=False,
        )

        # Normalize to [0, 1]
        cam = cam.squeeze().cpu().numpy()
        cam_min, cam_max = cam.min(), cam.max()
        if cam_max - cam_min > 1e-8:
            cam = (cam - cam_min) / (cam_max - cam_min)
        else:
            cam = np.zeros_like(cam)

        return cam.astype(np.float32)

    # ── Heatmap overlay on original image ─────────────────────

    def create_overlay(
        self,
        image_path: str,
        heatmap: np.ndarray,
        output_path: str,
        alpha: float = 0.5,
    ) -> str:
        """
        Overlay the Grad-CAM heatmap on the original image and save.

        Parameters
        ----------
        image_path : str
            Path to the original leaf image.
        heatmap : np.ndarray
            Normalized heatmap array (H, W) in [0, 1].
        output_path : str
            Where to save the overlay JPEG.
        alpha : float
            Blending weight (0 = only image, 1 = only heatmap).

        Returns
        -------
        str
            Path to the saved overlay image.
        """
        # Load original image
        original = cv2.imread(image_path)
        if original is None:
            logger.error(f"Cannot read image for overlay: {image_path}")
            return ""

        h, w = original.shape[:2]

        # Resize heatmap to match original
        heatmap_resized = cv2.resize(heatmap, (w, h))

        # Convert to colormap (JET)
        heatmap_colored = cv2.applyColorMap(
            (heatmap_resized * 255).astype(np.uint8),
            cv2.COLORMAP_JET,
        )

        # Blend
        overlay = cv2.addWeighted(original, 1 - alpha, heatmap_colored, alpha, 0)

        # Save
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        cv2.imwrite(output_path, overlay)
        logger.info(f"Grad-CAM overlay saved: {output_path}")

        return output_path

    # ── Cleanup ───────────────────────────────────────────────

    def remove_hooks(self):
        """Remove registered hooks to prevent memory leaks."""
        if self._forward_hook is not None:
            self._forward_hook.remove()
        if self._backward_hook is not None:
            self._backward_hook.remove()
        self._forward_hook = None
        self._backward_hook = None
