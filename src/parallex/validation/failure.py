def explain_failure(**kwargs):
    reasons = []

    if kwargs.get("overlaps") is False:
        reasons.append("no spatial overlap")
    if kwargs.get("matches", 0) < 4:
        reasons.append("too few correspondences")
    if kwargs.get("inliers", 0) < 10:
        reasons.append("too few geometric inliers")
    if kwargs.get("inlier_ratio", 1) < 0.20:
        reasons.append("low inlier ratio")
    if kwargs.get("coverage_ratio", 1) < 0.20:
        reasons.append("poor spatial coverage")
    if kwargs.get("rmse_px", 0) > 3:
        reasons.append("large reprojection error")

    return reasons or ["no failure condition triggered"]
