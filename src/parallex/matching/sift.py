import time
import cv2
import numpy as np

from .base import MatchResult, Matcher


class SIFTMatcher(Matcher):
    def __init__(
        self,
        max_features: int = 5000,
        ratio_test: float = 0.75,
    ):
        self.max_features = max_features
        self.ratio_test = ratio_test

    @staticmethod
    def _to_uint8(image):
        image = np.asarray(image)

        if image.dtype == np.uint8:
            return image

        image = image.astype(np.float32)
        finite = np.isfinite(image)

        if not finite.any():
            return np.zeros(image.shape, dtype=np.uint8)

        values = image[finite]
        lo = np.percentile(values, 1)
        hi = np.percentile(values, 99)

        if hi <= lo:
            return np.zeros(image.shape, dtype=np.uint8)

        image = np.clip(
            (image - lo) / (hi - lo),
            0,
            1,
        )

        return (image * 255).astype(np.uint8)

    def match(self, image_a, image_b) -> MatchResult:
        start = time.perf_counter()

        image_a = self._to_uint8(image_a)
        image_b = self._to_uint8(image_b)

        sift = cv2.SIFT_create(
            nfeatures=self.max_features
        )

        keypoints_a, descriptors_a = sift.detectAndCompute(
            image_a,
            None,
        )

        keypoints_b, descriptors_b = sift.detectAndCompute(
            image_b,
            None,
        )

        points_a = np.array(
            [kp.pt for kp in keypoints_a],
            dtype=np.float32,
        )

        points_b = np.array(
            [kp.pt for kp in keypoints_b],
            dtype=np.float32,
        )

        if descriptors_a is None or descriptors_b is None:
            runtime_ms = (
                time.perf_counter() - start
            ) * 1000.0

            return MatchResult(
                keypoints_a=points_a,
                keypoints_b=points_b,
                matches=np.empty(
                    (0, 2),
                    dtype=np.int32,
                ),
                scores=np.empty(
                    (0,),
                    dtype=np.float32,
                ),
                model_name="SIFT",
                runtime_ms=runtime_ms,
            )

        matcher = cv2.BFMatcher(
            cv2.NORM_L2,
            crossCheck=False,
        )

        knn_matches = matcher.knnMatch(
            descriptors_a,
            descriptors_b,
            k=2,
        )

        good_matches = []

        for pair in knn_matches:
            if len(pair) < 2:
                continue

            m, n = pair

            if m.distance < self.ratio_test * n.distance:
                good_matches.append(m)

        matches = np.array(
            [
                [m.queryIdx, m.trainIdx]
                for m in good_matches
            ],
            dtype=np.int32,
        )

        if matches.size == 0:
            matches = np.empty(
                (0, 2),
                dtype=np.int32,
            )

        distances = np.array(
            [m.distance for m in good_matches],
            dtype=np.float32,
        )

        scores = (
            1.0 / (1.0 + distances)
            if len(distances)
            else np.empty(
                (0,),
                dtype=np.float32,
            )
        )

        runtime_ms = (
            time.perf_counter() - start
        ) * 1000.0

        return MatchResult(
            keypoints_a=points_a,
            keypoints_b=points_b,
            matches=matches,
            scores=scores,
            model_name="SIFT",
            runtime_ms=runtime_ms,
        )
