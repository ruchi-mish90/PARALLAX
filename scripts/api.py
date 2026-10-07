from __future__ import annotations

import sys
import tempfile
import time
from pathlib import Path

import cv2
import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from parallex.preprocessing.clahe import preprocess_pair
from parallex.pipeline.registration import RegistrationPipeline
from parallex.pds4.reader import read_product
from parallex.io.pds4_image import open_pds4_image


app = FastAPI(
    title="PARALLAX Backend API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_standard_image(path: Path) -> np.ndarray:
    image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)

    if image is None:
        raise ValueError(f"Unable to read image: {path.name}")

    if image.ndim == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    return image


def _load_pds4_image(product_dir: Path) -> tuple[np.ndarray, dict]:
    product = read_product(product_dir)
    reader = open_pds4_image(product_dir)

    try:
        lines, samples = reader.shape

        max_dimension = 2048

        scale = min(
            1.0,
            max_dimension / float(max(lines, samples)),
        )

        height = max(1, int(round(lines * scale)))
        width = max(1, int(round(samples * scale)))

        row = max(0, (lines - height) // 2)
        col = max(0, (samples - width) // 2)

        image = reader.read_window(
            row=row,
            col=col,
            height=height,
            width=width,
        )

        if image.size == 0:
            raise ValueError("PDS4 image window is empty.")

        metadata = {
            "sensor": "UNKNOWN",
            "processing_level": "PDS4",
            "gsd": None,
            "altitude_km": None,
            "orbit": None,
            "projection": None,
            "source_shape": [int(lines), int(samples)],
            "window": {
                "row": int(row),
                "col": int(col),
                "height": int(height),
                "width": int(width),
            },
            "product_label": str(product.label_path),
        }

        return image, metadata

    finally:
        reader.close()


def _load_uploaded_source(
    image_path: Path,
    label_path: Path | None = None,
) -> tuple[np.ndarray, dict]:

    if image_path.suffix.lower() != ".img":
        image = _load_standard_image(image_path)

        return image, {
            "sensor": "UNKNOWN",
            "processing_level": "UPLOADED",
            "gsd": None,
            "altitude_km": None,
            "orbit": None,
            "projection": None,
        }

    if label_path is None:
        raise ValueError(
            f"PDS4 .IMG requires its accompanying XML label: {image_path.name}"
        )

    if not label_path.exists():
        raise ValueError(
            f"PDS4 XML label was not found: {label_path.name}"
        )

    return _load_pds4_image(image_path.parent)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "PARALLAX Backend",
        "pipeline": "available",
    }


@app.get("/api")
def api_info():
    return {
        "name": "PARALLAX",
        "description": "Chandrayaan-2 Lunar Image Registration Backend",
        "status": "online",
    }


@app.post("/api/register")
async def register_images(
    scenario: str = Form(...),
    reference: UploadFile = File(...),
    target: UploadFile = File(...),
    reference_label: UploadFile | None = File(None),
    target_label: UploadFile | None = File(None),
):
    scenario = scenario.upper().strip()

    if scenario not in {"EASY", "MEDIUM", "HARD", "CUSTOM"}:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid scenario: {scenario}",
        )

    if not reference.filename or not target.filename:
        raise HTTPException(
            status_code=400,
            detail="Both reference and target images are required.",
        )

    reference_is_pds4 = Path(reference.filename).suffix.lower() == ".img"
    target_is_pds4 = Path(target.filename).suffix.lower() == ".img"

    if reference_is_pds4 and reference_label is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Reference PDS4 .IMG requires its matching "
                "reference_label .XML file."
            ),
        )

    if target_is_pds4 and target_label is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Target PDS4 .IMG requires its matching "
                "target_label .XML file."
            ),
        )

    started = time.perf_counter()

    try:
        with tempfile.TemporaryDirectory(
            prefix="parallax_"
        ) as temp_dir_name:

            temp_dir = Path(temp_dir_name)

            # ------------------------------------------------------------------
            # Reference temporary product
            # ------------------------------------------------------------------

            reference_product_dir = (
                temp_dir / "reference_product"
            )

            reference_product_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            reference_path = (
                reference_product_dir
                / Path(reference.filename).name
            )

            reference_path.write_bytes(
                await reference.read()
            )

            reference_label_path = None

            if reference_label is not None:
                reference_label_path = (
                    reference_product_dir
                    / Path(reference_label.filename).name
                )

                reference_label_path.write_bytes(
                    await reference_label.read()
                )

            # ------------------------------------------------------------------
            # Target temporary product
            # ------------------------------------------------------------------

            target_product_dir = (
                temp_dir / "target_product"
            )

            target_product_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            target_path = (
                target_product_dir
                / Path(target.filename).name
            )

            target_path.write_bytes(
                await target.read()
            )

            target_label_path = None

            if target_label is not None:
                target_label_path = (
                    target_product_dir
                    / Path(target_label.filename).name
                )

                target_label_path.write_bytes(
                    await target_label.read()
                )

            # ------------------------------------------------------------------
            # Load images
            # ------------------------------------------------------------------

            if reference_is_pds4:
                image_a, metadata_a = _load_uploaded_source(
                    reference_path,
                    reference_label_path,
                )
            else:
                image_a, metadata_a = _load_uploaded_source(
                    reference_path,
                )

            if target_is_pds4:
                image_b, metadata_b = _load_uploaded_source(
                    target_path,
                    target_label_path,
                )
            else:
                image_b, metadata_b = _load_uploaded_source(
                    target_path,
                )

            if image_a.size == 0 or image_b.size == 0:
                raise ValueError(
                    "One of the uploaded images is empty."
                )

            # ------------------------------------------------------------------
            # CLAHE preprocessing
            # ------------------------------------------------------------------

            enhanced_a, enhanced_b, valid_a, valid_b = preprocess_pair(
                image_a,
                image_b,
            )

            valid_pixel_ratio = float(
                min(
                    np.mean(valid_a),
                    np.mean(valid_b),
                )
            )

            # ------------------------------------------------------------------
            # PARALLAX registration pipeline
            # ------------------------------------------------------------------

            pipeline = RegistrationPipeline()

            run_output = pipeline.run(
                enhanced_a,
                enhanced_b,
                metadata_a,
                metadata_b,
                overlap_ratio=1.0,
                valid_pixel_ratio=valid_pixel_ratio,
            )

            elapsed = time.perf_counter() - started

            if isinstance(run_output, tuple):
                decision, pipeline_res = run_output
            else:
                decision = run_output
                pipeline_res = getattr(
                    decision,
                    "result",
                    None,
                )

            # ------------------------------------------------------------------
            # Extract best completed attempt
            # ------------------------------------------------------------------

            best_attempt = None

            if (
                hasattr(decision, "attempts")
                and decision.attempts
            ):
                completed = [
                    a
                    for a in decision.attempts
                    if a.get("status") == "COMPLETED"
                ]

                if completed:
                    best_attempt = sorted(
                        completed,
                        key=lambda a: a.get(
                            "quality_score",
                            0.0,
                        ),
                        reverse=True,
                    )[0]
                else:
                    best_attempt = decision.attempts[-1]

            raw_matches = (
                best_attempt.get("raw_matches", 0)
                if best_attempt
                else 0
            )

            inliers = (
                best_attempt.get("inliers", 0)
                if best_attempt
                else 0
            )

            rmse_val = (
                best_attempt.get("rmse")
                if best_attempt
                else None
            )

            cov_val = (
                best_attempt.get("coverage")
                if best_attempt
                else None
            )

            inlier_ratio = (
                round(
                    float(inliers / raw_matches),
                    3,
                )
                if raw_matches > 0
                else 0.0
            )

            # ------------------------------------------------------------------
            # Quality decision
            # ------------------------------------------------------------------

            quality = getattr(
                decision,
                "quality",
                None,
            )

            if quality and hasattr(
                quality,
                "decision",
            ):
                status = str(
                    quality.decision
                ).upper()

            elif quality and isinstance(
                quality,
                dict,
            ):
                status = str(
                    quality.get(
                        "decision",
                        "REJECT",
                    )
                ).upper()

            elif getattr(
                decision,
                "rejected",
                False,
            ):
                status = "REJECT"

            else:
                status = (
                    str(
                        best_attempt.get(
                            "quality_decision",
                            "ACCEPT",
                        )
                    ).upper()
                    if best_attempt
                    else "ACCEPT"
                )

            matcher = (
                getattr(
                    decision,
                    "selected_matcher",
                    None,
                )
                or (
                    best_attempt.get("matcher")
                    if best_attempt
                    else None
                )
                or "Auto"
            )

            difficulty = (
                getattr(
                    decision,
                    "difficulty",
                    None,
                )
                or "MEDIUM"
            )

            confidence = getattr(
                decision,
                "confidence",
                0.85,
            )

            reason = getattr(
                decision,
                "reason",
                "",
            )

            return {
                "status": status,
                "scenario": scenario,
                "matcher": matcher,
                "difficulty": difficulty,
                "matches_found": int(raw_matches),
                "verified_matches": int(inliers),
                "inlier_ratio": inlier_ratio,
                "rmse_px": (
                    round(float(rmse_val), 3)
                    if rmse_val is not None
                    else None
                ),
                "coverage": (
                    round(float(cov_val), 3)
                    if cov_val is not None
                    else None
                ),
                "confidence": (
                    float(confidence)
                    if confidence is not None
                    else None
                ),
                "runtime_seconds": round(
                    elapsed,
                    3,
                ),
                "registered_image": None,
                "matches_image": None,
                "correspondence_csv": None,
                "metrics_report": None,
                "provenance_log": None,
                "reason": reason,
                "reference_shape": list(
                    image_a.shape
                ),
                "target_shape": list(
                    image_b.shape
                ),
                "reference_metadata": metadata_a,
                "target_metadata": metadata_b,
            }

    except MemoryError:
        raise HTTPException(
            status_code=413,
            detail=(
                "Image is too large for the available memory."
            ),
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                f"PARALLAX registration failed: {exc}"
            ),
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )
