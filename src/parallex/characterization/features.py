from __future__ import annotations

from ..routing.router import PairFeatures
from .pair import PairCharacterization
from .difficulty import estimate_difficulty


def characterization_to_features(
    characterization: PairCharacterization,
    metadata_a: dict,
    metadata_b: dict,
    *,
    overlap_ratio: float,
    image_shape_a=None,
    image_shape_b=None,
) -> PairFeatures:

    gsd_a = float(metadata_a.get("pixel_resolution_m") or 0.0)
    gsd_b = float(metadata_b.get("pixel_resolution_m") or 0.0)

    difficulty = estimate_difficulty(
        texture_score=characterization.texture_score,
        illumination_difference=characterization.illumination_difference,
        scale_ratio=characterization.scale_ratio,
        viewpoint_difference=characterization.viewpoint_difference,
        terrain_complexity=characterization.terrain_complexity,
        valid_pixel_ratio=characterization.valid_pixel_ratio,
    )

    height = 0
    width = 0

    if image_shape_a is not None:
        height, width = image_shape_a[:2]

    return PairFeatures(
        sensor_a=str(metadata_a.get("sensor", "unknown")),
        sensor_b=str(metadata_b.get("sensor", "unknown")),
        gsd_a=gsd_a,
        gsd_b=gsd_b,
        scale_ratio=characterization.scale_ratio,
        overlap_ratio=float(overlap_ratio),
        valid_pixel_ratio=characterization.valid_pixel_ratio,
        texture_score=characterization.texture_score,
        contrast_score=min(
            characterization.contrast_a,
            characterization.contrast_b,
        ),
        viewpoint_difference=characterization.viewpoint_difference,
        illumination_difference=characterization.illumination_difference,
        terrain_complexity=characterization.terrain_complexity,
        image_width=int(width),
        image_height=int(height),
        extra={
            "difficulty_score": difficulty.score,
            "difficulty_label": difficulty.label,
            "texture_a": characterization.texture_a,
            "texture_b": characterization.texture_b,
            "contrast_a": characterization.contrast_a,
            "contrast_b": characterization.contrast_b,
        },
    )
