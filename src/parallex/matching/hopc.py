import time
import cv2
import numpy as np

from .base import MatchResult, Matcher
from .rift import compute_rift_core


class HOPCMatcher(Matcher):
    """
    HOPC matcher for multimodal image registration.

    Default descriptor:
        3 x 3 cells
        4 x 4 pixels per cell
        8 orientation bins

    Descriptor dimension:
        3 x 3 x 8 = 72
    """

    def __init__(
        self,
        n_scales=4,
        n_orientations=6,
        n_bins=8,
        cell_size=4,
        cells_per_block=3,
        max_keypoints=1000,
        ratio_test=0.80,
        keypoint_spacing=8,
    ):
        self.n_scales = n_scales
        self.n_orientations = n_orientations
        self.n_bins = n_bins
        self.cell_size = cell_size
        self.cells_per_block = cells_per_block
        self.max_keypoints = max_keypoints
        self.ratio_test = ratio_test
        self.keypoint_spacing = keypoint_spacing

        self.patch_size = (
            cell_size * cells_per_block
        )

        self.descriptor_dimension = (
            cells_per_block *
            cells_per_block *
            n_bins
        )

    # --------------------------------------------------------
    # Orientation map from odd Log-Gabor responses
    # --------------------------------------------------------

    def _orientation_map(
        self,
        odd_responses,
    ):
        """
        Estimate local structural orientation.

        Odd responses are aggregated across scales.
        Orientation is represented over [0, pi).
        """

        odd = np.asarray(
            odd_responses,
            dtype=np.float32,
        )

        # odd shape:
        # (scales, orientations, H, W)

        response = np.sum(
            np.abs(odd),
            axis=0,
        )

        dominant_index = np.argmax(
            response,
            axis=0,
        )

        orientation_step = (
            np.pi /
            self.n_orientations
        )

        orientation = (
            dominant_index.astype(
                np.float32
            ) *
            orientation_step
        )

        strength = np.max(
            response,
            axis=0,
        )

        return (
            orientation,
            strength,
        )

    # --------------------------------------------------------
    # Phase-congruency structural map
    # --------------------------------------------------------

    def _structural_map(
        self,
        phase_congruency,
    ):
        pc = np.asarray(
            phase_congruency,
            dtype=np.float32,
        )

        if pc.ndim != 3:
            raise ValueError(
                "Phase congruency must have "
                "shape (orientation,H,W)"
            )

        return np.max(
            pc,
            axis=0,
        ).astype(np.float32)

    # --------------------------------------------------------
    # Keypoint detector
    # --------------------------------------------------------

    def _detect_keypoints(
        self,
        structural,
    ):
        """
        Select strong structural locations with
        spatial suppression.

        This is deliberately not claimed to be identical
        to every implementation of the original HOPC
        detector; it provides a deterministic detector
        compatible with our registration pipeline.
        """

        structural = np.asarray(
            structural,
            dtype=np.float32,
        )

        h, w = structural.shape

        border = (
            self.patch_size // 2
        )

        if (
            h <= 2 * border or
            w <= 2 * border
        ):
            return np.empty(
                (0, 2),
                dtype=np.float32,
            )

        # Normalize for detector stability.
        normalized = cv2.normalize(
            structural,
            None,
            0,
            255,
            cv2.NORM_MINMAX,
        ).astype(np.uint8)

        fast = cv2.FastFeatureDetector_create(
            threshold=10,
            nonmaxSuppression=True,
        )

        candidates = fast.detect(
            normalized,
            None,
        )

        if not candidates:
            # Fallback to strongest structural points.
            flat = structural.copy()

            flat[:border, :] = 0
            flat[-border:, :] = 0
            flat[:, :border] = 0
            flat[:, -border:] = 0

            count = min(
                self.max_keypoints,
                max(
                    1,
                    flat.size // 1000,
                ),
            )

            indices = np.argpartition(
                flat.ravel(),
                -count,
            )[-count:]

            ys, xs = np.unravel_index(
                indices,
                flat.shape,
            )

            candidates = [
                cv2.KeyPoint(
                    float(x),
                    float(y),
                    float(self.patch_size),
                )
                for x, y in zip(xs, ys)
            ]

        scored = []

        for kp in candidates:

            x = int(round(kp.pt[0]))
            y = int(round(kp.pt[1]))

            if (
                x < border or
                x >= w - border or
                y < border or
                y >= h - border
            ):
                continue

            scored.append(
                (
                    float(structural[y, x]),
                    float(kp.pt[0]),
                    float(kp.pt[1]),
                )
            )

        scored.sort(
            key=lambda x: x[0],
            reverse=True,
        )

        selected = []

        min_dist = float(
            self.keypoint_spacing
        )

        min_dist_sq = (
            min_dist ** 2
        )

        for score, x, y in scored:

            if all(
                (x - px) ** 2 +
                (y - py) ** 2
                >= min_dist_sq
                for px, py in selected
            ):
                selected.append(
                    (x, y)
                )

            if len(selected) >= (
                self.max_keypoints
            ):
                break

        if not selected:
            return np.empty(
                (0, 2),
                dtype=np.float32,
            )

        return np.asarray(
            selected,
            dtype=np.float32,
        )

    # --------------------------------------------------------
    # HOPC descriptor
    # --------------------------------------------------------

    def _descriptor(
        self,
        structural,
        orientation,
        keypoints,
    ):
        """
        Build dense local HOPC descriptors.

        Each descriptor consists of:

            3 x 3 spatial cells
            8 orientation bins

        yielding 72 dimensions.
        """

        keypoints = np.asarray(
            keypoints,
            dtype=np.float32,
        )

        dimension = (
            self.descriptor_dimension
        )

        if len(keypoints) == 0:
            return np.empty(
                (0, dimension),
                dtype=np.float32,
            )

        patch_size = (
            self.patch_size
        )

        half = patch_size // 2

        descriptors = []

        # Pixel offsets.
        offsets = np.arange(
            -half,
            half,
            dtype=np.int32,
        )

        oy, ox = np.meshgrid(
            offsets,
            offsets,
            indexing="ij",
        )

        h, w = structural.shape

        for x, y in keypoints:

            cx = int(round(x))
            cy = int(round(y))

            x0 = cx - half
            y0 = cy - half
            x1 = x0 + patch_size
            y1 = y0 + patch_size

            if (
                x0 < 0 or
                y0 < 0 or
                x1 > w or
                y1 > h
            ):
                descriptors.append(
                    np.zeros(
                        dimension,
                        dtype=np.float32,
                    )
                )
                continue

            local_strength = structural[
                y0:y1,
                x0:x1,
            ]

            local_orientation = orientation[
                y0:y1,
                x0:x1,
            ]

            # HOPC uses orientation modulo pi so
            # opposite contrast polarity is treated
            # consistently.
            local_orientation = (
                local_orientation % np.pi
            )

            bins = (
                local_orientation /
                np.pi *
                self.n_bins
            )

            bin_float = bins % (
                self.n_bins
            )

            bin0 = np.floor(
                bin_float
            ).astype(np.int32)

            frac = (
                bin_float -
                bin0
            )

            bin1 = (
                bin0 + 1
            ) % self.n_bins

            # Gaussian weighting.
            yy, xx = np.mgrid[
                0:patch_size,
                0:patch_size,
            ]

            center = (
                patch_size - 1
            ) / 2.0

            sigma = (
                patch_size / 2.0
            )

            gaussian = np.exp(
                -(
                    (xx - center) ** 2 +
                    (yy - center) ** 2
                ) /
                (
                    2.0 * sigma ** 2
                )
            ).astype(
                np.float32
            )

            weights = (
                local_strength *
                gaussian
            )

            descriptor = np.zeros(
                dimension,
                dtype=np.float32,
            )

            cell_size = (
                self.cell_size
            )

            for py in range(
                patch_size
            ):
                cell_y = min(
                    py // cell_size,
                    self.cells_per_block - 1,
                )

                for px in range(
                    patch_size
                ):
                    cell_x = min(
                        px // cell_size,
                        self.cells_per_block - 1,
                    )

                    base = (
                        (
                            cell_y *
                            self.cells_per_block +
                            cell_x
                        ) *
                        self.n_bins
                    )

                    weight = float(
                        weights[py, px]
                    )

                    descriptor[
                        base + bin0[py, px]
                    ] += (
                        weight *
                        (1.0 - frac[py, px])
                    )

                    descriptor[
                        base + bin1[py, px]
                    ] += (
                        weight *
                        frac[py, px]
                    )

            norm = np.linalg.norm(
                descriptor
            )

            if norm > 1e-8:
                descriptor /= norm

            descriptors.append(
                descriptor
            )

        return np.asarray(
            descriptors,
            dtype=np.float32,
        )

    # --------------------------------------------------------
    # Descriptor matching
    # --------------------------------------------------------

    @staticmethod
    def _match_descriptors(
        descriptors_a,
        descriptors_b,
        ratio_test,
    ):
        if (
            len(descriptors_a) == 0 or
            len(descriptors_b) < 2
        ):
            return (
                np.empty(
                    (0, 2),
                    dtype=np.int32,
                ),
                np.empty(
                    (0,),
                    dtype=np.float32,
                ),
            )

        # Squared Euclidean distance.
        aa = np.sum(
            descriptors_a ** 2,
            axis=1,
            keepdims=True,
        )

        bb = np.sum(
            descriptors_b ** 2,
            axis=1,
            keepdims=True,
        ).T

        distance_sq = (
            aa +
            bb -
            2.0 *
            descriptors_a @
            descriptors_b.T
        )

        distance_sq = np.maximum(
            distance_sq,
            0.0,
        )

        distances = np.sqrt(
            distance_sq
        )

        matches = []
        scores = []

        for i in range(
            distances.shape[0]
        ):

            row = distances[i]

            order = np.argsort(
                row
            )

            best = int(
                order[0]
            )

            second = int(
                order[1]
            )

            d1 = float(
                row[best]
            )

            d2 = float(
                row[second]
            )

            if d1 < ratio_test * d2:

                matches.append(
                    [i, best]
                )

                scores.append(
                    1.0 /
                    (1.0 + d1)
                )

        if not matches:
            return (
                np.empty(
                    (0, 2),
                    dtype=np.int32,
                ),
                np.empty(
                    (0,),
                    dtype=np.float32,
                ),
            )

        return (
            np.asarray(
                matches,
                dtype=np.int32,
            ),
            np.asarray(
                scores,
                dtype=np.float32,
            ),
        )

    # --------------------------------------------------------
    # Public matcher
    # --------------------------------------------------------

    def match(
        self,
        image_a,
        image_b,
    ):

        start = time.perf_counter()

        image_a = np.asarray(
            image_a,
            dtype=np.float32,
        )

        image_b = np.asarray(
            image_b,
            dtype=np.float32,
        )

        if (
            image_a.ndim != 2 or
            image_b.ndim != 2
        ):
            raise ValueError(
                "HOPC expects 2-D grayscale images"
            )

        core_a = compute_rift_core(
            image_a,
            n_scales=self.n_scales,
            n_orientations=self.n_orientations,
        )

        core_b = compute_rift_core(
            image_b,
            n_scales=self.n_scales,
            n_orientations=self.n_orientations,
        )

        orientation_a, strength_a = (
            self._orientation_map(
                core_a["odd"]
            )
        )

        orientation_b, strength_b = (
            self._orientation_map(
                core_b["odd"]
            )
        )

        structural_a = (
            self._structural_map(
                core_a["phase_congruency"]
            )
        )

        structural_b = (
            self._structural_map(
                core_b["phase_congruency"]
            )
        )

        keypoints_a = (
            self._detect_keypoints(
                structural_a
            )
        )

        keypoints_b = (
            self._detect_keypoints(
                structural_b
            )
        )

        descriptors_a = self._descriptor(
            structural_a,
            orientation_a,
            keypoints_a,
        )

        descriptors_b = self._descriptor(
            structural_b,
            orientation_b,
            keypoints_b,
        )

        matches, scores = (
            self._match_descriptors(
                descriptors_a,
                descriptors_b,
                self.ratio_test,
            )
        )

        runtime_ms = (
            time.perf_counter() -
            start
        ) * 1000.0

        return MatchResult(
            keypoints_a=keypoints_a,
            keypoints_b=keypoints_b,
            matches=matches,
            scores=scores,
            model_name="HOPC",
            runtime_ms=runtime_ms,
            metadata={
                "n_scales":
                    self.n_scales,
                "n_orientations":
                    self.n_orientations,
                "n_bins":
                    self.n_bins,
                "cell_size":
                    self.cell_size,
                "cells_per_block":
                    self.cells_per_block,
                "descriptor_dimension":
                    self.descriptor_dimension,
                "ratio_test":
                    self.ratio_test,
                "orientation_range":
                    "0-180 degrees",
                "structural_representation":
                    "phase_congruency",
            },
        )


__all__ = [
    "HOPCMatcher",
]
