from __future__ import annotations
from parallex.routing.representation_router import RepresentationRouter
from typing import Any

import numpy as np

from parallex.characterization.pair import characterize_pair
from parallex.characterization.features import characterization_to_features
from parallex.validation.observability import observability_gate
from parallex.routing.engine import RoutingEngine
from parallex.validation.confidence import filter_matches_by_confidence
from parallex.verification.geometric import verify_matches
from parallex.spatial.coverage import grid_coverage
from parallex.refinement.subpixel import refine_points
from parallex.validation.metrics import registration_metrics
from parallex.validation.quality import quality_decision


class RegistrationDecision:
    def __init__(self):
        self.selected_matcher = None
        self.difficulty = None
        self.confidence = 0.0
        self.reason = ""
        self.candidate_scores = {}
        self.rejected = False
        self.rejection_reason = ""
        self.attempts = []
        self.quality = None
        self.result = None
        self.metrics = None

    def __repr__(self):
        return (
            f"RegistrationDecision("
            f"selected_matcher={self.selected_matcher!r}, "
            f"confidence={self.confidence:.3f}, "
            f"rejected={self.rejected})"
        )

    def to_result(self):
        """Return the stable public registration result."""
        return RegistrationResult(
            self,
            self.result,
        )


class RegistrationResult:
    """Stable, serializable registration result for API/frontend use."""

    def __init__(self, decision, result=None):
        self.selected_matcher = decision.selected_matcher
        self.difficulty = decision.difficulty
        self.confidence = float(decision.confidence)
        self.reason = decision.reason
        self.rejected = bool(decision.rejected)
        self.rejection_reason = decision.rejection_reason
        self.quality = decision.quality
        self.metrics = decision.metrics
        self.result = result
        self.attempts = decision.attempts

    def to_dict(self):
        def serialize(value):
            if value is None:
                return None

            if isinstance(value, np.ndarray):
                return value.tolist()

            if isinstance(value, (np.integer,)):
                return int(value)

            if isinstance(value, (np.floating,)):
                return float(value)

            if isinstance(value, (np.bool_,)):
                return bool(value)

            if isinstance(value, dict):
                return {
                    str(k): serialize(v)
                    for k, v in value.items()
                }

            if isinstance(value, (list, tuple)):
                return [serialize(v) for v in value]

            if hasattr(value, "__dict__"):
                return {
                    str(k): serialize(v)
                    for k, v in vars(value).items()
                    if not k.startswith("_")
                }

            return value

        return serialize({
            "selected_matcher": self.selected_matcher,
            "difficulty": self.difficulty,
            "confidence": self.confidence,
            "reason": self.reason,
            "rejected": self.rejected,
            "rejection_reason": self.rejection_reason,
            "quality": self.quality,
            "metrics": self.metrics,
            "attempts": self.attempts,
        })


