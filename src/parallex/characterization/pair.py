from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass
class PairCharacterization:
    texture_a: float
    texture_b: float
    texture_score: float
    contrast_a: float
    contrast_b: float
    illumination_difference: float
    valid_pixel_ratio: float
    scale_ratio: float
    viewpoint_difference: float
    terrain_complexity: float


def _normalize(image):
    x = np.asarray(image, dtype=np.float32)
    finite = np.isfinite(x)

    if not finite.any():
        return np.zeros_like(x)

    values = x[finite]
    lo, hi = np.percentile(values, [1, 99])

    if hi <= lo:
        return np.zeros_like(x)

    return np.clip((x - lo) / (hi - lo), 0, 1)


def _texture_score(image):
    x = _normalize(image)

    gx = np.diff(x, axis=1)
    gy = np.diff(x, axis=0)

    gradient = np.mean(np.abs(gx)) + np.mean(np.abs(gy))

    return float(np.clip(gradient * 5.0, 0, 1))


def _contrast(image):
    x = _normalize(image)
    return float(np.clip(np.std(x) * 3.0, 0, 1))


def _illumination_difference(image_a, image_b):
    a = _normalize(image_a)
    b = _normalize(image_b)

    h = min(a.shape[0], b.shape[0])
    w = min(a.shape[1], b.shape[1])

    a = a[:h, :w]
    b = b[:h, :w]

    return float(np.clip(abs(float(np.mean(a)) - float(np.mean(b))), 0, 1))


def _valid_pixel_ratio(image_a, image_b):
    a = np.asarray(image_a)
    b = np.asarray(image_b)

    valid_a = np.isfinite(a) & (a != 0)
    valid_b = np.isfinite(b) & (b != 0)

    return float(min(np.mean(valid_a), np.mean(valid_b)))


def _viewpoint_difference(metadata_a, metadata_b):
    angles = ["roll_deg", "pitch_deg", "yaw_deg"]

    values = []

    for key in angles:
        a = metadata_a.get(key)
        b = metadata_b.get(key)

        if a is not None and b is not None:
            values.append(abs(float(a) - float(b)))

    if not values:
        return 0.0

    return float(np.clip(np.mean(values) / 180.0, 0, 1))


def characterize_pair(
    image_a,
    image_b,
    metadata_a,
    metadata_b,
    overlap_ratio=0.0,
):
    gsd_a = metadata_a.get("pixel_resolution_m")
    gsd_b = metadata_b.get("pixel_resolution_m")

    if gsd_a and gsd_b and gsd_a > 0 and gsd_b > 0:
        scale_ratio = float(max(gsd_a, gsd_b) / min(gsd_a, gsd_b))
    else:
        scale_ratio = 1.0

    texture_a = _texture_score(image_a)
    texture_b = _texture_score(image_b)

    texture_score = float(min(texture_a, texture_b))

    contrast_a = _contrast(image_a)
    contrast_b = _contrast(image_b)

    illumination_difference = _illumination_difference(
        image_a,
        image_b,
    )

    valid_ratio = _valid_pixel_ratio(
        image_a,
        image_b,
    )

    viewpoint_difference = _viewpoint_difference(
        metadata_a,
        metadata_b,
    )

    # Initial terrain-complexity proxy.
    # Final version should incorporate DEM/terrain data.
    terrain_complexity = float(
        np.clip(
            (texture_score + min(contrast_a, contrast_b)) / 2.0,
            0,
            1,
        )
    )

    return PairCharacterization(
        texture_a=texture_a,
        texture_b=texture_b,
        texture_score=texture_score,
        contrast_a=contrast_a,
        contrast_b=contrast_b,
        illumination_difference=illumination_difference,
        valid_pixel_ratio=valid_ratio,
        scale_ratio=scale_ratio,
        viewpoint_difference=viewpoint_difference,
        terrain_complexity=terrain_complexity,
    )

