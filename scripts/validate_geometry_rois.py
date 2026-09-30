from pathlib import Path
import sys
import numpy as np

ROOT = Path(r"C:\Users\graj6\Downloads\parallex")
sys.path.insert(0, str(ROOT / "src"))

from parallex.overlap.geometry import load_geometry, overlap_tiles, geo_to_pixel


PRODUCT_A = ROOT / r"data\real_pairs\ch2_tmc_nca_20221209T2305274611_d_img_d32"
PRODUCT_B = ROOT / r"data\real_pairs\ch2_tmc_ncn_20221209T2305274611_d_img_d32"


def find_csv(p):
    files = sorted(p.rglob("*.csv"))
    preferred = [
        x for x in files
        if any(k in x.name.lower() for k in ("geometry", "geom", "grd"))
    ]
    if not preferred:
        raise FileNotFoundError(f"No geometry CSV under {p}")
    return preferred[0]


ga = load_geometry(find_csv(PRODUCT_A))
gb = load_geometry(find_csv(PRODUCT_B))

print("=" * 80)
print("PARALLAX GEOMETRY -> PIXEL VALIDATION")
print("=" * 80)

print("A geometry:", ga.latitude.shape)
print("B geometry:", gb.latitude.shape)

tiles = overlap_tiles(
    ga,
    gb,
    latitude_min=0.0,
    latitude_max=90.0,
    longitude_intervals=[(0.0, 360.0)],
    tile_size=2048,
    samples_lat=4,
    samples_lon=4,
)

print("Candidate tiles:", len(tiles))
print()

for i, (ra, rb, lat, lon) in enumerate(tiles, 1):

    try:
        pa = geo_to_pixel(ga, lat, lon)
        pb = geo_to_pixel(gb, lat, lon)

        ay, ax = float(pa[0]), float(pa[1])
        by, bx = float(pb[0]), float(pb[1])

        center_a = (
            (ra.y0 + ra.y1) / 2,
            (ra.x0 + ra.x1) / 2,
        )

        center_b = (
            (rb.y0 + rb.y1) / 2,
            (rb.x0 + rb.x1) / 2,
        )

        error_a = np.hypot(
            ay - center_a[0],
            ax - center_a[1],
        )

        error_b = np.hypot(
            by - center_b[0],
            bx - center_b[1],
        )

        print(
            f"TILE {i}: "
            f"lat={lat:.4f}, lon={lon:.4f} | "
            f"A geo->px=({ay:.1f},{ax:.1f}) "
            f"center=({center_a[0]:.1f},{center_a[1]:.1f}) "
            f"err={error_a:.1f}px | "
            f"B geo->px=({by:.1f},{bx:.1f}) "
            f"center=({center_b[0]:.1f},{center_b[1]:.1f}) "
            f"err={error_b:.1f}px"
        )

    except Exception as e:
        print(f"TILE {i}: VALIDATION ERROR: {type(e).__name__}: {e}")

print()
print("=" * 80)
print("VALIDATION COMPLETE")
print("=" * 80)
