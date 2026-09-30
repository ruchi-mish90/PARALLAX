r"""
PARALLAX — P0001 cross-sensor adaptation / router training.

IMPORTANT:
This script intentionally uses ONLY these three products:
1) IIRS  : C:\Users\graj6\Downloads\P0001\ch2_iir_nci_20221209T1908498944_d_img_n18
2) OHRC  : C:\Users\graj6\Downloads\P0001\ch2_ohr_ncp_20250612T2031048828_d_img_d18
3) TMC2  : C:\Users\graj6\Downloads\P0001\ch2_tmc_ncn_20230605T1503198538_d_img_n18

It does NOT discover or use any other dataset.

What it builds:
- a manifest for the three allowed products
- pair records for OHRC↔TMC2, TMC2↔IIRS, OHRC↔IIRS
- feature vectors for router training
- optional matcher scores if the existing PARALLAX pipeline can be imported
- a lightweight RandomForest matcher router

Because only three real products are in scope, this is a P0001-specific
cross-sensor adaptation/benchmark, not a general lunar model.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from itertools import combinations

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------
# HARD DATA BOUNDARY — DO NOT ADD DATASETS HERE
# ---------------------------------------------------------------------
ALLOWED = {
    "IIRS": Path(
        r"C:\Users\graj6\Downloads\P0001\ch2_iir_nci_20221209T1908498944_d_img_n18"
    ),
    "OHRC": Path(
        r"C:\Users\graj6\Downloads\P0001\ch2_ohr_ncp_20250612T2031048828_d_img_d18"
    ),
    "TMC2": Path(
        r"C:\Users\graj6\Downloads\P0001\ch2_tmc_ncn_20230605T1503198538_d_img_n18"
    ),
}

OUT = Path("results") / "P0001_CROSS_SENSOR_TRAINING"

PAIR_TYPES = [
    ("OHRC", "TMC2"),
    ("TMC2", "IIRS"),
    ("OHRC", "IIRS"),
]

MATCHERS = ["sift", "hopc", "cfog", "loftr", "superpoint_lightglue"]


def assert_only_allowed():
    missing = [f"{k}: {v}" for k, v in ALLOWED.items() if not v.exists()]
    if missing:
        raise FileNotFoundError(
            "Required allowed product path(s) missing:\n" + "\n".join(missing)
        )

    # Fail closed: only inspect files below the three exact roots.
    for sensor, root in ALLOWED.items():
        for p in root.rglob("*"):
            if p.is_file() and not str(p.resolve()).lower().startswith(
                str(root.resolve()).lower()
            ):
                raise RuntimeError(f"Dataset boundary violation: {p}")


def discover_product(sensor: str, root: Path) -> dict:
    files = [p for p in root.rglob("*") if p.is_file()]

    def first_matching(patterns):
        for pat in patterns:
            hits = [p for p in files if re.search(pat, p.name, re.I)]
            if hits:
                return sorted(hits, key=lambda x: len(str(x)))[0]
        return None

    xml = first_matching([r"\.xml$"])
    geometry = first_matching([r"g_grd", r"geometry", r"calibrated.*\.csv$", r"\.csv$"])
    browse = first_matching(
        [
            r"browse.*calibrated.*\.(png|jpg|jpeg)$",
            r"browse.*\.(png|jpg|jpeg)$",
            r"calibrated.*\.(png|jpg|jpeg)$",
        ]
    )
    image = first_matching(
        [
            r"\.(img|dat|bin)$",
            r"\.(tif|tiff)$",
            r"\.(png|jpg|jpeg)$",
        ]
    )

    return {
        "sensor": sensor,
        "root": str(root),
        "label": str(xml) if xml else None,
        "geometry": str(geometry) if geometry else None,
        "browse_image": str(browse) if browse else None,
        "image": str(image) if image else None,
        "file_count": len(files),
    }


def geometry_summary(path: str | None) -> dict:
    if not path:
        return {"rows": 0}

    try:
        df = pd.read_csv(path)
    except Exception:
        return {"rows": 0, "error": "geometry CSV unreadable"}

    # Normalize names so we can recognize the documented lon/lat/scan/pixel grid.
    cols = {str(c).strip().lower(): c for c in df.columns}

    def find(*names):
        for n in names:
            if n in cols:
                return cols[n]
        return None

    lon = find("longitude", "lon", "long")
    lat = find("latitude", "lat")
    scan = find("scan", "line", "row")
    pix = find("pixel", "pix", "column", "col")

    out = {"rows": int(len(df)), "columns": [str(c) for c in df.columns]}

    if lon and lat:
        x = pd.to_numeric(df[lon], errors="coerce").to_numpy()
        y = pd.to_numeric(df[lat], errors="coerce").to_numpy()
        good = np.isfinite(x) & np.isfinite(y)
        if good.any():
            out["lon_min"] = float(x[good].min())
            out["lon_max"] = float(x[good].max())
            out["lat_min"] = float(y[good].min())
            out["lat_max"] = float(y[good].max())

    if scan:
        v = pd.to_numeric(df[scan], errors="coerce")
        out["scan_min"] = float(v.min())
        out["scan_max"] = float(v.max())

    if pix:
        v = pd.to_numeric(df[pix], errors="coerce")
        out["pixel_min"] = float(v.min())
        out["pixel_max"] = float(v.max())

    return out


def overlap_features(a: dict, b: dict) -> dict:
    """Geometry-only pair features. Missing geometry is represented explicitly."""
    if not all(k in a for k in ("lon_min", "lon_max", "lat_min", "lat_max")):
        return {"overlap_ratio": 0.0, "lon_overlap": 0.0, "lat_overlap": 0.0}
    if not all(k in b for k in ("lon_min", "lon_max", "lat_min", "lat_max")):
        return {"overlap_ratio": 0.0, "lon_overlap": 0.0, "lat_overlap": 0.0}

    lon_lo = max(a["lon_min"], b["lon_min"])
    lon_hi = min(a["lon_max"], b["lon_max"])
    lat_lo = max(a["lat_min"], b["lat_min"])
    lat_hi = min(a["lat_max"], b["lat_max"])

    lon_overlap = max(0.0, lon_hi - lon_lo)
    lat_overlap = max(0.0, lat_hi - lat_lo)

    aw = max(1e-12, a["lon_max"] - a["lon_min"])
    ah = max(1e-12, a["lat_max"] - a["lat_min"])
    bw = max(1e-12, b["lon_max"] - b["lon_min"])
    bh = max(1e-12, b["lat_max"] - b["lat_min"])

    inter = lon_overlap * lat_overlap
    union = aw * ah + bw * bh - inter

    return {
        "lon_overlap": lon_overlap,
        "lat_overlap": lat_overlap,
        "overlap_ratio": float(inter / max(union, 1e-12)),
    }


def image_stats(path: str | None) -> dict:
    if not path:
        return {"available": 0}

    p = Path(path)
    out = {"available": 1, "suffix": p.suffix.lower(), "bytes": p.stat().st_size}

    # PNG/JPEG/TIFF can be inspected without changing the dataset.
    try:
        from PIL import Image

        with Image.open(p) as im:
            out["width"], out["height"] = im.size
            out["mode"] = im.mode
    except Exception:
        pass

    return out


def build_manifest():
    OUT.mkdir(parents=True, exist_ok=True)

    products = {}
    for sensor, root in ALLOWED.items():
        p = discover_product(sensor, root)
        p["geometry_summary"] = geometry_summary(p["geometry"])
        p["image_stats"] = image_stats(p["browse_image"] or p["image"])
        products[sensor] = p

    with open(OUT / "allowed_products.json", "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2)

    rows = []
    for a, b in PAIR_TYPES:
        ga = products[a]["geometry_summary"]
        gb = products[b]["geometry_summary"]
        ov = overlap_features(ga, gb)

        rows.append(
            {
                "sensor_a": a,
                "sensor_b": b,
                "product_a": products[a]["root"],
                "product_b": products[b]["root"],
                "geometry_a": products[a]["geometry"],
                "geometry_b": products[b]["geometry"],
                **ov,
                "image_a": products[a]["browse_image"] or products[a]["image"],
                "image_b": products[b]["browse_image"] or products[b]["image"],
            }
        )

    pairs = pd.DataFrame(rows)
    pairs.to_csv(OUT / "pair_manifest.csv", index=False)
    return products, pairs


def characterize_image_pair(path_a: str, path_b: str) -> dict:
    """
    Image-level statistics for router features.
    This is intentionally lightweight; the actual registration pipeline remains
    responsible for geometric verification.
    """
    from PIL import Image, ImageOps

    def load_gray(path):
        im = Image.open(path).convert("L")
        # Keep benchmark fast and deterministic.
        im.thumbnail((1600, 1600))
        return np.asarray(im, dtype=np.float32) / 255.0

    a = load_gray(path_a)
    b = load_gray(path_b)

    def stats(x):
        gx = np.diff(x, axis=1)
        gy = np.diff(x, axis=0)
        g = np.sqrt(gx[:-1, :] ** 2 + gy[:, :-1] ** 2)
        hist, _ = np.histogram(x, bins=32, range=(0, 1), density=True)
        hist = hist / max(hist.sum(), 1e-12)
        entropy = float(-(hist[hist > 0] * np.log(hist[hist > 0])).sum())
        return {
            "mean": float(x.mean()),
            "std": float(x.std()),
            "entropy": entropy,
            "edge_density": float((g > np.percentile(g, 75)).mean()),
        }

    sa, sb = stats(a), stats(b)

    # Correlation on resized common shape.
    h = min(a.shape[0], b.shape[0])
    w = min(a.shape[1], b.shape[1])
    aa = a[:h, :w].ravel()
    bb = b[:h, :w].ravel()
    corr = float(np.corrcoef(aa, bb)[0, 1]) if aa.std() and bb.std() else 0.0

    return {
        "mean_abs_intensity_delta": abs(sa["mean"] - sb["mean"]),
        "std_ratio": min(sa["std"], sb["std"]) / max(sa["std"], sb["std"], 1e-8),
        "entropy_delta": abs(sa["entropy"] - sb["entropy"]),
        "edge_density_delta": abs(sa["edge_density"] - sb["edge_density"]),
        "global_corr": corr,
    }


def add_image_features(products, pairs):
    rows = []
    for _, r in pairs.iterrows():
        rec = r.to_dict()
        pa = rec["image_a"]
        pb = rec["image_b"]

        if pa and pb and Path(pa).exists() and Path(pb).exists():
            try:
                rec.update(characterize_image_pair(pa, pb))
            except Exception as e:
                rec["feature_error"] = str(e)
        else:
            rec.update(
                {
                    "mean_abs_intensity_delta": np.nan,
                    "std_ratio": np.nan,
                    "entropy_delta": np.nan,
                    "edge_density_delta": np.nan,
                    "global_corr": np.nan,
                }
            )

        rows.append(rec)

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "router_features.csv", index=False)
    return df


def train_router(score_csv: Path):
    """
    Train a lightweight matcher router from measured benchmark results.

    score_csv must contain:
      pair_id, matcher, quality_score

    quality_score should be produced by the existing PARALLAX quality model,
    not invented here.
    """
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import LeaveOneOut, cross_val_score
    from sklearn.preprocessing import LabelEncoder
    import joblib

    feats = pd.read_csv(OUT / "router_features.csv")
    scores = pd.read_csv(score_csv)

    # Best measured matcher per pair.
    best = (
        scores.sort_values(["pair_id", "quality_score"], ascending=[True, False])
        .groupby("pair_id", as_index=False)
        .first()[["pair_id", "matcher"]]
    )

    feats["pair_id"] = feats.apply(lambda r: f"{r.sensor_a}_{r.sensor_b}", axis=1)
    train = feats.merge(best, on="pair_id", how="inner")

    feature_cols = [
        "overlap_ratio",
        "lon_overlap",
        "lat_overlap",
        "mean_abs_intensity_delta",
        "std_ratio",
        "entropy_delta",
        "edge_density_delta",
        "global_corr",
    ]

    X = train[feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    y = train["matcher"].astype(str)

    enc = LabelEncoder()
    yy = enc.fit_transform(y)

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=6,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X, yy)

    joblib.dump(
        {"model": model, "label_encoder": enc, "features": feature_cols},
        OUT / "p0001_matcher_router.joblib",
    )

    with open(OUT / "router_training_summary.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "scope": "P0001 only",
                "samples": int(len(train)),
                "classes": enc.classes_.tolist(),
                "features": feature_cols,
                "warning": "Three real products provide very few independent pair samples; treat this as proof-of-concept adaptation, not a general lunar model.",
            },
            f,
            indent=2,
        )

    return train


def main():
    print("\n=== PARALLAX P0001 CROSS-SENSOR TRAINING ===")
    print("DATA SCOPE: ONLY IIRS + OHRC + TMC2 specified P0001 products\n")

    assert_only_allowed()

    products, pairs = build_manifest()

    print("Allowed products:")
    for s, p in products.items():
        print(f"  {s}: {p['root']}")
        print(f"      geometry: {p['geometry']}")
        print(f"      image:    {p['browse_image'] or p['image']}")

    print("\nPair types:")
    for _, r in pairs.iterrows():
        print(f"  {r.sensor_a} <-> {r.sensor_b} | " f"overlap={r.overlap_ratio:.6f}")

    feats = add_image_features(products, pairs)
    print(f"\nWrote router features: {OUT / 'router_features.csv'}")

    print(
        "\nNEXT EXECUTION STAGE:\n"
        "Run the existing PARALLAX registration pipeline on each real overlapping ROI\n"
        "for all five matchers, write pair_id/matcher/quality_score to:\n"
        f"  {OUT / 'matcher_scores.csv'}\n"
        "Then run this script with train_router() enabled.\n"
    )

    print("No other dataset is permitted by this script.")


if __name__ == "__main__":
    main()
