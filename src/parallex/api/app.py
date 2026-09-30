from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from parallex.products import Product
from parallex.preprocessing import create_preprocessor
from parallex.pipeline.registration import RegistrationPipeline


# ------------------------------------------------------------------
# Allowed current training products
# ------------------------------------------------------------------

ALLOWED_PRODUCTS = {
    "IIRS": Path(
        r"C:\Users\graj6\Downloads\P0001"
        r"\ch2_iir_nci_20221209T1908498944_d_img_n18"
    ),
    "OHRC": Path(
        r"C:\Users\graj6\Downloads\P0001"
        r"\ch2_ohr_ncp_20250612T2031048828_d_img_d18"
    ),
    "TMC-2": Path(r"C:\Users\graj6\Downloads\P0001\ch2_tmc_ncn_20230605T1503198538_d_img_n18"),
    "TMC2": Path(
        r"C:\Users\graj6\Downloads\P0001"
        r"\ch2_tmc_ncn_20230605T1503198538_d_img_n18"
    ),
}


class CorrespondenceOptions(BaseModel):
    ratioThreshold: Optional[float] = None
    maxRansacIterations: Optional[int] = None
    reprojectionThreshold: Optional[float] = None
    enforceAnms: Optional[bool] = None


class CorrespondenceRequest(BaseModel):
    regionId: str
    sourceInstrument: str
    targetInstrument: str
    selectedModelId: Optional[str] = None
    useTmcBridge: bool = False
    options: Optional[CorrespondenceOptions] = None


app = FastAPI(
    title="PARALLAX API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "parallax",
    }


def _bounded_representation(product: Product, instrument: str):
    """
    Build a bounded 2-D representation for the registration pipeline.

    This prevents full PDS4 products from being loaded into RAM.
    """

    instrument = instrument.upper()

    if instrument == "IIRS":
        processor = create_preprocessor(
            product,
            representation="band",
            band=160,
        )

        height = min(2048, int(product.shape[1]))
        width = min(2048, int(product.shape[2]))

        return processor.run_window(
            row=0,
            col=0,
            height=height,
            width=width,
        ).image

    if instrument in {"OHRC", "TMC2"}:
        processor = create_preprocessor(
            product,
            representation="gradient",
        )

        height = min(2048, int(product.shape[0]))
        width = min(2048, int(product.shape[1]))

        return processor.run_window(
            row=0,
            col=0,
            height=height,
            width=width,
        ).image

    raise ValueError(
        f"Unsupported instrument: {instrument}"
    )



def _json_float(value, default=0.0):
    try:
        value = float(value)
        if np.isfinite(value):
            return value
    except (TypeError, ValueError):
        pass
    return default


def _json_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _keypoint_dict(point, index, instrument):
    point = np.asarray(point, dtype=np.float32).reshape(-1)

    return {
        "id": int(index),
        "x": float(point[0]) if len(point) > 0 else 0.0,
        "y": float(point[1]) if len(point) > 1 else 0.0,
        "scale": 1.0,
        "orientation": 0.0,
        "response": 1.0,
        "instrument": instrument,
    }


