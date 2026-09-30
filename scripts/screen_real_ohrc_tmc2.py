from pathlib import Path
import numpy as np
import cv2
import json

from parallex.overlap.geometry import load_geometry
from parallex.io.pds4_image import open_pds4_image


ROOT = Path(r"C:\Users\graj6\Downloads\P0001")
OUT = Path("results/P0001_OHRC_TMC2_SCREEN")
OUT.mkdir(parents=True, exist_ok=True)

OHRC_DIR = next(ROOT.glob("ch2_ohr_ncp_*"))
TMC2_DIR = next(ROOT.glob("ch2_tmc_ncn_*"))

OHRC_GEO = next(OHRC_DIR.rglob("*_g_grd_*.csv"))
TMC2_GEO = next(TMC2_DIR.rglob("*_g_grd_*.csv"))


print("=" * 70)
print("PARALLAX REAL P0001 — OHRC ↔ TMC2 CANDIDATE SCREEN")
print("=" * 70)


# ------------------------------------------------------------
# LOAD
# ------------------------------------------------------------

oh_geo = load_geometry(OHRC_GEO)
tm_geo = load_geometry(TMC2_GEO)

oh = open_pds4_image(OHRC_DIR)
tm = open_pds4_image(TMC2_DIR)

print("OHRC image:", oh.shape)
print("TMC2 image:", tm.shape)


# ------------------------------------------------------------
# GEOMETRY
#
# GeometryGrid:
#   latitude  -> [scan, pixel]
#   longitude -> [scan, pixel]
#   scan_values  -> scan axis
#   pixel_values -> pixel axis
# ------------------------------------------------------------

def geometry_points(g):

    lat = np.asarray(
        g.latitude,
        dtype=np.float64,
    )

    lon = np.asarray(
        g.longitude,
        dtype=np.float64,
    )

    scans = np.asarray(
        g.scan_values,
        dtype=np.float64,
    )

    pixels = np.asarray(
        g.pixel_values,
        dtype=np.float64,
    )

    print(
        "geometry grid:",
        lat.shape,
        "scan axis:",
        len(scans),
        "pixel axis:",
        len(pixels),
    )

    expected = (
        len(scans),
        len(pixels),
    )

    if lat.shape != expected:
        raise RuntimeError(
            f"Latitude shape {lat.shape} "
            f"!= expected {expected}"
        )

    if lon.shape != expected:
        raise RuntimeError(
            f"Longitude shape {lon.shape} "
            f"!= expected {expected}"
        )

    scan_grid = np.broadcast_to(
        scans[:, None],
        lat.shape,
    )

    pixel_grid = np.broadcast_to(
        pixels[None, :],
        lat.shape,
    )

    valid = (
        np.isfinite(lat)
        & np.isfinite(lon)
    )

    return (
        lat[valid],
        lon[valid],
        scan_grid[valid],
        pixel_grid[valid],
    )


ohl, onl, osl, opl = geometry_points(oh_geo)
thl, tnl, tsl, tpl = geometry_points(tm_geo)


print()
print("OHRC geometry points:", len(ohl))
print("TMC2 geometry points:", len(thl))

print(
    "OHRC latitude:",
    float(np.min(ohl)),
    "to",
    float(np.max(ohl)),
)

print(
    "OHRC longitude:",
    float(np.min(onl)),
    "to",
    float(np.max(onl)),
)

print(
    "TMC2 latitude:",
    float(np.min(thl)),
    "to",
    float(np.max(thl)),
)

print(
    "TMC2 longitude:",
    float(np.min(tnl)),
    "to",
    float(np.max(tnl)),
)


# ------------------------------------------------------------
# REAL GEOGRAPHIC OVERLAP
#
# Do NOT assume both sensors use the same longitude representation.
# Find actual TMC2 geometry samples nearest to the OHRC footprint,
# using wrapped longitude distance.
# ------------------------------------------------------------

def geo_distance_sq(
    lat_a,
    lon_a,
    lat_b,
    lon_b,
):

    dlat = lat_a - lat_b

    dlon = (
        (lon_a - lon_b + 180.0)
        % 360.0
    ) - 180.0

    scale = np.cos(
        np.deg2rad(
            (lat_a + lat_b) * 0.5
        )
    )

    return (
        dlat * dlat
        + (dlon * scale) ** 2
    )


# Use the OHRC geometry as the authoritative
# set of candidate geographic locations.

# Keep the number manageable.
oh_step = max(
    1,
    len(ohl) // 2000,
)

oh_candidates = np.arange(
    0,
    len(ohl),
    oh_step,
)

best_pairs = []

for oi in oh_candidates:

    lat0 = float(ohl[oi])
    lon0 = float(onl[oi])

    d2 = geo_distance_sq(
        lat0,
        lon0,
        thl,
        tnl,
    )

    ti = int(
        np.argmin(d2)
    )

    best_pairs.append(
        (
            float(d2[ti]),
            oi,
            ti,
        )
    )


