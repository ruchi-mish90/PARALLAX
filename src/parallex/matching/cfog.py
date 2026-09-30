import time
import cv2
import numpy as np
from scipy.ndimage import gaussian_filter1d

from .base import MatchResult, Matcher


def oriented_gradient_channels(
    image,
    n_channels=9,
):
    """
    Build the pixel-wise orientated gradient channels.

    Gradients are folded into [0, pi) so that contrast
    inversion between modalities does not reverse the
    orientation representation.
    """

    image = np.asarray(
        image,
        dtype=np.float32,
    )

    if image.ndim != 2:
        raise ValueError(
            "CFOG expects a 2-D grayscale image"
        )

    gx = cv2.Sobel(
        image,
        cv2.CV_32F,
        1,
        0,
        ksize=3,
    )

    gy = cv2.Sobel(
        image,
        cv2.CV_32F,
        0,
        1,
        ksize=3,
    )

    magnitude = np.sqrt(
        gx * gx +
        gy * gy
    )

    orientation = (
        np.arctan2(
            gy,
            gx,
        ) % np.pi
    )

    bin_position = (
        orientation /
        np.pi *
        n_channels
    )

    lower = np.floor(
        bin_position
    ).astype(np.int32)

    fraction = (
        bin_position -
        lower
    )

    upper = (
        lower + 1
    ) % n_channels

    channels = np.zeros(
        (
            n_channels,
            image.shape[0],
            image.shape[1],
        ),
        dtype=np.float32,
    )

    for k in range(
        n_channels
    ):

        contribution_lower = (
            magnitude *
            (lower == k) *
            (1.0 - fraction)
        )

        contribution_upper = (
            magnitude *
            (upper == k) *
            fraction
        )

        channels[k] = (
            contribution_lower +
            contribution_upper
        )

    return channels


def cfog_feature_map(
    image,
    n_channels=9,
    sigma=0.8,
    orientation_smoothing=True,
):
    """
    Construct the CFOG pixel-wise feature representation.

    Spatial smoothing:
        Gaussian kernel with STD sigma.

    Orientation smoothing:
        [1, 2, 1] / 4 circular kernel.

    Output:
        (n_channels, H, W)
    """

    channels = oriented_gradient_channels(
        image,
        n_channels=n_channels,
    )

    smoothed = np.empty_like(
        channels
    )

    for k in range(
        n_channels
    ):
        smoothed[k] = gaussian_filter1d(
            channels[k],
            sigma=float(sigma),
            axis=0,
            mode="reflect",
        )

        smoothed[k] = gaussian_filter1d(
            smoothed[k],
            sigma=float(sigma),
            axis=1,
            mode="reflect",
        )

    if orientation_smoothing:

        circular = (
            smoothed +
            np.roll(
                smoothed,
                1,
                axis=0,
            ) +
            np.roll(
                smoothed,
                -1,
                axis=0,
            )
        )

        # The paper uses [1,2,1]^T.
        # Therefore the center channel receives
        # double weight.
        circular = (
            0.25 * (
                np.roll(
                    smoothed,
                    1,
                    axis=0,
                ) +
                2.0 * smoothed +
                np.roll(
                    smoothed,
                    -1,
                    axis=0,
                )
            )
        )

        smoothed = circular.astype(
            np.float32
        )

    return smoothed


def _detect_cfog_keypoints(
    feature_map,
    max_keypoints=500,
    spacing=8,
    border=16,
):
    """
    Select strong structural locations from the
    CFOG feature energy map.
    """

    energy = np.sqrt(
        np.sum(
            feature_map ** 2,
            axis=0,
        )
    )

    h, w = energy.shape

    if (
        h <= 2 * border or
        w <= 2 * border
    ):
        return np.empty(
            (0, 2),
            dtype=np.float32,
        )

    normalized = cv2.normalize(
        energy,
        None,
        0,
        255,
        cv2.NORM_MINMAX,
    ).astype(np.uint8)

    detector = cv2.FastFeatureDetector_create(
        threshold=10,
        nonmaxSuppression=True,
    )

    keypoints = detector.detect(
        normalized,
        None,
    )

    candidates = []

    for kp in keypoints:

        x = float(kp.pt[0])
        y = float(kp.pt[1])

        xi = int(round(x))
        yi = int(round(y))

        if (
            xi < border or
            xi >= w - border or
            yi < border or
            yi >= h - border
        ):
            continue

        candidates.append(
            (
                float(energy[yi, xi]),
                x,
                y,
            )
        )

    candidates.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    selected = []

    min_distance_sq = (
        float(spacing) ** 2
    )

    for score, x, y in candidates:

        if all(
            (x - px) ** 2 +
            (y - py) ** 2
            >= min_distance_sq
            for px, py in selected
        ):
            selected.append(
                (x, y)
            )

        if len(selected) >= max_keypoints:
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


