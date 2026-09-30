from __future__ import annotations

import cv2
import numpy as np

from ..matching.registry import create_matcher
from .router import AdaptiveRouter, PairFeatures


class RoutingEngine:
    def __init__(self, router=None):
        self.router = router or AdaptiveRouter()

    def _configs(self):
        return {
            "sift": {
                "max_features": 2000,
            },
            "hopc": {
                "max_keypoints": 500,
            },
            "cfog": {
                "max_keypoints": 500,
            },
            "superpoint_lightglue": {
                "max_keypoints": 512,
            },
            "loftr": {
                "pretrained": "outdoor",
            },
        }

    def route_candidates(self, features):
        decision = self.router.route(features)

        if decision.rejected:
            return decision, []

        ranked = sorted(
            decision.candidate_scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        return decision, [name for name, _ in ranked]

    @staticmethod
    def _prepare_loftr_image(image, max_dimension=1024):
        """
        Downscale only the temporary image used by LoFTR.

        The original image is never modified.
        Returns:
            resized_image, scale_x, scale_y
        """
        image = np.asarray(image)

        h, w = image.shape[:2]
        largest = max(h, w)

        if largest <= max_dimension:
            return image, 1.0, 1.0

        scale = float(max_dimension) / float(largest)

        new_w = max(8, int(round(w * scale)))
        new_h = max(8, int(round(h * scale)))

        resized = cv2.resize(
            image,
            (new_w, new_h),
            interpolation=cv2.INTER_AREA,
        )

        scale_x = float(w) / float(new_w)
        scale_y = float(h) / float(new_h)

        return resized, scale_x, scale_y

    @staticmethod
    def _restore_loftr_coordinates(match_result, scale_x, scale_y):
        """
        Restore LoFTR coordinates from the temporary resized image
        back to the original ROI coordinate system.

        PARALLAX matchers normally return coordinate pairs as:
            matches[:, 0] -> source point
            matches[:, 1] -> target point

        If the matcher stores coordinates under a different compatible
        representation, leave the result unchanged rather than corrupting it.
        """
        if match_result is None:
            return match_result

        matches = getattr(match_result, "matches", None)

        if matches is None:
            return match_result

        matches = np.asarray(matches)

        if matches.size == 0:
            return match_result

        restored = matches.copy()

        # Standard PARALLAX coordinate representation:
        # (N, 2, 2)
        #   N = matches
        #   first 2 = source/target
        #   last 2 = x/y
        if restored.ndim == 3 and restored.shape[-2:] == (2, 2):
            restored[:, 0, 0] *= scale_x
            restored[:, 0, 1] *= scale_y
            restored[:, 1, 0] *= scale_x
            restored[:, 1, 1] *= scale_y

        # Alternative representation:
        # (N, 4) = x_a, y_a, x_b, y_b
        elif restored.ndim == 2 and restored.shape[1] == 4:
            restored[:, 0] *= scale_x
            restored[:, 1] *= scale_y
            restored[:, 2] *= scale_x
            restored[:, 3] *= scale_y

        # Alternative representation:
        # (N, 2) can represent one coordinate array, but cannot safely
        # distinguish source/target here, so do not modify it.
        else:
            return match_result

        match_result.matches = restored

        metadata = getattr(match_result, "metadata", None)

        if metadata is None:
            metadata = {}

        metadata["loftr_input_scale_x"] = scale_x
        metadata["loftr_input_scale_y"] = scale_y
        metadata["loftr_memory_safe"] = True
        metadata["loftr_original_coordinates_restored"] = True

        match_result.metadata = metadata

        return match_result

    def _run_loftr(self, image_a, image_b):
        """
        Memory-safe LoFTR execution.

        LoFTR is NOT skipped for large ROIs. Instead, both images are
        temporarily downscaled so that the largest dimension is <= 1024.
        """
        prepared_a, scale_ax, scale_ay = self._prepare_loftr_image(
            image_a,
            max_dimension=1024,
        )

        prepared_b, scale_bx, scale_by = self._prepare_loftr_image(
            image_b,
            max_dimension=1024,
        )

        matcher = create_matcher(
            "loftr",
            **self._configs()["loftr"],
        )

        result = matcher.match(prepared_a, prepared_b)

        # Source and target may have different resize factors.
        matches = getattr(result, "matches", None)

        if matches is not None:
            matches = np.asarray(matches)

            if matches.size > 0:
                restored = matches.copy()

                if restored.ndim == 3 and restored.shape[-2:] == (2, 2):
                    restored[:, 0, 0] *= scale_ax
                    restored[:, 0, 1] *= scale_ay
                    restored[:, 1, 0] *= scale_bx
                    restored[:, 1, 1] *= scale_by

                    result.matches = restored

                elif restored.ndim == 2 and restored.shape[1] == 4:
                    restored[:, 0] *= scale_ax
                    restored[:, 1] *= scale_ay
                    restored[:, 2] *= scale_bx
                    restored[:, 3] *= scale_by

                    result.matches = restored

        metadata = getattr(result, "metadata", None)

        if metadata is None:
            metadata = {}

        metadata["loftr_input_shape_a"] = tuple(prepared_a.shape[:2])
        metadata["loftr_input_shape_b"] = tuple(prepared_b.shape[:2])
        metadata["loftr_scale_a"] = (scale_ax, scale_ay)
        metadata["loftr_scale_b"] = (scale_bx, scale_by)
        metadata["loftr_memory_safe"] = True
        metadata["loftr_original_coordinates_restored"] = True

        result.metadata = metadata

        return result

    def run(self, image_a, image_b, features):
        decision, candidates = self.route_candidates(features)

        if decision.rejected:
            return decision, None

        selected = candidates[0]

        if selected == "loftr":
            result = self._run_loftr(image_a, image_b)
        else:
            matcher = create_matcher(
                selected,
                **self._configs().get(selected, {}),
            )
            result = matcher.match(image_a, image_b)

        return decision, result

    def run_matcher(self, matcher_name, image_a, image_b):
        """
        Explicit matcher execution used by the fallback pipeline.

        LoFTR is memory-safe and is never rejected solely because the
        original ROI is larger than 1024 pixels.
        """
        if matcher_name == "loftr":
            return self._run_loftr(image_a, image_b)

        matcher = create_matcher(
            matcher_name,
            **self._configs().get(matcher_name, {}),
        )

        return matcher.match(image_a, image_b)
