from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from parallex.overlap.geometry import load_geometry, geo_to_pixel, _safe_roi


PRODUCT_A = ROOT / r"data\real_pairs\ch2_tmc_nca_20221209T2305274611_d_img_d32"
PRODUCT_B = ROOT / r"data\real_pairs\ch2_tmc_ncn_20221209T2305274611_d_img_d32"


def find_csv(product):
    files = sorted(product.rglob("*.csv"))
    preferred = [
        p for p in files
        if "grd" in p.name.lower()
        or "geometry" in p.name.lower()
    ]
    return preferred[0] if preferred else files[0]


ga = load_geometry(find_csv(PRODUCT_A))
gb = load_geometry(find_csv(PRODUCT_B))

print("=" * 80)
print("PARALLAX REAL GEOMETRY OVERLAP TEST")
print("=" * 80)

print("A:", ga.latitude.shape)
print("B:", gb.latitude.shape)

# Flatten valid geometry points.
lat_a = ga.latitude.ravel()
lon_a = ga.longitude.ravel()

lat_b = gb.latitude.ravel()
lon_b = gb.longitude.ravel()

valid_a = np.isfinite(lat_a) & np.isfinite(lon_a)
valid_b = np.isfinite(lat_b) & np.isfinite(lon_b)

lat_a = lat_a[valid_a]
lon_a = lon_a[valid_a] % 360.0

lat_b = lat_b[valid_b]
lon_b = lon_b[valid_b] % 360.0

# Conservative geographic overlap.
lat_min = max(lat_a.min(), lat_b.min())
lat_max = min(lat_a.max(), lat_b.max())

print(f"Common latitude range: {lat_min:.6f} -> {lat_max:.6f}")

# Use circular longitude coverage. For these north-polar TMC2 products,
# sample longitudes from actual geometry rather than 0/120/240 assumptions.
candidate_lons = np.concatenate([
    lon_a,
    lon_b,
])

# Quantize actual observed longitudes to avoid thousands of anchors.
candidate_lons = np.unique(
    np.round(candidate_lons, 1)
)

# Restrict latitude to common range.
lat_candidates = np.linspace(
    lat_min,
    lat_max,
    5,
)

# Select longitude anchors that actually occur in BOTH datasets,
# allowing a small geographic tolerance.
selected = []

for lat in lat_candidates:

    # Find actual longitude range represented near this latitude.
    mask_a = np.abs(lat_a - lat) <= 0.75
    mask_b = np.abs(lat_b - lat) <= 0.75

    if not mask_a.any() or not mask_b.any():
        continue

    la = lon_a[mask_a]
    lb = lon_b[mask_b]

    for lon in np.linspace(0.0, 360.0, 72, endpoint=False):

        da = np.minimum(
            np.abs(la - lon),
            360.0 - np.abs(la - lon),
        )

        db = np.minimum(
            np.abs(lb - lon),
            360.0 - np.abs(lb - lon),
        )

        if da.min() <= 1.0 and db.min() <= 1.0:
            selected.append(
                (
                    float(lat),
                    float(lon),
                )
            )

# Remove duplicates.
selected = list(dict.fromkeys(selected))

print("Actual common anchor candidates:", len(selected))
print()

# Image dimensions from actual known products.
shape_a = (188585, 4000)
shape_b = (188584, 4000)

for i, (lat, lon) in enumerate(selected[:20], 1):

    scan_a, pixel_a = geo_to_pixel(
        ga,
        lat,
        lon,
    )

    scan_b, pixel_b = geo_to_pixel(
        gb,
        lat,
        lon,
    )

    roi_a = _safe_roi(
        scan_a,
        pixel_a,
        shape_a,
        2048,
    )

    roi_b = _safe_roi(
        scan_b,
        pixel_b,
        shape_b,
        2048,
    )

    inside_a = (
        roi_a[0] <= scan_a < roi_a[1]
        and roi_a[2] <= pixel_a < roi_a[3]
    )

    inside_b = (
        roi_b[0] <= scan_b < roi_b[1]
        and roi_b[2] <= pixel_b < roi_b[3]
    )

    print(
        f"{i:02d} "
        f"LAT={lat:.4f} LON={lon:.4f} | "
        f"A=({scan_a:.0f},{pixel_a:.0f}) "
        f"B=({scan_b:.0f},{pixel_b:.0f}) | "
        f"inside={inside_a}/{inside_b}"
    )

print()
print("=" * 80)
print("OVERLAP TEST COMPLETE")
print("=" * 80)