best_pairs.sort(
    key=lambda x: x[0]
)


# Reject candidates that are obviously geographically
# unrelated. Threshold is intentionally conservative
# for this fast screening stage.
MAX_GEO_ERROR_DEG = 0.05

valid_pairs = [
    x for x in best_pairs
    if np.sqrt(x[0]) <= MAX_GEO_ERROR_DEG
]


print()
print(
    "Nearest geographic OHRC?TMC2 pairs:",
    len(best_pairs),
)

print(
    "Pairs within",
    MAX_GEO_ERROR_DEG,
    "deg:",
    len(valid_pairs),
)

if not valid_pairs:

    print()
    print(
        "Minimum geographic separation:",
        np.sqrt(best_pairs[0][0]),
        "degrees",
    )

    raise RuntimeError(
        "No close geographic OHRC/TMC2 "
        "pairs were found. "
        "This is a longitude-convention issue "
        "or a genuine footprint mismatch."
    )


# Select spatially distributed candidates.
# Prefer latitude separation and geographic diversity.

chosen = []

seen = set()

for d2, oi, ti in valid_pairs:

    lat = float(ohl[oi])
    lon = float(onl[oi])

    # Avoid candidates that are almost identical
    # geographically.
    too_close = False

    for _, prev_oi, _ in chosen:

        plat = float(ohl[prev_oi])
        plon = float(onl[prev_oi])

        if np.sqrt(
            geo_distance_sq(
                lat,
                lon,
                plat,
                plon,
            )
        ) < 0.01:

            too_close = True
            break

    if too_close:
        continue

    chosen.append(
        (d2, oi, ti)
    )

    if len(chosen) >= 9:
        break


selected = chosen

print(
    "Selected candidates:",
    len(selected),
)


# ------------------------------------------------------------
# Convert selected pairs to native coordinates
# ------------------------------------------------------------

candidate_pairs = []

for n, (d2, oi, ti) in enumerate(
    selected,
    start=1,
):

    candidate_pairs.append(
        {
            "id": f"A{n:02d}",
            "latitude": float(
                ohl[oi]
            ),
            "longitude": float(
                onl[oi]
            ),
            "ohrc_scan": float(
                osl[oi]
            ),
            "ohrc_pixel": float(
                opl[oi]
            ),
            "tmc2_latitude": float(
                thl[ti]
            ),
            "tmc2_longitude": float(
                tnl[ti]
            ),
            "tmc2_scan": float(
                tsl[ti]
            ),
            "tmc2_pixel": float(
                tpl[ti]
            ),
            "geo_error": float(
                np.sqrt(d2)
            ),
        }
    )


print()
print("SELECTED GEOGRAPHIC PAIRS")

for c in candidate_pairs:

    print(
        c["id"],
        "target=(",
        f"{c['latitude']:.6f},",
        f"{c['longitude']:.6f})",
        "TMC2=(",
        f"{c['tmc2_scan']:.0f},",
        f"{c['tmc2_pixel']:.0f})",
        "geo_error=",
        f"{c['geo_error']:.6f}",
    )

# ------------------------------------------------------------
# NEAREST OHRC GEOMETRY SAMPLE
# ------------------------------------------------------------

def nearest_ohrc(lat0, lon0):

    dlat = ohl - lat0

    dlon = (
        (onl - lon0 + 180.0)
        % 360.0
    ) - 180.0

    # Approximate geographic distance.
    scale = np.cos(
        np.deg2rad(lat0)
    )

    dist2 = (
        dlat * dlat
        + (dlon * scale) ** 2
    )

    k = int(
        np.argmin(dist2)
    )

    return (
        float(osl[k]),
        float(opl[k]),
        float(ohl[k]),
        float(onl[k]),
        float(np.sqrt(dist2[k])),
    )


# ------------------------------------------------------------
# IMAGE HELPERS
# ------------------------------------------------------------

def read_roi(
    reader,
    row,
    col,
    half_row,
    half_col,
):

    row = int(round(row))
    col = int(round(col))

    r0 = max(
        0,
        row - half_row,
    )

    c0 = max(
        0,
        col - half_col,
    )

    r1 = min(
        reader.shape[0],
        row + half_row + 1,
    )

    c1 = min(
        reader.shape[1],
        col + half_col + 1,
    )

    return reader.read_window(
        r0,
        c0,
        r1 - r0,
        c1 - c0,
    )


def normalize(img):

    img = np.asarray(
        img,
        dtype=np.float32,
    )

    img = np.nan_to_num(
        img,
        nan=0.0,
        posinf=0.0,
        neginf=0.0,
    )

    lo, hi = np.percentile(
        img,
        [2, 98],
    )

    if hi <= lo:
        return np.zeros(
            img.shape,
            dtype=np.uint8,
        )

    img = (
        (img - lo)
        / (hi - lo)
    )

    return (
        np.clip(
            img,
            0,
            1,
        )
        * 255
    ).astype(
        np.uint8
    )


