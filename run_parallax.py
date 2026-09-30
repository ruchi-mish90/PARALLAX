from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(r"C:\Users\graj6\Downloads\parallex")
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from parallex.io.pds4_image import open_pds4_image
from parallex.io.roi import memory_safe_window
from parallex.pds4.metadata import extract_metadata
from parallex.overlap.geometry import (
    load_geometry,
    overlap_tiles,
)
from parallex.overlap.spatial import spatial_co_location
from parallex.preprocessing import preprocess_pair
from parallex.pipeline.registration import RegistrationPipeline


PRODUCTS = {
    "OHRC_2020":
        ROOT / r"data\real_pairs\ch2_ohr_ncp_20200827T0619368134_d_img_d18",

    "OHRC_2025":
        ROOT / r"data\real_pairs\ch2_ohr_ncp_20250125T0129111531_d_img_d18",

    "TMC2_NCA":
        ROOT / r"data\real_pairs\ch2_tmc_nca_20221209T2305274611_d_img_d32",

    "TMC2_NCN":
        ROOT / r"data\real_pairs\ch2_tmc_ncn_20221209T2305274611_d_img_d32",

    "TMC2_P0001":
        ROOT / r"data\real_pairs\P0001_TMC2\extracted",
}


NEGATIVE_PAIRS = [
    ("P0001", "OHRC_2020", "TMC2_P0001"),
    ("P0004", "OHRC_2025", "TMC2_NCN"),
    ("P0005", "OHRC_2025", "TMC2_NCA"),
]


POSITIVE_PAIR = (
    "POSITIVE_TMC2",
    "TMC2_NCA",
    "TMC2_NCN",
)


OUTPUT = ROOT / "results" / "final_backend"
OUTPUT.mkdir(parents=True, exist_ok=True)


def find_geometry_csv(product):
    candidates = sorted(product.rglob("*.csv"))

    preferred = [
        p for p in candidates
        if "grd" in p.name.lower()
        or "geometry" in p.name.lower()
    ]

    if not preferred:
        raise FileNotFoundError(
            f"No geometry CSV found under {product}"
        )

    return preferred[0]


def load_product(name):
    product = PRODUCTS[name]

    geometry_csv = find_geometry_csv(product)
    geometry = load_geometry(geometry_csv)

    metadata = extract_metadata(product)

    image = open_pds4_image(product)

    return {
        "name": name,
        "product": product,
        "geometry": geometry,
        "geometry_csv": geometry_csv,
        "metadata": metadata,
        "image": image,
    }


def serialize_value(value):
    if value is None:
        return None

    if isinstance(value, (np.integer,)):
        return int(value)

    if isinstance(value, (np.floating,)):
        return float(value)

    if isinstance(value, np.ndarray):
        return value.tolist()

    if isinstance(value, Path):
        return str(value)

    if hasattr(value, "__dict__"):
        return {
            str(k): serialize_value(v)
            for k, v in value.__dict__.items()
        }

    return value


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(
            serialize_value(data),
            f,
            indent=2,
        )


def spatial_result_dict(result):
    return {
        "overlaps": bool(result.overlaps),
        "latitude_min": result.latitude_min,
        "latitude_max": result.latitude_max,
        "longitude_intervals": [
            [float(a), float(b)]
            for a, b in result.longitude_intervals
        ],
        "reason": result.reason,
    }


def process_negative_pair(pair_id, name_a, name_b, products):
    print()
    print("=" * 80)
    print(pair_id)
    print(f"A = {name_a}")
    print(f"B = {name_b}")

    result = spatial_co_location(
        products[name_a]["geometry"],
        products[name_b]["geometry"],
    )

    spatial = spatial_result_dict(result)

    pair_output = OUTPUT / pair_id
    pair_output.mkdir(parents=True, exist_ok=True)

    record = {
        "pair_id": pair_id,
        "sensor_a": name_a,
        "sensor_b": name_b,
        "stage": "spatial_co_location",
        "spatial": spatial,
        "registration_attempted": False,
        "decision": "REJECT" if not result.overlaps else "CONTINUE",
        "reason": result.reason,
    }

    save_json(
        pair_output / "result.json",
        record,
    )

    print("SPATIAL OVERLAP:", result.overlaps)
    print("REASON:", result.reason)
    print("REGISTRATION ATTEMPTED: False")

    return record


