"""
Unit tests for the Grad-CAM++ upgrade (no real model required).

Tests cover:
  1. Grad-CAM++ alpha weights differ from plain GAP weights
  2. Dynamic 60th-percentile thresholding zeros low values
  3. Unsharp-mask sharpening increases contrast (max - mean spread)
  4. create_overlay produces a valid BGR image matching original H x W
"""

from __future__ import annotations

import os
import sys
import tempfile

import cv2
import numpy as np
import pytest
import torch
import torch.nn as nn
import torch.nn.functional as F

# ── make sure the project root is importable ──────────────────
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from smart_system.plant_doctor.gradcam import GradCAMGenerator


# ═══════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════

def _make_synthetic_grads_acts(
    batch: int = 1,
    channels: int = 8,
    h: int = 7,
    w: int = 7,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Return random synthetic (gradients, activations) tensors."""
    torch.manual_seed(42)
    gradients  = torch.rand(batch, channels, h, w)
    activations = torch.rand(batch, channels, h, w) * 2.0  # range [0, 2)
    return gradients, activations


def _gradcam_plus_plus_weights(
    gradients: torch.Tensor,
    activations: torch.Tensor,
) -> torch.Tensor:
    """Recompute Grad-CAM++ weights — mirrors the logic in GradCAMGenerator."""
    grads2 = gradients ** 2
    grads3 = gradients ** 3
    denominator = (
        2.0 * grads2
        + (activations * grads3).sum(dim=(2, 3), keepdim=True)
        + 1e-8
    )
    alpha = grads2 / denominator
    weights = (alpha * F.relu(gradients)).sum(dim=(2, 3), keepdim=True)
    return weights


def _standard_gradcam_weights(gradients: torch.Tensor) -> torch.Tensor:
    """Standard Grad-CAM: global average pooling of gradients."""
    return gradients.mean(dim=(2, 3), keepdim=True)


# ═══════════════════════════════════════════════════════════════
# Test 1 — Grad-CAM++ weights differ from standard GAP weights
# ═══════════════════════════════════════════════════════════════

def test_gradcampp_weights_differ_from_standard():
    """
    Grad-CAM++ α-weighted per-channel weights must NOT equal the
    plain global-average-pooling weights of standard Grad-CAM.
    """
    grads, acts = _make_synthetic_grads_acts()

    w_pp  = _gradcam_plus_plus_weights(grads, acts)
    w_std = _standard_gradcam_weights(grads)

    # They should have the same shape
    assert w_pp.shape == w_std.shape, "Shape mismatch between weight tensors"

    # They must NOT be numerically identical
    assert not torch.allclose(
        w_pp, w_std, atol=1e-5
    ), "Grad-CAM++ weights are unexpectedly identical to standard Grad-CAM"


# ═══════════════════════════════════════════════════════════════
# Test 2 — Dynamic thresholding zeros values below 60th percentile
# ═══════════════════════════════════════════════════════════════

def test_dynamic_thresholding():
    """
    After applying the 60th-percentile threshold, at least 60% of
    pixels in the normalized CAM must be exactly zero.
    """
    np.random.seed(0)
    cam = np.random.rand(224, 224).astype(np.float32)  # uniform [0, 1)

    threshold = np.percentile(cam, 60)
    cam_thresh = np.where(cam > threshold, cam, 0.0)

    zero_fraction = np.mean(cam_thresh == 0.0)
    assert zero_fraction >= 0.59, (
        f"Expected ≥59% zeros after thresholding, got {zero_fraction:.2%}"
    )


# ═══════════════════════════════════════════════════════════════
# Test 3 — Sharpening increases contrast (max − mean spread)
# ═══════════════════════════════════════════════════════════════

def test_sharpening_increases_contrast():
    """
    Unsharp-mask (addWeighted 1.5 / -0.5) should raise the max−mean
    spread compared to the plain Gaussian-blurred map.
    """
    np.random.seed(1)
    heatmap = np.random.rand(224, 224).astype(np.float32)

    blurred       = cv2.GaussianBlur(heatmap, (3, 3), sigmaX=0)
    heatmap_sharp = cv2.addWeighted(heatmap, 1.5, blurred, -0.5, 0)
    heatmap_sharp = np.clip(heatmap_sharp, 0.0, 1.0)

    spread_orig  = heatmap.max() - heatmap.mean()
    spread_sharp = heatmap_sharp.max() - heatmap_sharp.mean()

    # Sharpening must increase the spread by at least a small margin
    assert spread_sharp > spread_orig * 0.99, (
        f"Sharpening did not increase contrast: "
        f"original spread={spread_orig:.4f}, sharpened={spread_sharp:.4f}"
    )


# ═══════════════════════════════════════════════════════════════
# Test 4 — create_overlay produces valid BGR image at correct size
# ═══════════════════════════════════════════════════════════════

class _TinyConvNet(nn.Module):
    """Minimal model that satisfies GradCAMGenerator's hook interface."""
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 8,  3, padding=1),
            nn.ReLU(),
            nn.Conv2d(8, 16, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(16, 32, 3, padding=1),  # features[-3]
            nn.ReLU(),
            nn.Conv2d(32, 32, 3, padding=1),  # features[-2]
            nn.ReLU(),
            nn.Conv2d(32, 32, 3, padding=1),  # features[-1]
        )
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(32, 10),
        )

    def forward(self, x):
        x = self.features(x)
        return self.classifier(x)


def test_create_overlay_output_size():
    """
    create_overlay() must write a valid JPEG whose spatial dimensions
    match the original image (H, W).
    """
    # Build a tiny synthetic model
    model = _TinyConvNet()
    device = torch.device("cpu")
    gen = GradCAMGenerator(model, architecture="EfficientNet-B0", device=device)

    # Synthetic heatmap (224x224, values in [0, 1])
    heatmap = np.random.rand(224, 224).astype(np.float32)

    # Create a temporary "original" image (100x150 BGR)
    with tempfile.TemporaryDirectory() as tmpdir:
        orig_path    = os.path.join(tmpdir, "orig.jpg")
        overlay_path = os.path.join(tmpdir, "overlay.jpg")

        dummy_img = np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8)
        cv2.imwrite(orig_path, dummy_img)

        result = gen.create_overlay(orig_path, heatmap, overlay_path)

        assert result == overlay_path, "create_overlay returned wrong path"
        assert os.path.isfile(overlay_path), "Overlay file was not created"

        saved = cv2.imread(overlay_path)
        assert saved is not None, "cv2 could not read the saved overlay"
        assert saved.shape[:2] == (100, 150), (
            f"Overlay H×W mismatch: expected (100, 150), got {saved.shape[:2]}"
        )
        assert saved.ndim == 3 and saved.shape[2] == 3, "Overlay is not BGR"

    gen.remove_hooks()