class RegistrationPipeline:
    def __init__(self, router=None, engine=None):
        self.representation_router = RepresentationRouter()
        self.engine = engine or RoutingEngine()

        if router is not None:
            self.engine.router = router

    @staticmethod
    def _extract_points(match_result: Any):
        """
        Convert matcher output into actual coordinate arrays.

        Supported formats:

        Index-based:
            matches.shape == (N, 2)
            matches[:, 0] indexes keypoints_a
            matches[:, 1] indexes keypoints_b

        Direct coordinates:
            matches.shape == (N, 4)
            [x_a, y_a, x_b, y_b]
        """

        matches = np.asarray(
            getattr(match_result, "matches", None)
        )

        keypoints_a = np.asarray(
            getattr(match_result, "keypoints_a", None)
        )

        keypoints_b = np.asarray(
            getattr(match_result, "keypoints_b", None)
        )

        if matches.size == 0:
            return (
                np.empty((0, 2), dtype=np.float32),
                np.empty((0, 2), dtype=np.float32),
            )

        if matches.ndim != 2:
            raise ValueError(
                f"Unsupported match coordinate shape: {matches.shape}"
            )

        if matches.shape[1] == 2:

            if (
                keypoints_a.ndim != 2
                or keypoints_a.shape[1] != 2
                or keypoints_b.ndim != 2
                or keypoints_b.shape[1] != 2
            ):
                raise ValueError(
                    "Index-based matches require keypoints_a and "
                    "keypoints_b with shape (N, 2). "
                    f"Got keypoints_a={keypoints_a.shape}, "
                    f"keypoints_b={keypoints_b.shape}."
                )

            indices_a = matches[:, 0].astype(np.int64)
            indices_b = matches[:, 1].astype(np.int64)

            valid = (
                (indices_a >= 0)
                & (indices_a < len(keypoints_a))
                & (indices_b >= 0)
                & (indices_b < len(keypoints_b))
            )

            if not np.all(valid):
                invalid_count = int((~valid).sum())
                raise ValueError(
                    f"Match indices contain {invalid_count} invalid "
                    f"keypoint references."
                )

            points_a = keypoints_a[indices_a]
            points_b = keypoints_b[indices_b]

            return (
                np.asarray(points_a, dtype=np.float32),
                np.asarray(points_b, dtype=np.float32),
            )

        if matches.shape[1] == 4:

            points_a = matches[:, 0:2]
            points_b = matches[:, 2:4]

            return (
                np.asarray(points_a, dtype=np.float32),
                np.asarray(points_b, dtype=np.float32),
            )

        raise ValueError(
            f"Unsupported match coordinate shape: {matches.shape}"
        )

    @staticmethod
    def _build_filtered_match_result(result, filtered_matches):
        """
        Create a lightweight matcher-result object containing:

        - original keypoints
        - confidence-filtered match indices
        - confidence-filtered scores

        This keeps the representation expected by verify_matches().
        """

        class FilteredMatchResult:
            pass

        filtered = FilteredMatchResult()

        filtered.keypoints_a = np.asarray(
            getattr(
                result,
                "keypoints_a",
                np.empty((0, 2), dtype=np.float32),
            )
        )

        filtered.keypoints_b = np.asarray(
            getattr(
                result,
                "keypoints_b",
                np.empty((0, 2), dtype=np.float32),
            )
        )

        filtered.matches = np.asarray(
            filtered_matches.matches
        )

        filtered.scores = np.asarray(
            filtered_matches.scores,
            dtype=np.float32,
        )

        return filtered

    def run(
        self,
        image_a,
        image_b,
        metadata_a,
        metadata_b,
        *,
        overlap_ratio=1.0,
        valid_pixel_ratio=1.0,
    ):
        decision = RegistrationDecision()

        # =========================================================
        # 1. PAIR CHARACTERIZATION
        # =========================================================
        characterization = characterize_pair(
            image_a,
            image_b,
            metadata_a,
            metadata_b,
            overlap_ratio=overlap_ratio,
        )

        features = characterization_to_features(
            characterization,
            metadata_a,
            metadata_b,
            overlap_ratio=overlap_ratio,
            image_shape_a=image_a.shape,
            image_shape_b=image_b.shape,
        )

        features.valid_pixel_ratio = float(
            valid_pixel_ratio
        )

        # =========================================================
        # 2. OBSERVABILITY GATE
        # =========================================================
        observability = observability_gate(
            overlap_ratio=overlap_ratio,
            valid_pixel_ratio=valid_pixel_ratio,
            texture_score=characterization.texture_score,
            geometric_valid=True,
        )

        if not observability.observable:
            decision.rejected = True
            decision.rejection_reason = str(
                getattr(
                    observability,
                    "reason",
                    "pair not observable",
                )
            )
            decision.reason = decision.rejection_reason
            return decision, None

        # =========================================================
        # 3. ADAPTIVE ROUTING
        # =========================================================
        routing, candidates = self.engine.route_candidates(
            features
        )

        # Select the preprocessing representation independently of the
        # existing matcher candidate routing.
        representation_features = {
            key: value
            for key, value in vars(features).items()
        }

        representation_route = self.representation_router.route(
            representation_features
        )

        decision.selected_representation = (
            representation_route.representation
        )
        decision.representation_band = (
            representation_route.band
        )
        decision.representation_reason = (
            representation_route.reason
        )

        decision.difficulty = routing.difficulty
        decision.confidence = float(
            routing.confidence
        )
        decision.candidate_scores = dict(
            routing.candidate_scores
        )

        if routing.rejected:
            decision.rejected = True
            decision.rejection_reason = str(
                routing.rejection_reason
            )
            decision.reason = decision.rejection_reason
            return decision, None

        # =========================================================
        # 4. REPRESENTATION PREPROCESSING
        # =========================================================
        matcher_image_a = image_a
        matcher_image_b = image_b

        try:
            from parallex.preprocessing import create_preprocessor

            sensor_a = str(
                metadata_a.get("sensor", "")
            ).upper()
            sensor_b = str(
                metadata_b.get("sensor", "")
            ).upper()

            # Only apply the selected representation when the supplied
            # inputs are Product objects. Existing ndarray workflows
            # remain unchanged.
            if hasattr(image_a, "read_window") and hasattr(
                image_b, "read_window"
            ):
                processor_a = create_preprocessor(
                    image_a,
                    representation=(
                        decision.selected_representation
                    ),
                    band=decision.representation_band,
                )

                processor_b = create_preprocessor(
                    image_b,
                    representation=(
                        decision.selected_representation
                    ),
                    band=decision.representation_band,
                )

                # Keep preprocessing bounded for large PDS4 products.
                # Registration inputs are already expected to represent
                # the working ROI/tile.
                def _process_product_window(processor, product):
                    shape = product.shape

                    if len(shape) == 3:
                        height = min(2048, int(shape[1]))
                        width = min(2048, int(shape[2]))
                    else:
                        height = min(2048, int(shape[0]))
                        width = min(2048, int(shape[1]))

                    return processor.run_window(
                        row=0,
                        col=0,
                        height=height,
                        width=width,
                    ).image

                matcher_image_a = _process_product_window(
                    processor_a,
                    image_a,
                )

                matcher_image_b = _process_product_window(
                    processor_b,
                    image_b,
                )

        except (AttributeError, TypeError, ValueError):
            # Preserve the existing ndarray registration path.
            matcher_image_a = image_a
            matcher_image_b = image_b

        # =========================================================
        # 5. MATCHER LOOP
        # =========================================================
        best = None

        for matcher_name in candidates:

            attempt = {
                "matcher": matcher_name,
                "status": "STARTED",
            }

            try:

                # -------------------------------------------------
                # Run matcher
                # -------------------------------------------------
                result = self.engine.run_matcher(
                    matcher_name,
                    matcher_image_a,
                    matcher_image_b,
                )

                if result is None:
                    attempt["status"] = "FAILED"
                    attempt["reason"] = (
                        "matcher returned None"
                    )
                    decision.attempts.append(attempt)
                    continue

                raw_matches = np.asarray(
                    getattr(
                        result,
                        "matches",
                        np.empty(
                            (0, 2),
                            dtype=np.int32,
                        ),
                    )
                )

                raw_scores = np.asarray(
                    getattr(
                        result,
                        "scores",
                        np.empty(
                            (0,),
                            dtype=np.float32,
                        ),
                    ),
                    dtype=np.float32,
                ).reshape(-1)

                attempt["raw_matches"] = int(
                    len(raw_matches)
                )

                # -------------------------------------------------
                # Confidence filtering
                # -------------------------------------------------
                confidence_result = (
                    filter_matches_by_confidence(
                        raw_matches,
                        raw_scores,
                        percentile=50,
                        min_matches=4,
                    )
                )

                attempt["filtered_matches"] = int(
                    len(confidence_result.matches)
                )

                attempt["confidence_threshold"] = float(
                    confidence_result.threshold
                )

                attempt["retained_ratio"] = float(
                    confidence_result.retained_ratio
                )

                if len(confidence_result.matches) < 4:
                    attempt["status"] = "FAILED"
                    attempt["reason"] = (
                        "fewer than 4 matches after "
                        "confidence filtering"
                    )
                    decision.attempts.append(attempt)
                    continue

                # -------------------------------------------------
                # Preserve matcher representation
                # -------------------------------------------------
                filtered_result = (
                    self._build_filtered_match_result(
                        result,
                        confidence_result,
                    )
                )

                # -------------------------------------------------
                # Extract actual coordinates for later stages
                # -------------------------------------------------
                points_a, points_b = self._extract_points(
                    filtered_result
                )

                attempt["coordinate_points"] = int(
                    len(points_a)
                )

                if len(points_a) < 4:
                    attempt["status"] = "FAILED"
                    attempt["reason"] = (
                        "fewer than 4 coordinate "
                        "correspondences"
                    )
                    decision.attempts.append(attempt)
                    continue

                # -------------------------------------------------
                # Robust geometric verification
                #
                # IMPORTANT:
                # verify_matches expects:
                #   keypoints_a
                #   keypoints_b
                #   matches
                #
                # NOT already-extracted coordinates.
                # -------------------------------------------------
                verification = verify_matches(
                    filtered_result.keypoints_a,
                    filtered_result.keypoints_b,
                    filtered_result.matches,
                    model="affine",
                )

                attempt["inliers"] = int(
                    verification.num_inliers
                )

                attempt["inlier_ratio"] = float(
                    verification.inlier_ratio
                )

                attempt["reprojection_error_px"] = float(
                    verification.reprojection_error
                )

                attempt["verification_success"] = bool(
                    verification.success
                )

                # Preserve the actual verified geometric transform
                # and inlier mask for downstream API/reporting layers.
                attempt["verification_matrix"] = (
                    verification.matrix.tolist()
                    if verification.matrix is not None
                    else None
                )

                attempt["verification_inlier_mask"] = (
                    np.asarray(
                        verification.inlier_mask,
                        dtype=bool,
                    ).tolist()
                    if verification.inlier_mask is not None
                    else None
                )

                if not verification.success:
                    attempt["status"] = "FAILED"
                    attempt["reason"] = (
                        "geometric verification failed"
                    )
                    decision.attempts.append(attempt)
                    continue

                # -------------------------------------------------
                # RANSAC inlier mask corresponds to filtered matches
                # -------------------------------------------------
                inlier_mask = np.asarray(
                    verification.inlier_mask,
                    dtype=bool,
                ).reshape(-1)

                if len(inlier_mask) != len(points_a):
                    attempt["status"] = "FAILED"
                    attempt["reason"] = (
                        "inlier mask length does not match "
                        "filtered correspondence count"
                    )
                    decision.attempts.append(attempt)
                    continue

                verified_a = points_a[inlier_mask]
                verified_b = points_b[inlier_mask]

                if len(verified_a) < 3:
                    attempt["status"] = "FAILED"
                    attempt["reason"] = (
                        "fewer than 3 geometric inliers"
                    )
                    decision.attempts.append(attempt)
                    continue

                # -------------------------------------------------
                # Spatial coverage
                # -------------------------------------------------
                coverage_a = grid_coverage(
                    verified_a,
                    image_a.shape,
                )

                coverage_b = grid_coverage(
                    verified_b,
                    image_b.shape,
                )

                coverage_ratio = float(
                    min(
                        coverage_a.coverage_ratio,
                        coverage_b.coverage_ratio,
                    )
                )

                uniformity = float(
                    min(
                        coverage_a.uniformity,
                        coverage_b.uniformity,
                    )
                )

                attempt["coverage_ratio"] = (
                    coverage_ratio
                )

                attempt["coverage_source"] = float(
                    coverage_a.coverage_ratio
                )

                attempt["coverage_target"] = float(
                    coverage_b.coverage_ratio
                )

                attempt["uniformity"] = uniformity

                # -------------------------------------------------
                # Sub-pixel refinement
                # -------------------------------------------------
                refinement_a = refine_points(
                    image_a,
                    verified_a,
                )

                refinement_b = refine_points(
                    image_b,
                    verified_b,
                )

                refined_a = np.asarray(
                    refinement_a.points,
                    dtype=np.float32,
                )

                refined_b = np.asarray(
                    refinement_b.points,
                    dtype=np.float32,
                )

                refinement_success = bool(
                    refinement_a.success_ratio > 0
                    and refinement_b.success_ratio > 0
                    and len(refined_a)
                    == len(refined_b)
                )

                attempt["refinement_success"] = (
                    refinement_success
                )

                attempt["refinement_success_ratio_a"] = (
                    float(
                        refinement_a.success_ratio
                    )
                )

                attempt["refinement_success_ratio_b"] = (
                    float(
                        refinement_b.success_ratio
                    )
                )

                attempt["mean_subpixel_shift_a"] = (
                    float(
                        refinement_a.mean_shift
                    )
                )

                attempt["mean_subpixel_shift_b"] = (
                    float(
                        refinement_b.mean_shift
                    )
                )

                # -------------------------------------------------
                # Refined reprojection error
                # -------------------------------------------------
                refined_rmse = float(
                    verification.reprojection_error
                )

                if (
                    refinement_success
                    and verification.matrix is not None
                    and len(refined_a) >= 3
                ):

                    matrix = np.asarray(
                        verification.matrix,
                        dtype=np.float64,
                    )

                    homogeneous = np.concatenate(
                        [
                            refined_a.astype(
                                np.float64
                            ),
                            np.ones(
                                (
                                    len(refined_a),
                                    1,
                                ),
                                dtype=np.float64,
                            ),
                        ],
                        axis=1,
                    )

                    projected = (
                        homogeneous @ matrix.T
                    )

                    if projected.shape[1] == 3:

                        denom = projected[:, 2:3]

                        denom[
                            np.abs(denom) < 1e-12
                        ] = 1e-12

                        projected_xy = (
                            projected[:, :2]
                            / denom
                        )

                    else:
                        projected_xy = (
                            projected[:, :2]
                        )

                    errors = (
                        projected_xy
                        - refined_b.astype(
                            np.float64
                        )
                    )

                    refined_rmse = float(
                        np.sqrt(
                            np.mean(
                                np.sum(
                                    errors * errors,
                                    axis=1,
                                )
                            )
                        )
                    )

                attempt[
                    "refined_reprojection_error_px"
                ] = refined_rmse

                # -------------------------------------------------
                # Registration metrics
                # -------------------------------------------------
                metrics = registration_metrics(
                    refined_a,
                    refined_b,
                    verification.matrix,
                    total_matches=int(
                        len(confidence_result.matches)
                    ),
                )

                attempt["metrics"] = metrics

                attempt["rmse_px"] = float(
                    getattr(
                        metrics,
                        "rmse_px",
                        refined_rmse,
                    )
                )

                attempt["mean_error_px"] = float(
                    getattr(
                        metrics,
                        "mean_error_px",
                        refined_rmse,
                    )
                )

                attempt["max_error_px"] = float(
                    getattr(
                        metrics,
                        "max_error_px",
                        refined_rmse,
                    )
                )

                # -------------------------------------------------
                # Final quality model
                # -------------------------------------------------
                quality = quality_decision(
                    rmse_px=refined_rmse,
                    inlier_count=int(
                        verification.num_inliers
                    ),
                    inlier_ratio=float(
                        verification.inlier_ratio
                    ),
                    coverage_ratio=coverage_ratio,
                    uniformity=uniformity,
                    confidence=float(
                        decision.confidence
                    ),
                )

                quality_score = float(
                    getattr(
                        quality,
                        "score",
                        0.0,
                    )
                )

                quality_label = getattr(
                    quality,
                    "decision",
                    getattr(
                        quality,
                        "label",
                        "REJECT",
                    ),
                )

                quality_reasons = list(
                    getattr(
                        quality,
                        "reasons",
                        [],
                    )
                )

                attempt["quality_score"] = (
                    quality_score
                )

                attempt["quality_decision"] = (
                    quality_label
                )

                attempt["quality_reasons"] = (
                    quality_reasons
                )

                attempt["status"] = "COMPLETED"

                candidate = {
                    "matcher": matcher_name,
                    "result": result,
                    "verification": verification,
                    "metrics": metrics,
                    "quality": quality,
                    "quality_score": quality_score,
                    "rmse": refined_rmse,
                    "coverage": coverage_ratio,
                    "inliers": int(
                        verification.num_inliers
                    ),
                }

                if (
                    best is None
                    or candidate["quality_score"]
                    > best["quality_score"]
                ):
                    best = candidate

                decision.attempts.append(
                    attempt
                )

                # -------------------------------------------------
                # Early acceptance
                # -------------------------------------------------
                if (
                    str(quality_label).upper()
                    == "ACCEPT"
                ):

                    decision.selected_matcher = (
                        matcher_name
                    )

                    decision.quality = quality
                    decision.result = result

                    decision.reason = (
                        f"{matcher_name} accepted by "
                        "final quality model"
                    )

                    return decision, result

            except MemoryError as exc:

                attempt["status"] = "SKIPPED"
                attempt["reason"] = (
                    f"memory error: {exc}"
                )

                decision.attempts.append(
                    attempt
                )

            except RuntimeError as exc:

                attempt["status"] = "SKIPPED"
                attempt["reason"] = (
                    f"runtime error: {exc}"
                )

                decision.attempts.append(
                    attempt
                )

            except Exception as exc:

                attempt["status"] = "FAILED"
                attempt["reason"] = (
                    f"{type(exc).__name__}: {exc}"
                )

                decision.attempts.append(
                    attempt
                )

        # =========================================================
        # 5. BEST COMPLETED FALLBACK
        # =========================================================
        if best is not None:

            decision.selected_matcher = (
                best["matcher"]
            )

            decision.quality = best["quality"]
            decision.result = best["result"]

            decision.reason = (
                "No matcher satisfied the strict "
                "acceptance criteria; returning the "
                "best completed candidate."
            )

            quality_label = getattr(
                best["quality"],
                "decision",
                getattr(
                    best["quality"],
                    "label",
                    "REJECT",
                ),
            )

            if (
                str(quality_label).upper()
                == "REJECT"
            ):

                decision.rejected = True

                decision.rejection_reason = (
                    "Best completed registration did not "
                    "satisfy final quality criteria."
                )

            return decision, best["result"]

        # =========================================================
        # 6. COMPLETE FAILURE
        # =========================================================
        decision.rejected = True

        decision.rejection_reason = (
            "All candidate matchers failed or were skipped."
        )

        decision.reason = (
            decision.rejection_reason
        )

        return decision, None
