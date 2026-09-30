from dataclasses import dataclass
import numpy as np
import cv2


@dataclass
class VerificationResult:
    model_name: str
    inlier_mask: np.ndarray
    num_matches: int
    num_inliers: int
    inlier_ratio: float
    reprojection_error: float
    success: bool
    matrix: np.ndarray | None = None


def verify_matches(
    keypoints_a,
    keypoints_b,
    matches,
    model="affine",
    threshold=3.0,
    confidence=0.995,
    max_iterations=5000,
):
    matches = np.asarray(matches)

    if len(matches) < 3:
        return VerificationResult(
            model_name=model,
            inlier_mask=np.zeros(len(matches), dtype=bool),
            num_matches=len(matches),
            num_inliers=0,
            inlier_ratio=0.0,
            reprojection_error=float("inf"),
            success=False,
            matrix=None,
        )

    pts_a = np.asarray(keypoints_a)[matches[:, 0]].astype(np.float32)
    pts_b = np.asarray(keypoints_b)[matches[:, 1]].astype(np.float32)

    if model == "affine":
        matrix, mask = cv2.estimateAffinePartial2D(
            pts_a,
            pts_b,
            method=cv2.RANSAC,
            ransacReprojThreshold=threshold,
            maxIters=max_iterations,
            confidence=confidence,
        )
    elif model == "homography":
        matrix, mask = cv2.findHomography(
            pts_a,
            pts_b,
            cv2.RANSAC,
            threshold,
            maxIters=max_iterations,
            confidence=confidence,
        )
    else:
        raise ValueError(f"Unsupported model: {model}")

    if matrix is None or mask is None:
        return VerificationResult(
            model_name=model,
            inlier_mask=np.zeros(len(matches), dtype=bool),
            num_matches=len(matches),
            num_inliers=0,
            inlier_ratio=0.0,
            reprojection_error=float("inf"),
            success=False,
            matrix=None,
        )

    inlier_mask = mask.ravel().astype(bool)

    if model == "affine":
        projected = cv2.transform(
            pts_a.reshape(-1, 1, 2),
            matrix,
        ).reshape(-1, 2)
    else:
        homogeneous = np.column_stack(
            [pts_a, np.ones(len(pts_a))]
        )
        projected_h = homogeneous @ matrix.T
        projected = (
            projected_h[:, :2]
            / projected_h[:, 2:3]
        )

    errors = np.linalg.norm(projected - pts_b, axis=1)
    inlier_errors = errors[inlier_mask]

    reprojection_error = (
        float(np.mean(inlier_errors))
        if len(inlier_errors)
        else float("inf")
    )

    num_inliers = int(inlier_mask.sum())

    return VerificationResult(
        model_name=model,
        inlier_mask=inlier_mask,
        num_matches=len(matches),
        num_inliers=num_inliers,
        inlier_ratio=num_inliers / len(matches),
        reprojection_error=reprojection_error,
        success=num_inliers >= 3,
        matrix=matrix,
    )