def choose_positive_roi(product_a, product_b, spatial):
    tiles = overlap_tiles(
        product_a["geometry"],
        product_b["geometry"],
        spatial.latitude_min,
        spatial.latitude_max,
        spatial.longitude_intervals,
        tile_size=2048,
        samples_lat=3,
        samples_lon=3,
    )

    if not tiles:
        raise RuntimeError(
            "Spatial overlap exists but no geographic ROI "
            "could be generated."
        )

    # Prefer an interior tile rather than a boundary tile.
    candidates = []

    for tile in tiles:
        roi_a, roi_b, lat, lon = tile

        image_a = product_a["image"]
        image_b = product_b["image"]

        margin = 256

        interior_a = (
            roi_a.y0 > margin
            and roi_a.x0 > margin
            and roi_a.y1 < image_a.shape[0] - margin
            and roi_a.x1 < image_a.shape[1] - margin
        )

        interior_b = (
            roi_b.y0 > margin
            and roi_b.x0 > margin
            and roi_b.y1 < image_b.shape[0] - margin
            and roi_b.x1 < image_b.shape[1] - margin
        )

        if interior_a and interior_b:
            candidates.append(tile)

    if candidates:
        return candidates[len(candidates) // 2]

    return tiles[len(tiles) // 2]


def run_positive_pair():
    pair_id, name_a, name_b = POSITIVE_PAIR

    print()
    print("=" * 80)
    print("POSITIVE REAL-DATA REGISTRATION")
    print("=" * 80)
    print(f"A = {name_a}")
    print(f"B = {name_b}")

    product_a = PRODUCTS_DATA[name_a]
    product_b = PRODUCTS_DATA[name_b]

    spatial = spatial_co_location(
        product_a["geometry"],
        product_b["geometry"],
    )

    spatial_dict = spatial_result_dict(spatial)

    print("SPATIAL OVERLAP:", spatial.overlaps)

    if not spatial.overlaps:
        raise RuntimeError(
            "The designated positive pair does not overlap."
        )

    roi_a, roi_b, anchor_lat, anchor_lon = choose_positive_roi(
        product_a,
        product_b,
        spatial,
    )

    print(
        f"ANCHOR: lat={anchor_lat:.6f}, "
        f"lon={anchor_lon:.6f}"
    )

    print(
        "ROI A:",
        roi_a.y0,
        roi_a.y1,
        roi_a.x0,
        roi_a.x1,
    )

    print(
        "ROI B:",
        roi_b.y0,
        roi_b.y1,
        roi_b.x0,
        roi_b.x1,
    )

    image_a = memory_safe_window(
        product_a["image"],
        roi_a,
        max_height=2048,
        max_width=2048,
    )

    image_b = memory_safe_window(
        product_b["image"],
        roi_b,
        max_height=2048,
        max_width=2048,
    )

    print("RAW IMAGE A:", image_a.shape, image_a.dtype)
    print("RAW IMAGE B:", image_b.shape, image_b.dtype)

    clahe_a, clahe_b, valid_a, valid_b = preprocess_pair(
        image_a,
        image_b,
    )

    valid_ratio_a = float(np.mean(valid_a))
    valid_ratio_b = float(np.mean(valid_b))
    valid_ratio = min(
        valid_ratio_a,
        valid_ratio_b,
    )

    print(
        "VALID PIXEL RATIO:",
        f"{valid_ratio:.4f}",
    )

    pipeline = RegistrationPipeline()

    start = time.perf_counter()

    decision, result = pipeline.run(
        clahe_a,
        clahe_b,
        product_a["metadata"],
        product_b["metadata"],
        overlap_ratio=1.0,
        valid_pixel_ratio=valid_ratio,
    )

    elapsed = time.perf_counter() - start

    print()
    print("REGISTRATION COMPLETE")
    print("SELECTED MATCHER:", decision.selected_matcher)
    print("DIFFICULTY:", decision.difficulty)
    print("DECISION:", "REJECT" if decision.rejected else "COMPLETED")
    print("RUNTIME:", f"{elapsed:.2f} s")

    attempts = []

    for attempt in decision.attempts:
        attempts.append(
            serialize_value(attempt)
        )

    quality = serialize_value(decision.quality)

    record = {
        "pair_id": pair_id,
        "sensor_a": name_a,
        "sensor_b": name_b,
        "spatial": spatial_dict,
        "anchor": {
            "latitude": float(anchor_lat),
            "longitude": float(anchor_lon),
        },
        "roi_a": {
            "y0": roi_a.y0,
            "y1": roi_a.y1,
            "x0": roi_a.x0,
            "x1": roi_a.x1,
        },
        "roi_b": {
            "y0": roi_b.y0,
            "y1": roi_b.y1,
            "x0": roi_b.x0,
            "x1": roi_b.x1,
        },
        "preprocessing": {
            "method": "percentile_normalization_plus_CLAHE",
            "valid_ratio_a": valid_ratio_a,
            "valid_ratio_b": valid_ratio_b,
            "valid_ratio": valid_ratio,
        },
        "routing": {
            "selected_matcher": decision.selected_matcher,
            "difficulty": decision.difficulty,
            "confidence": decision.confidence,
            "candidate_scores": serialize_value(
                decision.candidate_scores
            ),
        },
        "quality": quality,
        "attempts": attempts,
        "rejected": bool(decision.rejected),
        "reason": decision.reason,
        "rejection_reason": decision.rejection_reason,
        "runtime_seconds": float(elapsed),
    }

    output_dir = OUTPUT / pair_id
    output_dir.mkdir(parents=True, exist_ok=True)

    save_json(
        output_dir / "result.json",
        record,
    )

    return record


print("=" * 80)
print("PARALLAX FINAL BACKEND RUNNER")
print("=" * 80)

print()
print("Loading products...")

PRODUCTS_DATA = {}

required_names = {
    name
    for _, name_a, name_b in NEGATIVE_PAIRS
    for name in (name_a, name_b)
}

required_names.update(
    [POSITIVE_PAIR[1], POSITIVE_PAIR[2]]
)

for name in sorted(required_names):
    PRODUCTS_DATA[name] = load_product(name)

    grid = PRODUCTS_DATA[name]["geometry"]

    print(
        f"{name:12s} "
        f"geometry={grid.latitude.shape} "
        f"metadata_sensor="
        f"{PRODUCTS_DATA[name]['metadata'].get('sensor')}"
    )


all_records = []

print()
print("=" * 80)
print("NEGATIVE SPATIAL CASES")
print("=" * 80)

for pair in NEGATIVE_PAIRS:
    all_records.append(
        process_negative_pair(
            pair[0],
            pair[1],
            pair[2],
            PRODUCTS_DATA,
        )
    )


positive_record = run_positive_pair()
all_records.append(positive_record)


csv_path = OUTPUT / "parallax_results.csv"

fieldnames = [
    "pair_id",
    "sensor_a",
    "sensor_b",
    "spatial_overlap",
    "registration_attempted",
    "selected_matcher",
    "difficulty",
    "decision",
    "runtime_seconds",
    "reason",
]

with csv_path.open(
    "w",
    newline="",
    encoding="utf-8",
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames,
    )

    writer.writeheader()

    for record in all_records:

        writer.writerow({
            "pair_id": record["pair_id"],
            "sensor_a": record["sensor_a"],
            "sensor_b": record["sensor_b"],
            "spatial_overlap": record["spatial"]["overlaps"],
            "registration_attempted": record.get("registration_attempted", True),
            "selected_matcher": record.get(
                "routing",
                {},
            ).get(
                "selected_matcher"
            ),
            "difficulty": record.get(
                "routing",
                {},
            ).get(
                "difficulty"
            ),
            "decision": record.get(
                "decision",
                "COMPLETED",
            ),
            "runtime_seconds": record.get(
                "runtime_seconds"
            ),
            "reason": record.get(
                "reason",
                "",
            ),
        })


save_json(
    OUTPUT / "parallax_results.json",
    all_records,
)


print()
print("=" * 80)
print("FINAL BACKEND RUN COMPLETE")
print("=" * 80)
print("RESULTS:", OUTPUT)
print("CSV:", csv_path)
print(
    "JSON:",
    OUTPUT / "parallax_results.json",
)

for record in all_records:
    print()
    print(
        record["pair_id"],
        "→",
        record["reason"],
    )




