from __future__ import annotations

import cv2
import numpy as np


def clahe_preprocess(
    image,
    valid_mask=None,
    low=1.0,
    high=99.0,
    clip_limit=2.0,
    tile_grid_size=(8, 8),
):
    """
    PARALLAX illumination-robust preprocessing.

    Steps:
        1. robust percentile normalization
        2. conversion to 8-bit
        3. CLAHE local contrast enhancement

    Returns:
        enhanced_image, valid_mask
    """

    image = np.asarray(image, dtype=np.float32)

    if valid_mask is None:
        valid_mask = np.isfinite(image)

    valid_mask = (
        np.asarray(valid_mask, dtype=bool)
        & np.isfinite(image)
    )

    if not np.any(valid_mask):
        return (
            np.zeros_like(image, dtype=np.uint8),
            valid_mask,
        )

    values = image[valid_mask]

    lo, hi = np.percentile(
        values,
        [float(low), float(high)],
    )

    if (
        not np.isfinite(lo)
        or not np.isfinite(hi)
        or hi <= lo
    ):
        normalized = np.zeros_like(
            image,
            dtype=np.float32,
        )
        normalized[valid_mask] = 0.5

    else:
        normalized = (
            (image - lo)
            / (hi - lo)
        )

        normalized = np.clip(
            normalized,
            0.0,
            1.0,
        )

    normalized[~valid_mask] = 0.0

    image_u8 = np.round(
        normalized * 255.0
    ).astype(np.uint8)

    clahe = cv2.createCLAHE(
        clipLimit=float(clip_limit),
        tileGridSize=tuple(
            int(x) for x in tile_grid_size
        ),
    )

    enhanced = clahe.apply(image_u8)

    enhanced[~valid_mask] = 0

    return enhanced, valid_mask


def preprocess_pair(
    image_a,
    image_b,
    mask_a=None,
    mask_b=None,
):
    """
    Apply identical PARALLAX preprocessing to both
    images in a registration pair.
    """

    enhanced_a, valid_a = clahe_preprocess(
        image_a,
        valid_mask=mask_a,
    )

    enhanced_b, valid_b = clahe_preprocess(
        image_b,
        valid_mask=mask_b,
    )

    return (
        enhanced_a,
        enhanced_b,
        valid_a,
        valid_b,
    )
