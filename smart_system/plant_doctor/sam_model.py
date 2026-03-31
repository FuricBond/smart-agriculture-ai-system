import torch
import cv2
import numpy as np
from segment_anything import sam_model_registry, SamPredictor


class SAMModel:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        sam = sam_model_registry["vit_b"](checkpoint="sam_vit_b.pth")
        sam.to(self.device)

        self.predictor = SamPredictor(sam)

    def get_mask(self, image_path, input_point=None, input_label=None):
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        self.predictor.set_image(image_rgb)

        h, w, _ = image.shape

        if input_point is None:
            input_point = np.array([[w // 2, h // 2]])
            input_label = np.array([1])

        masks, scores, _ = self.predictor.predict(
            point_coords=input_point,
            point_labels=input_label,
            multimask_output=True
        )

        best_mask = masks[np.argmax(scores)]

        return best_mask.astype(np.float32)
