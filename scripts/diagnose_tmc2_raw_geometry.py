from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\graj6\Downloads\P0001")
TMC2_DIR = next(ROOT.glob("ch2_tmc_ncn_*"))
GEO = next(TMC2_DIR.rglob("*_g_grd_*.csv"))

print("=" * 70)
print("P0001 TMC2 RAW GEOMETRY DIAGNOSTIC")
print("=" * 70)
print("FILE:", GEO)

df = pd.read_csv(GEO)

print()
print("COLUMNS:")
print(list(df.columns))

print()
print("SHAPE:", df.shape)

print()
print("FIRST 5 ROWS:")
print(df.head().to_string())

# Find likely latitude/longitude columns.
lat_col = next(
    c for c in df.columns
    if c.lower() in (
        "latitude",
        "lat",
        "center_latitude",
    )
)

lon_col = next(
    c for c in df.columns
    if c.lower() in (
        "longitude",
        "lon",
        "center_longitude",
    )
)

print()
print("LAT COLUMN:", lat_col)
print("LON COLUMN:", lon_col)

lat = pd.to_numeric(
    df[lat_col],
    errors="coerce",
)

lon = pd.to_numeric(
    df[lon_col],
    errors="coerce",
)

valid = (
    lat.notna()
    & lon.notna()
)

print()
print("RAW LAT EXTENT:")
print(
    float(lat[valid].min()),
    "to",
    float(lat[valid].max()),
)

print()
print("RAW LON EXTENT:")
print(
    float(lon[valid].min()),
    "to",
    float(lon[valid].max()),
)

# ------------------------------------------------------------
# Direct latitude window
# ------------------------------------------------------------

mask = (
    valid
    & (lat >= 60.0)
    & (lat <= 61.2)
)

subset = df.loc[mask].copy()

print()
print(
    "RAW ROWS WITH LAT 60.0–61.2:",
    len(subset),
)

if len(subset):

    print()
    print(
        "LONGITUDE RANGE IN THAT LATITUDE WINDOW:"
    )

    slon = pd.to_numeric(
        subset[lon_col],
        errors="coerce",
    )

    print(
        float(slon.min()),
        "to",
        float(slon.max()),
    )

    print()
    print(
        "ROWS NEAR EXPECTED OHRC LONGITUDE 355.x:"
    )

    near = subset[
        (
            (
                (
                    slon - 355.38 + 180
                ) % 360
            ) - 180
        ).abs() < 1.0
    ]

    print(
        "COUNT:",
        len(near),
    )

    if len(near):

        print(
            near.head(20).to_string()
        )

    else:

        print(
            "NO RAW TMC2 ROWS NEAR 355.38°"
        )

else:

    print(
        "NO RAW TMC2 ROWS AT LATITUDE 60–61.2"
    )

# ------------------------------------------------------------
# Show rows nearest expected geographic point
# ------------------------------------------------------------

target_lat = 60.5923
target_lon = 355.38

dlat = lat - target_lat

dlon = (
    (
        lon
        - target_lon
        + 180
    ) % 360
) - 180

score = (
    dlat * dlat
    + (
        dlon
        * np.cos(
            np.deg2rad(
                target_lat
            )
        )
    ) ** 2
)

score = score.where(valid)

nearest = score.nsmallest(10).index

print()
print(
    "10 RAW TMC2 ROWS NEAREST TO"
    f" ({target_lat}, {target_lon}):"
)

print(
    df.loc[nearest].to_string()
)