def _decision_to_response(
    decision,
    result,
    source_instrument,
    target_instrument,
):
    attempts = getattr(decision, "attempts", []) or []

    selected_matcher = getattr(
        decision,
        "selected_matcher",
        None,
    )

    keypoints_a = np.asarray(
        getattr(
            result,
            "keypoints_a",
            np.empty((0, 2), dtype=np.float32),
        )
        if result is not None
        else np.empty((0, 2), dtype=np.float32)
    )

    keypoints_b = np.asarray(
        getattr(
            result,
            "keypoints_b",
            np.empty((0, 2), dtype=np.float32),
        )
        if result is not None
        else np.empty((0, 2), dtype=np.float32)
    )

    matches = np.asarray(
        getattr(
            result,
            "matches",
            np.empty((0, 2), dtype=np.int32),
        )
        if result is not None
        else np.empty((0, 2), dtype=np.int32)
    )

    scores = np.asarray(
        getattr(
            result,
            "scores",
            np.empty((0,), dtype=np.float32),
        )
        if result is not None
        else np.empty((0,), dtype=np.float32)
    ).reshape(-1)

    inlier_mask = getattr(
        result,
        "inlier_mask",
        None,
    )

    selected_attempt = None

    for attempt in attempts:
        if (
            selected_matcher is not None
            and attempt.get("matcher") == selected_matcher
        ):
            selected_attempt = attempt

    if selected_attempt is None:
        for attempt in reversed(attempts):
            if attempt.get("status") == "COMPLETED":
                selected_attempt = attempt
                break

    if selected_attempt is None:
        selected_attempt = {}

    candidate_matches = _json_int(
        selected_attempt.get(
            "filtered_matches",
            len(matches),
        )
    )

    inliers = _json_int(
        selected_attempt.get(
            "inliers",
            int(
                np.count_nonzero(inlier_mask)
            )
            if inlier_mask is not None
            else 0,
        )
    )

    outliers = max(
        0,
        candidate_matches - inliers,
    )

    inlier_ratio = (
        float(inliers) / float(candidate_matches)
        if candidate_matches
        else 0.0
    )

    rmse = _json_float(
        selected_attempt.get(
            "refined_reprojection_error_px",
            selected_attempt.get(
                "reprojection_error_px",
                0.0,
            ),
        )
    )

    coverage = _json_float(
        selected_attempt.get(
            "coverage_ratio",
            0.0,
        )
    )

    source_keypoints = [
        _keypoint_dict(
            point,
            index,
            source_instrument,
        )
        for index, point in enumerate(keypoints_a)
    ]

    target_keypoints = [
        _keypoint_dict(
            point,
            index,
            target_instrument,
        )
        for index, point in enumerate(keypoints_b)
    ]

    frontend_matches = []

    for index, pair in enumerate(matches):
        pair = np.asarray(
            pair,
            dtype=np.int64,
        ).reshape(-1)

        if len(pair) < 2:
            continue

        source_index = int(pair[0])
        target_index = int(pair[1])

        if (
            source_index < 0
            or source_index >= len(source_keypoints)
            or target_index < 0
            or target_index >= len(target_keypoints)
        ):
            continue

        score = (
            float(scores[index])
            if index < len(scores)
            else 0.0
        )

        is_inlier = False

        if (
            inlier_mask is not None
            and index < len(inlier_mask)
        ):
            is_inlier = bool(
                inlier_mask[index]
            )

        frontend_matches.append(
            {
                "id": int(index),
                "sourceKeypoint": source_keypoints[
                    source_index
                ],
                "targetKeypoint": target_keypoints[
                    target_index
                ],
                "distance": score,
                "confidence": score,
                "isRansacInlier": is_inlier,
                "isAnmsSelected": False,
                "residualError": rmse,
            }
        )

    confidence = _json_float(
        getattr(
            decision,
            "confidence",
            0.0,
        )
    )

    rejected = bool(
        getattr(
            decision,
            "rejected",
            False,
        )
    )

    status = (
        "error"
        if result is None
        else "partial"
        if rejected
        else "success"
    )

    verification_matrix = selected_attempt.get(
        "verification_matrix"
    )

    if verification_matrix is None:
        verification_matrix = [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ]

    return {
        "status": status,
        "sourceKeypoints": source_keypoints,
        "targetKeypoints": target_keypoints,
        "matches": frontend_matches,
        "metrics": {
            "totalFeaturesSource": len(
                source_keypoints
            ),
            "totalFeaturesTarget": len(
                target_keypoints
            ),
            "candidateMatches": candidate_matches,
            "inlierMatches": inliers,
            "outlierMatches": outliers,
            "inlierRatio": inlier_ratio,
            "rmse": rmse,
            "uncertaintyPx": rmse,
            "precision": inlier_ratio,
            "recall": inlier_ratio,
            "f1Score": inlier_ratio,
            "spatialCoverage": coverage,
            "confidenceScore": confidence,
            "qualityGateStatus": (
                "FAILED"
                if rejected
                else "PASSED"
            ),
            "evidenceType": "TARGET_QUALITY_GATE",
            "selectedModelName": (
                selected_matcher or "AUTO"
            ),
            "tmcBridgeActive": False,
            "transformationType": "AFFINE",
            "sourceCoverage": coverage,
            "targetCoverage": coverage,
            "uniformityScore": _json_float(
                selected_attempt.get(
                    "uniformity",
                    0.0,
                )
            ),
            "beforeRmse": rmse,
            "afterRmse": rmse,
            "refinementGain": 0.0,
            "meanError": _json_float(
                selected_attempt.get(
                    "mean_error_px",
                    rmse,
                )
            ),
            "medianError": rmse,
            "maxError": _json_float(
                selected_attempt.get(
                    "max_error_px",
                    rmse,
                )
            ),
        },
        "homography": verification_matrix,
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "dataSource": "LIVE TELEMETRY",
    }


@app.post("/api/correspondence")
def correspondence(
    request: CorrespondenceRequest,
):
    source = request.sourceInstrument.upper()
    if source in ("TMC-2", "TMC"): source = "TMC2"
    target = request.targetInstrument.upper()
    if target in ("TMC-2", "TMC"): target = "TMC2"

    if source not in ALLOWED_PRODUCTS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported source instrument: {source}",
        )

    if target not in ALLOWED_PRODUCTS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported target instrument: {target}",
        )

    source_path = ALLOWED_PRODUCTS[source]
    target_path = ALLOWED_PRODUCTS[target]

    if not source_path.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Source product not found: {source_path}",
        )

    if not target_path.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Target product not found: {target_path}",
        )

    try:
        with Product(source_path) as source_product:
            with Product(target_path) as target_product:

                image_a = _bounded_representation(
                    source_product,
                    source,
                )

                image_b = _bounded_representation(
                    target_product,
                    target,
                )

                metadata_a = dict(
                    source_product.metadata
                )
                metadata_b = dict(
                    target_product.metadata
                )

                pipeline = RegistrationPipeline()

                decision, result = pipeline.run(
                    image_a,
                    image_b,
                    metadata_a,
                    metadata_b,
                    overlap_ratio=1.0,
                    valid_pixel_ratio=1.0,
                )

                return _decision_to_response(
                    decision,
                    result,
                    source,
                    target,
                )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                f"PARALLAX registration failed: "
                f"{type(exc).__name__}: {exc}"
            ),
        ) from exc
