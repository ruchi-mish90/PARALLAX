from __future__ import annotations

from pathlib import Path

import numpy as np

from parallex.products.product import Product
from parallex.geometry.adapter import GeometryAdapter
from parallex.preprocessing.registry import create_preprocessor
from parallex.preprocessing.storage import create_run, save_preprocessed


IIRS_PATH = Path(
    r"C:\Users\graj6\Downloads\P0001\ch2_iir_nci_20221209T1908498944_d_img_n18"
)

TMC2_PATH = Path(
    r"C:\Users\graj6\Downloads\P0001\ch2_tmc_ncn_20230605T1503198538_d_img_n18"
)


def main():
    source = Product(IIRS_PATH)
    target = Product(TMC2_PATH)

    source_geo = GeometryAdapter(source)
    target_geo = GeometryAdapter(target)

    # Known valid geographic overlap for the current IIRS ↔ TMC2 test.
    lat_min = 60.0
    lat_max = 82.0
    lon_min = 354.6
    lon_max = 355.5

    # Use the center of the validated overlap to obtain pixel coordinates.
    lat = (lat_min + lat_max) / 2.0
    lon = (lon_min + lon_max) / 2.0

    source_px = source_geo.geo_to_pixel(lat, lon)
    target_px = target_geo.geo_to_pixel(lat, lon)

    if source_px is None or target_px is None:
        raise RuntimeError("Could not project overlap center into both products.")

    source_row, source_col = map(int, map(round, source_px))
    target_row, target_col = map(int, map(round, target_px))

    size = 512

    source_shape = source.shape[-2:]
    target_shape = target.shape[-2:]

    source_row = max(0, min(source_row - size // 2, source_shape[0] - size))
    source_col = max(0, min(source_col - size // 2, source_shape[1] - size))

    target_row = max(0, min(target_row - size // 2, target_shape[0] - size))
    target_col = max(0, min(target_col - size, target_shape[1] - size))

    source_processor = create_preprocessor(
        source,
        representation="band",
        band=160,
        normalize=True,
    )

    target_processor = create_preprocessor(
        target,
        representation="gradient",
        normalize=True,
    )

    source_result = source_processor.run_window(
        source_row,
        source_col,
        size,
        size,
    )

    target_result = target_processor.run_window(
        target_row,
        target_col,
        size,
        size,
    )

    run_id, run_dir = create_run("IIRS", "TMC2")

    manifest = {
        "source_sensor": "IIRS",
        "target_sensor": "TMC2",
        "source_product": str(IIRS_PATH),
        "target_product": str(TMC2_PATH),
        "source_representation": "band",
        "source_band": 160,
        "target_representation": "gradient",
        "roi": {
            "latitude": [lat_min, lat_max],
            "longitude": [lon_min, lon_max],
            "source_pixel": [source_row, source_col],
            "target_pixel": [target_row, target_col],
            "size": [size, size],
        },
        "overlap_validated": True,
    }

    saved = save_preprocessed(
        run_dir,
        source_image=source_result.image,
        target_image=target_result.image,
        source_metadata={
            "sensor": "IIRS",
            "representation": "band",
            "band": 160,
            "shape": list(source_result.image.shape),
            "row": source_row,
            "col": source_col,
        },
        target_metadata={
            "sensor": "TMC2",
            "representation": "gradient",
            "shape": list(target_result.image.shape),
            "row": target_row,
            "col": target_col,
        },
        manifest=manifest,
    )

    print("\nPREPROCESSING COMPLETE")
    print("RUN ID:", run_id)
    print("SOURCE:", saved["source_path"])
    print("TARGET:", saved["target_path"])
    print("MANIFEST:", saved["manifest"])
    print("SOURCE SHAPE:", source_result.image.shape)
    print("TARGET SHAPE:", target_result.image.shape)


if __name__ == "__main__":
    main()
