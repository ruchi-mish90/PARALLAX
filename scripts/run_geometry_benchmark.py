from __future__ import annotations

import sys
from pathlib import Path

# Initialize PyTorch before importing PARALLAX modules.
# This avoids the intermittent Windows DLL initialization failure.
import torch

print("TORCH:", torch.__version__)
print("CUDA:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import csv
import time
import numpy as np

from parallex.io.pds4_image import open_pds4_image
from parallex.pds4.metadata import extract_metadata
from parallex.overlap.geometry import load_geometry, overlap_tiles
from parallex.pipeline.registration import RegistrationPipeline


ROOT = Path(__file__).resolve().parents[1]

PRODUCT_A = ROOT / r"data\real_pairs\ch2_tmc_nca_20221209T2305274611_d_img_d32"
PRODUCT_B = ROOT / r"data\real_pairs\ch2_tmc_ncn_20221209T2305274611_d_img_d32"

OUTPUT_DIR = ROOT / r"data\real_pairs\benchmark_results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_CSV = OUTPUT_DIR / "tmc2_nca_vs_ncn_geometry_benchmark.csv"


def find_geometry_csv(product_dir: Path) -> Path:
    csv_files = sorted(product_dir.rglob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV geometry file found under {product_dir}"
        )

    preferred = [
        p for p in csv_files
        if any(
            token in p.name.lower()
            for token in ("geometry", "geom", "tie", "point")
        )
    ]

    return preferred[0] if preferred else csv_files[0]


def main():

    print("=" * 80)
    print("PARALLAX GEOMETRY-BASED REAL-DATA BENCHMARK")
    print("=" * 80)

    print("\n[1/6] Loading metadata")

    metadata_a = extract_metadata(PRODUCT_A)
    metadata_b = extract_metadata(PRODUCT_B)

    print("Sensor A:", metadata_a.get("sensor"))
    print("Sensor B:", metadata_b.get("sensor"))

    print("\n[2/6] Loading geometry")

    geometry_csv_a = find_geometry_csv(PRODUCT_A)
    geometry_csv_b = find_geometry_csv(PRODUCT_B)

    print("Geometry A:", geometry_csv_a)
    print("Geometry B:", geometry_csv_b)

    grid_a = load_geometry(geometry_csv_a)
    grid_b = load_geometry(geometry_csv_b)

    print("Geometry A:", grid_a.latitude.shape)
    print("Geometry B:", grid_b.latitude.shape)

    print("\n[3/6] Opening images")

    reader_a = open_pds4_image(PRODUCT_A)
    reader_b = open_pds4_image(PRODUCT_B)

    print("Image A:", reader_a.info.shape, reader_a.info.dtype)
    print("Image B:", reader_b.info.shape, reader_b.info.dtype)

    print("\n[4/6] Generating geometry-derived overlapping ROIs")

    tiles = overlap_tiles(
        grid_a,
        grid_b,
        latitude_min=0.0,
        latitude_max=90.0,
        longitude_intervals=[(0.0, 360.0)],
        tile_size=2048,
        samples_lat=4,
        samples_lon=4,
    )

    print("Geometry-derived tiles:", len(tiles))

    if not tiles:
        raise RuntimeError(
            "No overlapping geometry-derived tiles were generated."
        )

    pipeline = RegistrationPipeline()

    rows = []
    total_start = time.perf_counter()

    print("\n[5/6] Running registration\n")

    for tile_id, (roi_a, roi_b, latitude, longitude) in enumerate(
        tiles, start=1
    ):

        print("-" * 80)
        print(
            f"TILE {tile_id}/{len(tiles)} | "
            f"LAT={latitude:.6f} | LON={longitude:.6f}"
        )

        print(
            "ROI A:",
            (roi_a.y0, roi_a.y1, roi_a.x0, roi_a.x1)
        )

        print(
            "ROI B:",
            (roi_b.y0, roi_b.y1, roi_b.x0, roi_b.x1)
        )

        tile_start = time.perf_counter()

        try:

            image_a = reader_a.read_window(
                roi_a.y0,
                roi_a.x0,
                roi_a.height,
                roi_a.width,
            )

            image_b = reader_b.read_window(
                roi_b.y0,
                roi_b.x0,
                roi_b.height,
                roi_b.width,
            )

            decision, result = pipeline.run(
                image_a,
                image_b,
                metadata_a,
                metadata_b,
                overlap_ratio=1.0,
                valid_pixel_ratio=1.0,
            )

            elapsed = time.perf_counter() - tile_start

            print(
                "FINAL:",
                decision.selected_matcher,
                "| REJECTED:",
                decision.rejected,
                "| TIME:",
                f"{elapsed:.2f}s",
            )

            for attempt in decision.attempts:

                matcher = attempt.get("matcher", "")
                status = attempt.get("status", "")

                row = {
                    "tile_id": tile_id,
                    "latitude": latitude,
                    "longitude": longitude,

                    "roi_a_y0": roi_a.y0,
                    "roi_a_y1": roi_a.y1,
                    "roi_a_x0": roi_a.x0,
                    "roi_a_x1": roi_a.x1,

                    "roi_b_y0": roi_b.y0,
                    "roi_b_y1": roi_b.y1,
                    "roi_b_x0": roi_b.x0,
                    "roi_b_x1": roi_b.x1,

                    "matcher": matcher,
                    "status": status,

                    "raw_matches": attempt.get("raw_matches", ""),
                    "filtered_matches": attempt.get(
                        "filtered_matches", ""
                    ),

                    "confidence_threshold": attempt.get(
                        "confidence_threshold", ""
                    ),

                    "retained_ratio": attempt.get(
                        "retained_ratio", ""
                    ),

                    "coordinate_points": attempt.get(
                        "coordinate_points", ""
                    ),

                    "inliers": attempt.get("inliers", ""),
                    "inlier_ratio": attempt.get(
                        "inlier_ratio", ""
                    ),

                    "reprojection_error_px": attempt.get(
                        "reprojection_error_px", ""
                    ),

                    "refined_reprojection_error_px":
                        attempt.get(
                            "refined_reprojection_error_px",
                            ""
                        ),

                    "coverage_ratio": attempt.get(
                        "coverage_ratio", ""
                    ),

                    "coverage_source": attempt.get(
                        "coverage_source", ""
                    ),

                    "coverage_target": attempt.get(
                        "coverage_target", ""
                    ),

                    "uniformity": attempt.get(
                        "uniformity", ""
                    ),

                    "refinement_success": attempt.get(
                        "refinement_success", ""
                    ),

                    "mean_subpixel_shift_a": attempt.get(
                        "mean_subpixel_shift_a", ""
                    ),

                    "mean_subpixel_shift_b": attempt.get(
                        "mean_subpixel_shift_b", ""
                    ),

                    "quality_score": attempt.get(
                        "quality_score", ""
                    ),

                    "quality_decision": attempt.get(
                        "quality_decision", ""
                    ),

                    "quality_reasons": "|".join(
                        map(
                            str,
                            attempt.get(
                                "quality_reasons", []
                            ),
                        )
                    ),

                    "tile_time_s": elapsed,

                    "final_selected_matcher":
                        decision.selected_matcher,

                    "final_rejected":
                        decision.rejected,

                    "final_reason":
                        decision.reason,
                }

                rows.append(row)

                print(
                    f"  {matcher:25s} "
                    f"{status:12s} "
                    f"raw={row['raw_matches']} "
                    f"filtered={row['filtered_matches']} "
                    f"inliers={row['inliers']} "
                    f"ratio={row['inlier_ratio']} "
                    f"rmse={row['refined_reprojection_error_px']} "
                    f"coverage={row['coverage_ratio']} "
                    f"quality={row['quality_decision']}"
                )

        except Exception as exc:

            elapsed = time.perf_counter() - tile_start

            print(
                "TILE ERROR:",
                type(exc).__name__,
                str(exc),
            )

            rows.append({
                "tile_id": tile_id,
                "latitude": latitude,
                "longitude": longitude,

                "roi_a_y0": roi_a.y0,
                "roi_a_y1": roi_a.y1,
                "roi_a_x0": roi_a.x0,
                "roi_a_x1": roi_a.x1,

                "roi_b_y0": roi_b.y0,
                "roi_b_y1": roi_b.y1,
                "roi_b_x0": roi_b.x0,
                "roi_b_x1": roi_b.x1,

                "matcher": "",
                "status": "TILE_FAILED",

                "raw_matches": "",
                "filtered_matches": "",
                "confidence_threshold": "",
                "retained_ratio": "",
                "coordinate_points": "",

                "inliers": "",
                "inlier_ratio": "",

                "reprojection_error_px": "",
                "refined_reprojection_error_px": "",

                "coverage_ratio": "",
                "coverage_source": "",
                "coverage_target": "",
                "uniformity": "",

                "refinement_success": "",
                "mean_subpixel_shift_a": "",
                "mean_subpixel_shift_b": "",

                "quality_score": "",
                "quality_decision": "",

                "quality_reasons":
                    f"{type(exc).__name__}: {exc}",

                "tile_time_s": elapsed,
                "final_selected_matcher": "",
                "final_rejected": "",
                "final_reason": "",
            })

    print("\n[6/6] Writing benchmark CSV")

    if rows:

        fieldnames = list(rows[0].keys())

        with OUTPUT_CSV.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as f:

            writer = csv.DictWriter(
                f,
                fieldnames=fieldnames,
            )

            writer.writeheader()
            writer.writerows(rows)

    total_elapsed = time.perf_counter() - total_start

    print()
    print("=" * 80)
    print("BENCHMARK COMPLETE")
    print("=" * 80)
    print("Tiles:", len(tiles))
    print("Benchmark rows:", len(rows))
    print("Total time:", f"{total_elapsed:.2f}s")
    print("Output:", OUTPUT_CSV)
    print("=" * 80)


if __name__ == "__main__":
    main()