def edge_correlation(a, b):

    a = normalize(a)
    b = normalize(b)

    b = cv2.resize(
        b,
        (
            a.shape[1],
            a.shape[0],
        ),
        interpolation=cv2.INTER_AREA,
    )

    ea = cv2.Canny(
        a,
        30,
        100,
    )

    eb = cv2.Canny(
        b,
        30,
        100,
    )

    aa = ea.astype(
        np.float32
    ).ravel()

    bb = eb.astype(
        np.float32
    ).ravel()

    if (
        aa.std() == 0
        or bb.std() == 0
    ):
        return 0.0

    return float(
        np.corrcoef(
            aa,
            bb,
        )[0, 1]
    )


# ------------------------------------------------------------
# CANDIDATE SCREEN
# ------------------------------------------------------------

TM_HALF = 200

# OHRC/TMC2 are approximately ~20x apart.
# This is only a screening context, NOT a registration warp.
OH_HALF_ROW = 4000
OH_HALF_COL = 4000

results = []


for c in candidate_pairs:

    n = int(
        c["id"][1:]
    )

    target_lat = c["latitude"]
    target_lon = c["longitude"]

    tm_scan = c["tmc2_scan"]
    tm_pixel = c["tmc2_pixel"]

    oh_scan = c["ohrc_scan"]
    oh_pixel = c["ohrc_pixel"]

    oh_lat = target_lat
    oh_lon = target_lon

    geo_error = c["geo_error"]

    print()
    print("-" * 70)

    print(
        f"A{n:02d}",
        "target=",
        f"({target_lat:.6f}, "
        f"{target_lon:.6f})",
    )

    print(
        "TMC2:",
        f"({tm_scan:.1f}, {tm_pixel:.1f})",
    )

    print(
        "OHRC:",
        f"({oh_scan:.1f}, {oh_pixel:.1f})",
        "geo_error=",
        f"{geo_error:.6f}",
    )

    try:

        tm_roi = read_roi(
            tm,
            tm_scan,
            tm_pixel,
            TM_HALF,
            TM_HALF,
        )

        oh_roi = read_roi(
            oh,
            oh_scan,
            oh_pixel,
            OH_HALF_ROW,
            OH_HALF_COL,
        )

        oh_small = cv2.resize(
            oh_roi.astype(
                np.float32
            ),
            (
                tm_roi.shape[1],
                tm_roi.shape[0],
            ),
            interpolation=cv2.INTER_AREA,
        )

        score = edge_correlation(
            tm_roi,
            oh_small,
        )

        panel = np.hstack([
            normalize(tm_roi),
            normalize(oh_small),
        ])

        cv2.imwrite(
            str(
                OUT
                / f"A{n:02d}_comparison.png"
            ),
            panel,
        )

        result = {
            "id": f"A{n:02d}",
            "latitude": target_lat,
            "longitude": target_lon,
            "tmc2_scan": tm_scan,
            "tmc2_pixel": tm_pixel,
            "ohrc_scan": oh_scan,
            "ohrc_pixel": oh_pixel,
            "ohrc_geo_error": geo_error,
            "edge_correlation": score,
            "tmc2_shape": list(
                tm_roi.shape
            ),
            "ohrc_shape": list(
                oh_roi.shape
            ),
        }

        results.append(result)

        print(
            "TMC2 ROI:",
            tm_roi.shape,
        )

        print(
            "OHRC ROI:",
            oh_roi.shape,
        )

        print(
            "edge correlation:",
            f"{score:.6f}",
        )

    except Exception as exc:

        print(
            "ERROR:",
            type(exc).__name__,
            str(exc),
        )

        results.append({
            "id": f"A{n:02d}",
            "error":
                f"{type(exc).__name__}: {exc}",
        })


# ------------------------------------------------------------
# SAVE
# ------------------------------------------------------------

with open(
    OUT / "screening_results.json",
    "w",
    encoding="utf-8",
) as f:

    json.dump(
        results,
        f,
        indent=2,
    )


valid = [
    x
    for x in results
    if "edge_correlation" in x
]

valid.sort(
    key=lambda x:
        x["edge_correlation"],
    reverse=True,
)


print()
print("=" * 70)
print("RANKED CANDIDATES")
print("=" * 70)

for x in valid:

    print(
        x["id"],
        "edge_corr=",
        f"{x['edge_correlation']:.6f}",
        "TMC2=(",
        f"{x['tmc2_scan']:.0f},",
        f"{x['tmc2_pixel']:.0f})",
        "OHRC=(",
        f"{x['ohrc_scan']:.0f},",
        f"{x['ohrc_pixel']:.0f})",
    )


print()
print(
    "OUTPUT:",
    OUT.resolve(),
)

