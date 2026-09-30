from __future__ import annotations

import numpy as np


class LoFTRMatcher:

    name = "loftr"

    def __init__(self, pretrained="outdoor", device=None):
        self.pretrained = pretrained
        self.device = device
        self.model = None

    def _load(self):
        import torch
        from kornia.feature import LoFTR

        self.model = LoFTR(
            pretrained=self.pretrained
        ).eval().float()

        if self.device is not None:
            self.model = self.model.to(self.device)

    @staticmethod
    def _prepare(image):
        import torch

        image = np.asarray(
            image,
            dtype=np.float32
        )

        image = np.nan_to_num(image)

        low, high = np.percentile(
            image,
            [1, 99]
        )

        image = np.clip(
            (image - low) /
            (high - low + 1e-6),
            0,
            1
        )

        return torch.from_numpy(
            image
        )[None, None]

    def match(self, image_a, image_b):

        import torch

        if self.model is None:
            self._load()

        tensor_a = self._prepare(image_a)
        tensor_b = self._prepare(image_b)

        device = next(
            self.model.parameters()
        ).device

        tensor_a = tensor_a.to(
            device=device,
            dtype=torch.float32
        )
        tensor_b = tensor_b.to(
            device=device,
            dtype=torch.float32
        )

        with torch.inference_mode():

            output = self.model({
                "image0": tensor_a,
                "image1": tensor_b,
            })

        keypoints_a = (
            output["keypoints0"]
            .detach()
            .cpu()
            .numpy()
            .astype(np.float32)
        )

        keypoints_b = (
            output["keypoints1"]
            .detach()
            .cpu()
            .numpy()
            .astype(np.float32)
        )

        confidence = output.get(
            "confidence",
            torch.ones(
                len(keypoints_a),
                device=device
            )
        )

        confidence = (
            confidence
            .detach()
            .cpu()
            .numpy()
            .astype(np.float32)
        )

        matches = np.column_stack([
            np.arange(
                len(keypoints_a),
                dtype=np.int64
            ),
            np.arange(
                len(keypoints_b),
                dtype=np.int64
            ),
        ])

        return type(
            "MatchResult",
            (),
            {
                "keypoints_a": keypoints_a,
                "keypoints_b": keypoints_b,
                "matches": matches,
                "scores": confidence,
                "matcher_name": self.name,
            },
        )()
