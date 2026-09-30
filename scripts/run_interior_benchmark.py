from __future__ import annotations

import sys
import time
import csv
from pathlib import Path

import numpy as np
import cv2
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from parallex.overlap.geometry import load_geometry, geo_to_pixel, _safe_roi
from parallex.io.pds4_image import open_pds4_image
from parallex.pds4.metadata import extract_metadata
from parallex.pipeline.registration import RegistrationPipeline


A = ROOT / r"data\real_pairs\ch2_tmc_nca_20221209T2305274611_d_img_d32"
B = ROOT / r"data\real_pairs\ch2_tmc_ncn_20221209T2305274611_d_img_d32"


def find_csv(product):
    files = sorted(product.rglob("*.csv"))
    files = [
        p for p in files
        if "grd" in p.name.lower()
        or "geometry" in p.name.lower()
    ]
    if not files:
        raise FileNotFoundError(f"No geometry CSV in {product}")
    return files[0]


def clahe(image):
    image = np.asarray(image, dtype=np.float32)

    lo, hi = np.percentile(image, [1, 99])

    if hi <= lo:
        return image

    image = np.clip(
        (image - lo) / (hi - lo),
        0,
        1,
    )

    image8 = np.uint8(image * 255)

    enhancer = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8),
    )

    return enhancer.apply(image8).astype(np.float32) / 255.0


class ROI:
    def __init__(self, y0, y1, x0, x1):
        self.y0 = int(y0)
        self.y1 = int(y1)
        self.x0 = int(x0)
        self.x1 = int(x1)

    @property
    def height(self):
        return self.y1 - self.y0

    @property
    def width(self):
        return self.x1 - self.x0


def get_common_anchors(ga, gb):

    lat_a = ga.latitude.ravel()
    lon_a = ga.longitude.ravel() % 360

    lat_b = gb.latitude.ravel()
    lon_b = gb.longitude.ravel() % 360

    valid_a = np.isfinite(lat_a) & np.isfinite(lon_a)
    valid_b = np.isfinite(lat_b) & np.isfinite(lon_b)

    lat_a = lat_a[valid_a]
    lon_a = lon_a[valid_a]

    lat_b = lat_b[valid_b]
    lon_b = lon_b[valid_b]

    common_lat_min = max(
        lat_a.min(),
        lat_b.min(),
    )

    common_lat_max = min(
        lat_a.max(),
        lat_b.max(),
    )

    anchors = []

    # Dense candidate search over actual footprint.
    for lat in np.linspace(
        common_lat_min + 1.0,
        common_lat_max - 1.0,
        12,
    ):

        mask_a = np.abs(lat_a - lat) <= 0.75
        mask_b = np.abs(lat_b - lat) <= 0.75

        if not mask_a.any() or not mask_b.any():
            continue

        la = lon_a[mask_a]
        lb = lon_b[mask_b]

        # Use actual longitudes represented by the two footprints.
        for lon in np.linspace(
            0,
            360,
            144,
            endpoint=False,
        ):

            da = np.minimum(
                np.abs(la - lon),
                360 - np.abs(la - lon),
            )

            db = np.minimum(
                np.abs(lb - lon),
                360 - np.abs(lb - lon),
            )

            if da.min() <= 0.75 and db.min() <= 0.75:
                anchors.append(
                    (float(lat), float(lon))
                )

    return list(dict.fromkeys(anchors))


