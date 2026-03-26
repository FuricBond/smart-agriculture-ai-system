"""
Disease Similarity Search — FAISS-based Feature Matching
==========================================================
Extracts feature vectors from the model's penultimate layer
and uses FAISS to find visually similar disease cases.

Workflow
--------
  1. Build an index from known disease images (offline)
  2. At inference time, extract the query feature vector
  3. Search the FAISS index for the top-N nearest neighbors
  4. Return similar cases with labels and distances

Author  : Smart Agriculture AI Team
Version : 1.0.0
"""

from __future__ import annotations

import os
import json
import logging
import pickle
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
from PIL import Image

logger = logging.getLogger("plant_doctor.similarity")


# ═══════════════════════════════════════════════════════════════
# INDEX FILE PATHS
# ═══════════════════════════════════════════════════════════════

DEFAULT_INDEX_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "disease_model", "models", "faiss_index"
)


class FeatureExtractor:
    """
    Extracts feature vectors from the model's penultimate layer.

    Works by hooking into the layer just before the classifier head
    to capture the high-dimensional representation.
    """

    def __init__(
        self,
        model: nn.Module,
        architecture: str,
        device: torch.device,
    ) -> None:
        self.model = model
        self.architecture = architecture
        self.device = device
        self._features: Optional[torch.Tensor] = None
        self._hook = self._register_hook()

    def _register_hook(self):
        """Hook into the feature layer before the classifier."""
        if "efficientnet" in self.architecture.lower():
            # EfficientNet: avgpool output
            target = self.model.avgpool
        elif "resnet" in self.architecture.lower():
            target = self.model.avgpool
        else:
            # Fallback: use the last adaptive avg pool we can find
            target = None
            for module in self.model.modules():
                if isinstance(module, nn.AdaptiveAvgPool2d):
                    target = module
            if target is None:
                logger.warning("Cannot find feature extraction layer")
                return None

        return target.register_forward_hook(self._hook_fn)

    def _hook_fn(self, module, input, output):
        self._features = output.detach()

    def extract(self, image_tensor: torch.Tensor) -> np.ndarray:
        """
        Extract a feature vector from a preprocessed image tensor.

        Returns
        -------
        np.ndarray
            1-D feature vector (e.g., 1280 for EfficientNet-B0).
        """
        self.model.eval()
        with torch.no_grad():
            _ = self.model(image_tensor.to(self.device))

        if self._features is None:
            logger.error("Feature extraction hook did not fire")
            return np.zeros(1280, dtype=np.float32)

        # Flatten: (1, C, 1, 1) → (C,)
        feat = self._features.squeeze().cpu().numpy()

        # L2 normalize for cosine similarity
        norm = np.linalg.norm(feat)
        if norm > 1e-8:
            feat = feat / norm

        return feat.astype(np.float32)

    def remove_hook(self):
        if self._hook is not None:
            self._hook.remove()
            self._hook = None


