import cv2
import numpy as np

from parallex.matching.base import MatchResult


def verify_homography(
    result: MatchResult,
    reprojection_threshold: float = 3.0,
    confidence: float = 0.995,
    max_iterations: int = 5000,
):
    """
    Robustly verify correspondences using RANSAC homography.

    This is a baseline verifier. It must NOT be interpreted as a
    universal lunar-terrain model; non-planar terrain may require
    terrain-aware geometry later.
    """

    if len(result.matches) < 4:
        result.inlier_mask = np.zeros(
            len(result.matches),
            dtype=bool,
        )

        result.metadata["verification"] = "insufficient_matches"

        return result, None

    points_a = np.asarray(
        result.keypoints_a[result.matches[:, 0]],
        dtype=np.float32,
    )

    points_b = np.asarray(
        result.keypoints_b[result.matches[:, 1]],
        dtype=np.float32,
    )

    matrix, mask = cv2.findHomography(
        points_a,
        points_b,
        method=cv2.RANSAC,
        ransacReprojThreshold=float(reprojection_threshold),
        maxIters=int(max_iterations),
        confidence=float(confidence),
    )

    if mask is None:
        inlier_mask = np.zeros(
            len(result.matches),
            dtype=bool,
        )
    else:
        inlier_mask = mask.ravel().astype(bool)

    result.inlier_mask = inlier_mask

    result.metadata.update({
        "verification": "RANSAC_HOMOGRAPHY",
        "reprojection_threshold": float(reprojection_threshold),
        "ransac_confidence": float(confidence),
        "max_iterations": int(max_iterations),
    })

    return result, matrix


def reprojection_errors(result: MatchResult, matrix):
    """
    Calculate per-match reprojection error for a verified homography.
    """
    if matrix is None or len(result.matches) == 0:
        return np.empty(
            (0,),
            dtype=np.float32,
        )

    points_a = np.asarray(
        result.keypoints_a[result.matches[:, 0]],
        dtype=np.float32,
    )

    points_b = np.asarray(
        result.keypoints_b[result.matches[:, 1]],
        dtype=np.float32,
    )

    projected = cv2.perspectiveTransform(
        points_a.reshape(-1, 1, 2),
        matrix,
    ).reshape(-1, 2)

    errors = np.linalg.norm(
        projected - points_b,
        axis=1,
    )

    return errors.astype(np.float32)
