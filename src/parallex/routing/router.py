from .representation_router import RepresentationRouter, RepresentationRoute

from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class PairFeatures:
    sensor_a: str = "unknown"
    sensor_b: str = "unknown"

    gsd_a: float = 0.0
    gsd_b: float = 0.0
    scale_ratio: float = 1.0

    overlap_ratio: float = 1.0
    valid_pixel_ratio: float = 1.0

    texture_score: float = 0.5
    shadow_ratio: float = 0.0
    contrast_score: float = 0.5

    viewpoint_difference: float = 0.0
    illumination_difference: float = 0.0
    phase_difference: float = 0.0

    terrain_complexity: float = 0.5
    geometric_uncertainty: float = 0.0

    image_width: int = 0
    image_height: int = 0

    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RoutingDecision:
    selected_matcher: str
    difficulty: str
    confidence: float
    reason: str
    candidate_scores: Dict[str, float]
    rejected: bool = False
    rejection_reason: str = ""
    selected_representation: str = "native"
    representation_band: int | None = None
    representation_reason: str = ""


class AdaptiveRouter:

    MATCHERS = (
        "sift",
        "hopc",
        "cfog",
        "superpoint_lightglue",
        "loftr",
    )

    def __init__(self):
        self.representation_router = RepresentationRouter()
        pass

    @staticmethod
    def _clamp(value):
        return max(0.0, min(1.0, float(value)))

    def estimate_difficulty(self, features: PairFeatures):
        difficulty_score = 0.0

        difficulty_score += 0.20 * self._clamp(
            abs(features.scale_ratio - 1.0)
        )

        difficulty_score += 0.20 * self._clamp(
            features.viewpoint_difference
        )

        difficulty_score += 0.20 * self._clamp(
            features.illumination_difference
        )

        difficulty_score += 0.10 * self._clamp(
            features.phase_difference
        )

        difficulty_score += 0.10 * self._clamp(
            features.shadow_ratio
        )

        difficulty_score += 0.10 * self._clamp(
            1.0 - features.texture_score
        )

        difficulty_score += 0.10 * self._clamp(
            features.terrain_complexity
        )

        if difficulty_score < 0.33:
            label = "easy"
        elif difficulty_score < 0.66:
            label = "medium"
        elif difficulty_score < 0.85:
            label = "hard"
        else:
            label = "extreme"

        return label, difficulty_score

    def route(self, features: PairFeatures) -> RoutingDecision:
        representation_features = {
            key: value
            for key, value in vars(features).items()
        }

        representation_route = self.representation_router.route(
            representation_features
        )

        if features.overlap_ratio <= 0.0:
            return RoutingDecision(
                selected_matcher="none",
                selected_representation=representation_route.representation,
                representation_band=representation_route.band,
                representation_reason=representation_route.reason,
                difficulty="unobservable",
                confidence=1.0,
                reason="No meaningful spatial overlap.",
                candidate_scores={},
                rejected=True,
                rejection_reason="no_overlap",
            )

        if features.valid_pixel_ratio < 0.05:
            return RoutingDecision(
                selected_matcher="none",
                selected_representation=representation_route.representation,
                representation_band=representation_route.band,
                representation_reason=representation_route.reason,
                difficulty="unobservable",
                confidence=0.95,
                reason="Insufficient valid image content.",
                candidate_scores={},
                rejected=True,
                rejection_reason="insufficient_valid_pixels",
            )

        difficulty, difficulty_score = self.estimate_difficulty(features)

        scores = {
            "sift": 0.50,
            "hopc": 0.50,
            "cfog": 0.50,
            "superpoint_lightglue": 0.50,
            "loftr": 0.50,
        }

        # Radiometric robustness
        scores["cfog"] += 0.30 * features.illumination_difference
        scores["hopc"] += 0.25 * features.illumination_difference

        # Texture-poor scenes
        scores["hopc"] += 0.25 * (1.0 - features.texture_score)
        scores["superpoint_lightglue"] += 0.20 * (
            1.0 - features.texture_score
        )

        # Viewpoint / scale difficulty
        scores["superpoint_lightglue"] += 0.30 * features.viewpoint_difference
        scores["superpoint_lightglue"] += 0.25 * self._clamp(
            abs(features.scale_ratio - 1.0)
        )

        # Terrain complexity
        scores["superpoint_lightglue"] += 0.15 * features.terrain_complexity

        # Dense matching for difficult/extreme pairs
        scores["loftr"] += 0.25 * features.viewpoint_difference
        scores["loftr"] += 0.25 * features.illumination_difference
        scores["loftr"] += 0.20 * features.terrain_complexity
        scores["loftr"] += 0.20 * (1.0 - features.texture_score)
        scores["hopc"] += 0.10 * features.terrain_complexity

        # Keep scores bounded
        scores = {
            k: self._clamp(v)
            for k, v in scores.items()
        }

        selected = max(scores, key=scores.get)
        confidence = scores[selected]

        return RoutingDecision(
            selected_matcher=selected,
            selected_representation=representation_route.representation,
            representation_band=representation_route.band,
            representation_reason=representation_route.reason,
            difficulty=difficulty,
            confidence=confidence,
            reason=(
                f"{difficulty} pair; "
                f"{selected} currently has the highest "
                f"estimated utility."
            ),
            candidate_scores=scores,
        )