class DiseaseSimilaritySearch:
    """
    FAISS-based similarity search for plant disease images.

    Parameters
    ----------
    index_dir : str
        Directory containing the FAISS index and metadata files.
    """

    def __init__(self, index_dir: str = DEFAULT_INDEX_DIR) -> None:
        self.index_dir = os.path.abspath(index_dir)
        self.index = None
        self.metadata: List[Dict] = []
        self._loaded = False

    def load_index(self) -> bool:
        """Load the pre-built FAISS index and metadata."""
        try:
            import faiss
        except ImportError:
            logger.warning(
                "FAISS not installed. Similarity search disabled. "
                "Install: pip install faiss-cpu"
            )
            return False

        index_path = os.path.join(self.index_dir, "disease_features.index")
        meta_path = os.path.join(self.index_dir, "disease_metadata.json")

        if not os.path.isfile(index_path):
            logger.info(
                f"FAISS index not found at {index_path}. "
                f"Run build_index() to create it."
            )
            return False

        try:
            self.index = faiss.read_index(index_path)
            with open(meta_path, "r") as f:
                self.metadata = json.load(f)
            self._loaded = True
            logger.info(
                f"Loaded FAISS index: {self.index.ntotal} vectors, "
                f"{len(self.metadata)} metadata entries"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {e}")
            return False

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 3,
    ) -> List[Dict]:
        """
        Search for the most similar disease images.

        Parameters
        ----------
        query_vector : np.ndarray
            The L2-normalized feature vector of the query image.
        top_k : int
            Number of similar results to return.

        Returns
        -------
        list of dict
            Each dict contains:
              image  : str   — Path or identifier of the similar image
              label  : str   — Disease class label
              score  : float — Similarity score (lower distance = more similar)
        """
        if not self._loaded or self.index is None:
            logger.warning("FAISS index not loaded; returning empty results")
            return []

        try:
            # Ensure shape (1, d) for FAISS
            query = query_vector.reshape(1, -1).astype(np.float32)
            distances, indices = self.index.search(query, top_k)

            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx < 0 or idx >= len(self.metadata):
                    continue
                entry = self.metadata[idx]
                results.append({
                    "image": entry.get("image_path", "unknown"),
                    "label": entry.get("label", "unknown"),
                    "score": round(float(dist), 4),
                })

            return results
        except Exception as e:
            logger.error(f"FAISS search failed: {e}")
            return []

    @staticmethod
    def build_index(
        model: nn.Module,
        architecture: str,
        device: torch.device,
        transform,
        data_dir: str,
        output_dir: str,
        class_names: List[str],
        max_per_class: int = 50,
    ) -> bool:
        """
        Build a FAISS index from a dataset of disease images.

        This is an offline step — run once after training.

        Parameters
        ----------
        model : nn.Module
            The trained model.
        architecture : str
            Model architecture name.
        device : torch.device
            Computation device.
        transform : callable
            Image preprocessing transform.
        data_dir : str
            Root directory with class subfolders.
        output_dir : str
            Where to save the index and metadata.
        class_names : list
            Disease class names.
        max_per_class : int
            Max images to index per class (for speed).

        Returns
        -------
        bool
            True if index was built successfully.
        """
        try:
            import faiss
        except ImportError:
            logger.error("FAISS not installed. Install: pip install faiss-cpu")
            return False

        if not os.path.isdir(data_dir):
            logger.error(f"Data directory not found: {data_dir}")
            return False

        extractor = FeatureExtractor(model, architecture, device)
        all_features = []
        all_metadata = []

        logger.info(f"Building FAISS index from {data_dir}...")

        for class_name in sorted(os.listdir(data_dir)):
            class_dir = os.path.join(data_dir, class_name)
            if not os.path.isdir(class_dir):
                continue

            images = [
                f for f in os.listdir(class_dir)
                if f.lower().endswith(('.jpg', '.jpeg', '.png'))
            ][:max_per_class]

            for img_name in images:
                img_path = os.path.join(class_dir, img_name)
                try:
                    img = Image.open(img_path).convert("RGB")
                    tensor = transform(img).unsqueeze(0)
                    feat = extractor.extract(tensor)
                    all_features.append(feat)
                    all_metadata.append({
                        "image_path": img_path,
                        "label": class_name,
                    })
                except Exception as e:
                    logger.warning(f"Skipping {img_path}: {e}")

        extractor.remove_hook()

        if not all_features:
            logger.error("No features extracted — index not built")
            return False

        features_matrix = np.vstack(all_features).astype(np.float32)
        dim = features_matrix.shape[1]

        # Build L2 index
        index = faiss.IndexFlatL2(dim)
        index.add(features_matrix)

        # Save
        os.makedirs(output_dir, exist_ok=True)
        index_path = os.path.join(output_dir, "disease_features.index")
        meta_path = os.path.join(output_dir, "disease_metadata.json")

        faiss.write_index(index, index_path)
        with open(meta_path, "w") as f:
            json.dump(all_metadata, f, indent=2)

        logger.info(
            f"FAISS index built: {len(all_features)} vectors, dim={dim} "
            f"→ {index_path}"
        )
        return True