def cfog_patch_descriptors(
    feature_map,
    keypoints,
    patch_size=21,
):
    """
    Extract normalized local CFOG patch descriptors.

    Each pixel has 9 CFOG channels. A local patch is
    flattened into a single normalized vector.

    The underlying CFOG feature dimensionality remains 9.
    """

    feature_map = np.asarray(
        feature_map,
        dtype=np.float32,
    )

    keypoints = np.asarray(
        keypoints,
        dtype=np.float32,
    )

    n_channels, h, w = (
        feature_map.shape
    )

    if len(keypoints) == 0:
        return np.empty(
            (
                0,
                n_channels *
                patch_size *
                patch_size,
            ),
            dtype=np.float32,
        )

    half = patch_size // 2

    descriptors = []

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
                    n_channels *
                    patch_size *
                    patch_size,
                    dtype=np.float32,
                )
            )
            continue

        patch = feature_map[
            :,
            y0:y1,
            x0:x1,
        ]

        descriptor = patch.reshape(
            -1
        ).astype(
            np.float32
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


def _match_descriptors(
    descriptors_a,
    descriptors_b,
    ratio_test=0.85,
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

    distances_sq = (
        aa +
        bb -
        2.0 *
        descriptors_a @
        descriptors_b.T
    )

    distances_sq = np.maximum(
        distances_sq,
        0.0,
    )

    distances = np.sqrt(
        distances_sq
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
                [
                    i,
                    best,
                ]
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


class CFOGMatcher(Matcher):

    def __init__(
        self,
        n_channels=9,
        sigma=0.8,
        patch_size=21,
        max_keypoints=500,
        ratio_test=0.85,
        keypoint_spacing=8,
        orientation_smoothing=True,
    ):
        self.n_channels = n_channels
        self.sigma = sigma
        self.patch_size = patch_size
        self.max_keypoints = max_keypoints
        self.ratio_test = ratio_test
        self.keypoint_spacing = (
            keypoint_spacing
        )
        self.orientation_smoothing = (
            orientation_smoothing
        )

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
                "CFOG expects 2-D grayscale images"
            )

        feature_a = cfog_feature_map(
            image_a,
            n_channels=self.n_channels,
            sigma=self.sigma,
            orientation_smoothing=(
                self.orientation_smoothing
            ),
        )

        feature_b = cfog_feature_map(
            image_b,
            n_channels=self.n_channels,
            sigma=self.sigma,
            orientation_smoothing=(
                self.orientation_smoothing
            ),
        )

        keypoints_a = (
            _detect_cfog_keypoints(
                feature_a,
                max_keypoints=self.max_keypoints,
                spacing=self.keypoint_spacing,
                border=self.patch_size // 2 + 2,
            )
        )

        keypoints_b = (
            _detect_cfog_keypoints(
                feature_b,
                max_keypoints=self.max_keypoints,
                spacing=self.keypoint_spacing,
                border=self.patch_size // 2 + 2,
            )
        )

        descriptors_a = (
            cfog_patch_descriptors(
                feature_a,
                keypoints_a,
                patch_size=self.patch_size,
            )
        )

        descriptors_b = (
            cfog_patch_descriptors(
                feature_b,
                keypoints_b,
                patch_size=self.patch_size,
            )
        )

        matches, scores = (
            _match_descriptors(
                descriptors_a,
                descriptors_b,
                ratio_test=self.ratio_test,
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
            model_name="CFOG",
            runtime_ms=runtime_ms,
            metadata={
                "n_channels":
                    self.n_channels,
                "sigma":
                    self.sigma,
                "patch_size":
                    self.patch_size,
                "feature_dimension":
                    self.n_channels,
                "orientation_range":
                    "0-180 degrees",
                "orientation_smoothing":
                    self.orientation_smoothing,
                "ratio_test":
                    self.ratio_test,
                "representation":
                    "pixel-wise CFOG",
            },
        )


__all__ = [
    "oriented_gradient_channels",
    "cfog_feature_map",
    "cfog_patch_descriptors",
    "CFOGMatcher",
]
