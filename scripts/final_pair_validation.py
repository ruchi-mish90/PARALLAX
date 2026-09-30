from pathlib import Path
import sys

ROOT = Path(r"C:\Users\graj6\Downloads\parallex")
sys.path.insert(0, str(ROOT / "src"))

from parallex.overlap.geometry import load_geometry
from parallex.overlap.spatial import spatial_co_location


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


def find_csv(product):
    files = sorted(product.rglob("*.csv"))

    preferred = [
        p for p in files
        if "grd" in p.name.lower()
        or "geometry" in p.name.lower()
    ]

    if not preferred:
        raise FileNotFoundError(
            f"No geometry CSV found under {product}"
        )

    return preferred[0]


grids = {}

print("=" * 80)
print("LOADING ACTUAL PDS4 GEOMETRY")
print("=" * 80)

for name, product in PRODUCTS.items():

    try:

        csv_path = find_csv(product)
        grid = load_geometry(csv_path)

        grids[name] = grid

        print(
            f"{name:12s} "
            f"shape={grid.latitude.shape} "
            f"file={csv_path.name}"
        )

    except Exception as e:

        print(
            f"{name:12s} ERROR "
            f"{type(e).__name__}: {e}"
        )


pairs = [
    ("P0001", "OHRC_2020", "TMC2_P0001"),
    ("P0004", "OHRC_2025", "TMC2_NCN"),
    ("P0005", "OHRC_2025", "TMC2_NCA"),
]


print()
print("=" * 80)
print("FINAL 3-PAIR SPATIAL VALIDATION")
print("=" * 80)

for pair_id, name_a, name_b in pairs:

    print()
    print(pair_id)
    print(
        f"  A = {name_a}"
    )
    print(
        f"  B = {name_b}"
    )

    try:

        result = spatial_co_location(
            grids[name_a],
            grids[name_b],
        )

        print(
            "  Raw result:",
            result,
        )

        # spatial_co_location currently returns a tuple.
        if isinstance(result, tuple):

            print(
                "  Tuple length:",
                len(result),
            )

            for i, value in enumerate(result):
                print(
                    f"  result[{i}] = {value}"
                )

        else:

            print(
                "  Result type:",
                type(result).__name__,
            )

            print(
                "  Attributes:",
                getattr(result, "__dict__", None),
            )

    except Exception as e:

        print(
            "  ERROR:",
            type(e).__name__,
            str(e),
        )

print()
print("=" * 80)
print("VALIDATION COMPLETE")
print("=" * 80)

