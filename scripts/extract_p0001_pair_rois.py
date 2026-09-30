from pathlib import Path
import csv
import json
import numpy as np

from parallex.overlap.geometry import load_geometry, geo_to_pixel


P0001 = Path(r"C:\Users\graj6\Downloads\P0001")
OUT = Path("results") / "P0001_3SENSOR_ROIS"


PRODUCTS = {
    "OHRC": P0001 / "ch2_ohr_ncp_20250612T2031048828_d_img_d18",
    "TMC2": P0001 / "ch2_tmc_ncn_20230605T1503198538_d_img_n18",
    "IIRS": P0001 / "ch2_iir_nci_20221209T1908498944_d_img_n18",
}


PAIRS = [
    ("OHRC", "TMC2"),
    ("TMC2", "IIRS"),
    ("IIRS", "OHRC"),
]


# Conservative geographic sampling.
# We deliberately stay away from the exact footprint edges.
PAIR_WINDOWS = {
    ("OHRC", "TMC2"): {
        "lat_min": 60.25,
        "lat_max": 60.93,
        "lon_min": 355.25,
        "lon_max": 355.51,
    },
    ("TMC2", "IIRS"): {
        "lat_min": 60.0,
        "lat_max": 82.0,
        "lon_min": 354.6,
        "lon_max": 355.5,
    },
    ("IIRS", "OHRC"): {
        "lat_min": 60.25,
        "lat_max": 60.93,
        "lon_min": 355.25,
        "lon_max": 355.51,
    },
}


def find_geometry(product):
    files = list(product.glob("geometry/**/*.csv"))
    if not files:
        raise FileNotFoundError(f"No geometry CSV found: {product}")
    if len(files) != 1:
        raise RuntimeError(
            f"Expected exactly one geometry CSV for {product}, found {len(files)}"
        )
    return files[0]


def footprint(product):
    path = find_geometry(product)

    lon = []
    lat = []

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                lon.append(float(row["Longitude"]))
                lat.append(float(row["Latitude"]))
            except (ValueError, TypeError):
                continue

    return {
        "lat_min": float(np.min(lat)),
        "lat_max": float(np.max(lat)),
        "lon_min": float(np.min(lon)),
        "lon_max": float(np.max(lon)),
    }


def image_shape(sensor):
    if sensor == "OHRC":
        return (79796, 12000)
    if sensor == "TMC2":
        return (153244, 4000)
    if sensor == "IIRS":
        # Correspondence image representation is still 2-D.
        # For geometry purposes the spatial dimensions are:
        # LINE x SAMPLE.
        return (10075, 250)
    raise ValueError(sensor)


def intersect_window(a, b, requested):
    fa = footprint(PRODUCTS[a])
    fb = footprint(PRODUCTS[b])

    lat_min = max(
        requested["lat_min"],
        fa["lat_min"],
        fb["lat_min"],
    )
    lat_max = min(
        requested["lat_max"],
        fa["lat_max"],
        fb["lat_max"],
    )

    lon_min = max(
        requested["lon_min"],
        fa["lon_min"],
        fb["lon_min"],
    )
    lon_max = min(
        requested["lon_max"],
        fa["lon_max"],
        fb["lon_max"],
    )

    if lat_min >= lat_max or lon_min >= lon_max:
        raise RuntimeError(
            f"No valid interior overlap for {a}-{b}: "
            f"lat={lat_min}..{lat_max}, "
            f"lon={lon_min}..{lon_max}"
        )

    return lat_min, lat_max, lon_min, lon_max


def sample_anchors(lat_min, lat_max, lon_min, lon_max,
                   n_lat=5, n_lon=5):

    lats = np.linspace(lat_min, lat_max, n_lat)
    lons = np.linspace(lon_min, lon_max, n_lon)

    return [
        (float(lat), float(lon))
        for lat in lats
        for lon in lons
    ]


def main():

    OUT.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("PARALLAX — P0001 THREE-SENSOR ROI DISCOVERY")
    print("=" * 80)

    loaded = {}

    for sensor, product in PRODUCTS.items():
        geometry_file = find_geometry(product)
        loaded[sensor] = load_geometry(geometry_file)

        print(
            f"{sensor:5s} | "
            f"geometry={geometry_file.name}"
        )

    manifest = {
        "dataset": "P0001",
        "pairs": [],
    }

    for a, b in PAIRS:

        print("\n" + "=" * 80)
        print(f"{a} <-> {b}")
        print("=" * 80)

        lat_min, lat_max, lon_min, lon_max = intersect_window(
            a, b, PAIR_WINDOWS[(a, b)]
        )

        print(
            f"Interior overlap:\n"
            f"  latitude  {lat_min:.6f} -> {lat_max:.6f}\n"
            f"  longitude {lon_min:.6f} -> {lon_max:.6f}"
        )

        anchors = sample_anchors(
            lat_min,
            lat_max,
            lon_min,
            lon_max,
        )

        pair_dir = OUT / f"{a}_{b}"
        pair_dir.mkdir(parents=True, exist_ok=True)

        pair_records = []

        for idx, (lat, lon) in enumerate(anchors, start=1):

            try:
                scan_a, pixel_a = geo_to_pixel(
                    loaded[a],
                    lat,
                    lon,
                )

                scan_b, pixel_b = geo_to_pixel(
                    loaded[b],
                    lat,
                    lon,
                )

            except Exception as exc:
                print(
                    f"  Anchor {idx:02d}: FAILED "
                    f"({lat:.6f}, {lon:.6f}) -> {exc}"
                )
                continue

            h_a, w_a = image_shape(a)
            h_b, w_b = image_shape(b)

            valid = (
                0 <= scan_a < h_a and
                0 <= pixel_a < w_a and
                0 <= scan_b < h_b and
                0 <= pixel_b < w_b
            )

            record = {
                "anchor_id": idx,
                "latitude": lat,
                "longitude": lon,

                "sensor_a": a,
                "scan_a": float(scan_a),
                "pixel_a": float(pixel_a),

                "sensor_b": b,
                "scan_b": float(scan_b),
                "pixel_b": float(pixel_b),

                "valid": bool(valid),
            }

            pair_records.append(record)

            status = "OK" if valid else "OUT_OF_BOUNDS"

            print(
                f"  Anchor {idx:02d}: {status} | "
                f"geo=({lat:.6f}, {lon:.6f}) | "
                f"{a}=({scan_a:.2f},{pixel_a:.2f}) | "
                f"{b}=({scan_b:.2f},{pixel_b:.2f})"
            )

        pair_manifest = {
            "pair": f"{a}_{b}",
            "latitude_range": [lat_min, lat_max],
            "longitude_range": [lon_min, lon_max],
            "anchors": pair_records,
        }

        with open(
            pair_dir / "anchors.json",
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(pair_manifest, f, indent=2)

        valid_count = sum(r["valid"] for r in pair_records)

        print(
            f"\nVALID ANCHORS: {valid_count}/{len(pair_records)}"
        )

        manifest["pairs"].append(pair_manifest)

    with open(
        OUT / "roi_manifest.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(manifest, f, indent=2)

    print("\n" + "=" * 80)
    print("ROI DISCOVERY COMPLETE")
    print("=" * 80)
    print(f"Output: {OUT.resolve()}")


if __name__ == "__main__":
    main()
