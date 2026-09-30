
import time
import numpy as np
import torch

from .base import MatchResult, Matcher


class SuperPointLightGlueMatcher(Matcher):
    def __init__(self, max_keypoints=512, device=None):
        self.max_keypoints = max_keypoints
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        from lightglue import SuperPoint, LightGlue

        self.extractor = SuperPoint(
            max_num_keypoints=max_keypoints
        ).eval().to(self.device)

        self.matcher = LightGlue(
            features="superpoint"
        ).eval().to(self.device)

    @staticmethod
    def _to_tensor(image, device):
        image = np.asarray(image, dtype=np.float32)

        if image.ndim == 3:
            image = image.mean(axis=2)

        if image.max() > 1.0:
            image = image / 255.0

        image = np.clip(image, 0.0, 1.0)

        return torch.from_numpy(image)[None, None].to(device)

    def match(self, image_a, image_b):
        start = time.perf_counter()

        with torch.inference_mode():
            tensor_a = self._to_tensor(image_a, self.device)
            tensor_b = self._to_tensor(image_b, self.device)

            feats_a = self.extractor.extract(tensor_a)
            feats_b = self.extractor.extract(tensor_b)

            result = self.matcher({
                "image0": feats_a,
                "image1": feats_b
            })

        matches = result["matches"][0].detach().cpu().numpy()

        scores = result.get("scores")
        if scores is not None:
            scores = scores[0].detach().cpu().numpy()
        else:
            scores = np.ones(len(matches), dtype=np.float32)

        keypoints_a = (
            feats_a["keypoints"][0].detach().cpu().numpy()
        )
        keypoints_b = (
            feats_b["keypoints"][0].detach().cpu().numpy()
        )

        runtime_ms = (time.perf_counter() - start) * 1000.0

        return MatchResult(
            keypoints_a=keypoints_a,
            keypoints_b=keypoints_b,
            matches=matches.astype(np.int64),
            scores=scores.astype(np.float32),
            model_name="superpoint_lightglue",
            runtime_ms=runtime_ms,
            metadata={
                "device": str(self.device),
                "max_keypoints": self.max_keypoints,
                "feature_extractor": "SuperPoint",
                "matcher": "LightGlue",
            },
        )
