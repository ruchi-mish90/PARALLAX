from pathlib import Path
import numpy as np

from parallex.overlap.geometry import load_geometry

P = Path(r"C:\Users\graj6\Downloads\P0001")

files = {
    "OHRC": next(P.rglob("*ohr*ncp*_g_grd*.csv")),
    "TMC2": next(P.rglob("*tmc*ncn*_g_grd*.csv")),
    "IIRS": next(P.rglob("*iir*nci*_g_grd*.csv")),
}

print("=" * 60)
print("PARALLAX GEOMETRY SAMPLING")
print("=" * 60)

for name, path in files.items():

    grid = load_geometry(path)

    print()
    print(name)
    print("grid:", grid.latitude.shape)

    # Horizontal sampling at middle scan
    mid_scan = grid.latitude.shape[0] // 2

    lat = grid.latitude[mid_scan]
    lon = grid.longitude[mid_scan]

    valid = np.isfinite(lat) & np.isfinite(lon)

    lat = lat[valid]
    lon = lon[valid]

    if len(lon) > 1:

        # longitude difference in degrees
        dlon = np.abs(np.diff(lon))

        print(
            "horizontal longitude step:",
            "median=", float(np.nanmedian(dlon)),
            "mean=", float(np.nanmean(dlon)),
            "max=", float(np.nanmax(dlon)),
        )

    # Vertical sampling at middle pixel
    mid_pixel = grid.longitude.shape[1] // 2

    lat2 = grid.latitude[:, mid_pixel]
    lon2 = grid.longitude[:, mid_pixel]

    valid2 = np.isfinite(lat2) & np.isfinite(lon2)

    lat2 = lat2[valid2]
    lon2 = lon2[valid2]

    if len(lat2) > 1:

        dlat = np.abs(np.diff(lat2))

        print(
            "vertical latitude step:",
            "median=", float(np.nanmedian(dlat)),
            "mean=", float(np.nanmean(dlat)),
            "max=", float(np.nanmax(dlat)),
        )

print()
print("=" * 60)
