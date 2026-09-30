from __future__ import annotations
import numpy as np
import cv2

def reprojection_errors(source_points, target_points, matrix):
    src = np.asarray(source_points, dtype=np.float32).reshape(-1, 1, 2)
    dst = np.asarray(target_points, dtype=np.float32).reshape(-1, 1, 2)

    if len(src) == 0:
        return np.empty(0, dtype=np.float32)

    pred = cv2.perspectiveTransform(
        src, np.asarray(matrix, dtype=np.float32)
    )
    return np.linalg.norm(pred - dst, axis=2).ravel()

def registration_metrics(source_points, target_points, matrix, total_matches=None):
    errors = reprojection_errors(source_points, target_points, matrix)
    n = len(errors)

    if n == 0:
        return {
            "rmse_px": float("inf"),
            "mean_error_px": float("inf"),
            "median_error_px": float("inf"),
            "max_error_px": float("inf"),
            "inlier_count": 0,
            "inlier_ratio": 0.0,
        }

    return {
        "rmse_px": float(np.sqrt(np.mean(errors ** 2))),
        "mean_error_px": float(np.mean(errors)),
        "median_error_px": float(np.median(errors)),
        "max_error_px": float(np.max(errors)),
        "inlier_count": int(n),
        "inlier_ratio": float(
            n / max(1, total_matches if total_matches is not None else n)
        ),
    }