def main():

    print("=" * 80)
    print("PARALLAX INTERIOR-ANCHOR BENCHMARK")
    print("=" * 80)

    ga = load_geometry(find_csv(A))
    gb = load_geometry(find_csv(B))

    reader_a = open_pds4_image(A)
    reader_b = open_pds4_image(B)

    metadata_a = extract_metadata(A)
    metadata_b = extract_metadata(B)

    candidates = get_common_anchors(ga, gb)

    print("Common candidates:", len(candidates))

    valid = []

    margin = 1024

    for lat, lon in candidates:

        scan_a, px_a = geo_to_pixel(
            ga,
            lat,
            lon,
        )

        scan_b, px_b = geo_to_pixel(
            gb,
            lat,
            lon,
        )

        # Require a full 2048x2048 ROI around the point.
        if not (
            margin <= scan_a <= reader_a.info.shape[0] - margin
            and margin <= px_a <= reader_a.info.shape[1] - margin
        ):
            continue

        if not (
            margin <= scan_b <= reader_b.info.shape[0] - margin
            and margin <= px_b <= reader_b.info.shape[1] - margin
        ):
            continue

        valid.append(
            (
                lat,
                lon,
                scan_a,
                px_a,
                scan_b,
                px_b,
            )
        )

    print("Interior anchors:", len(valid))

    # Maximum 4 representative anchors for fast laptop evaluation.
    if len(valid) > 4:
        indices = np.linspace(
            0,
            len(valid) - 1,
            4,
            dtype=int,
        )
        valid = [
            valid[i]
            for i in indices
        ]

    print("Anchors benchmarked:", len(valid))

    if not valid:
        print()
        print("NO INTERIOR ANCHORS FOUND.")
        print("Geometry footprint is too close to image boundaries.")
        return

    pipeline = RegistrationPipeline()

    output_dir = (
        ROOT
        / r"data\real_pairs\benchmark_results"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_csv = (
        output_dir
        / "tmc2_nca_vs_ncn_interior_clahe_benchmark.csv"
    )

    rows = []

    total_start = time.perf_counter()

    for tile_id, item in enumerate(
        valid,
        1,
    ):

        (
            lat,
            lon,
            scan_a,
            px_a,
            scan_b,
            px_b,
        ) = item

        roi_a_t = _safe_roi(
            scan_a,
            px_a,
            reader_a.info.shape,
            2048,
        )

        roi_b_t = _safe_roi(
            scan_b,
            px_b,
            reader_b.info.shape,
            2048,
        )

        roi_a = ROI(*roi_a_t)
        roi_b = ROI(*roi_b_t)

        print()
        print("-" * 80)
        print(
            f"TILE {tile_id}/{len(valid)} "
            f"LAT={lat:.4f} "
            f"LON={lon:.4f}"
        )

        print(
            f"A anchor=({scan_a:.0f},{px_a:.0f}) "
            f"ROI={roi_a_t}"
        )

        print(
            f"B anchor=({scan_b:.0f},{px_b:.0f}) "
            f"ROI={roi_b_t}"
        )

        start = time.perf_counter()

        try:

            raw_a = reader_a.read_window(
                roi_a.y0,
                roi_a.x0,
                roi_a.height,
                roi_a.width,
            )

            raw_b = reader_b.read_window(
                roi_b.y0,
                roi_b.x0,
                roi_b.height,
                roi_b.width,
            )

            image_a = clahe(raw_a)
            image_b = clahe(raw_b)

            decision, result = pipeline.run(
                image_a,
                image_b,
                metadata_a,
                metadata_b,
                overlap_ratio=1.0,
                valid_pixel_ratio=1.0,
            )

            elapsed = time.perf_counter() - start

            print(
                "FINAL:",
                decision.selected_matcher,
                "| REJECTED:",
                decision.rejected,
                "| TIME:",
                f"{elapsed:.2f}s",
            )

            for attempt in decision.attempts:

                row = {
                    "tile_id": tile_id,
                    "latitude": lat,
                    "longitude": lon,

                    "anchor_scan_a": scan_a,
                    "anchor_pixel_a": px_a,
                    "anchor_scan_b": scan_b,
                    "anchor_pixel_b": px_b,

                    "matcher": attempt.get(
                        "matcher",
                        "",
                    ),

                    "status": attempt.get(
                        "status",
                        "",
                    ),

                    "raw_matches": attempt.get(
                        "raw_matches",
                        "",
                    ),

                    "filtered_matches": attempt.get(
                        "filtered_matches",
                        "",
                    ),

                    "inliers": attempt.get(
                        "inliers",
                        "",
                    ),

                    "inlier_ratio": attempt.get(
                        "inlier_ratio",
                        "",
                    ),

                    "reprojection_error_px":
                        attempt.get(
                            "reprojection_error_px",
                            "",
                        ),

                    "refined_reprojection_error_px":
                        attempt.get(
                            "refined_reprojection_error_px",
                            "",
                        ),

                    "coverage_ratio":
                        attempt.get(
                            "coverage_ratio",
                            "",
                        ),

                    "uniformity":
                        attempt.get(
                            "uniformity",
                            "",
                        ),

                    "quality_score":
                        attempt.get(
                            "quality_score",
                            "",
                        ),

                    "quality_decision":
                        attempt.get(
                            "quality_decision",
                            "",
                        ),

                    "quality_reasons":
                        "|".join(
                            map(
                                str,
                                attempt.get(
                                    "quality_reasons",
                                    [],
                                ),
                            )
                        ),

                    "time_s":
                        elapsed,
                }

                rows.append(row)

                print(
                    f"  {row['matcher']:25s} "
                    f"raw={row['raw_matches']} "
                    f"filtered={row['filtered_matches']} "
                    f"inliers={row['inliers']} "
                    f"ratio={row['inlier_ratio']} "
                    f"RMSE={row['refined_reprojection_error_px']} "
                    f"coverage={row['coverage_ratio']} "
                    f"quality={row['quality_decision']}"
                )

        except Exception as exc:

            print(
                "ERROR:",
                type(exc).__name__,
                str(exc),
            )

    if rows:

        with output_csv.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as f:

            writer = csv.DictWriter(
                f,
                fieldnames=rows[0].keys(),
            )

            writer.writeheader()
            writer.writerows(rows)

    total = time.perf_counter() - total_start

    print()
    print("=" * 80)
    print("INTERIOR BENCHMARK COMPLETE")
    print("=" * 80)
    print("Anchors tested:", len(valid))
    print("Result rows:", len(rows))
    print("Total time:", f"{total:.2f}s")
    print("Output:", output_csv)
    print("=" * 80)


if __name__ == "__main__":
    main()
