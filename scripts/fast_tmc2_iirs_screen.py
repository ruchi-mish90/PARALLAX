from pathlib import Path
import numpy as np
import cv2
import json

from parallex.io.pds4_image import open_pds4_image


ROOT = Path(r"C:\Users\graj6\Downloads\P0001")
OUT = Path("results/P0001_TMC2_IIRS_FAST")
OUT.mkdir(parents=True, exist_ok=True)

TMC_DIR = next(ROOT.glob("ch2_tmc_ncn_*"))
IIR_DIR = next(ROOT.glob("ch2_iir_nci_*"))

TMC_GEO = next(TMC_DIR.rglob("*_g_grd_*.csv"))
IIR_GEO = next(IIR_DIR.rglob("*_g_grd_*.csv"))

print("=" * 70)
print("PARALLAX REAL P0001 — TMC2 ↔ IIRS FAST SCREEN")
print("=" * 70)

print("TMC2 GEO:", TMC_GEO)
print("IIRS GEO:", IIR_GEO)

# ------------------------------------------------------------
# RAW GEOMETRY
# ------------------------------------------------------------

tm = np.genfromtxt(
    TMC_GEO,
    delimiter=",",
    names=True,
    dtype=None,
    encoding="utf-8",
)

ii = np.genfromtxt(
    IIR_GEO,
    delimiter=",",
    names=True,
    dtype=None,
    encoding="utf-8",
)

def col(a, name):
    return np.asarray(
        a[name],
        dtype=np.float64,
    )

tm_lon = col(tm, "Longitude")
tm_lat = col(tm, "Latitude")
tm_pix = col(tm, "Pixel")
tm_scan = col(tm, "Scan")

ii_lon = col(ii, "Longitude")
ii_lat = col(ii, "Latitude")
ii_pix = col(ii, "Pixel")
ii_scan = col(ii, "Scan")

tm_valid = (
    np.isfinite(tm_lat)
    & np.isfinite(tm_lon)
)

ii_valid = (
    np.isfinite(ii_lat)
    & np.isfinite(ii_lon)
)

tm_lon = tm_lon[tm_valid]
tm_lat = tm_lat[tm_valid]
tm_pix = tm_pix[tm_valid]
tm_scan = tm_scan[tm_valid]

ii_lon = ii_lon[ii_valid]
ii_lat = ii_lat[ii_valid]
ii_pix = ii_pix[ii_valid]
ii_scan = ii_scan[ii_valid]

print("TMC2 geometry:", len(tm_lat))
print("IIRS geometry:", len(ii_lat))

print(
    "TMC2:",
    tm_lat.min(),
    tm_lat.max(),
    tm_lon.min(),
    tm_lon.max(),
)

print(
    "IIRS:",
    ii_lat.min(),
    ii_lat.max(),
    ii_lon.min(),
    ii_lon.max(),
)

# ------------------------------------------------------------
# FIND IIRS -> TMC2 GEOGRAPHIC CORRESPONDENCES
# ------------------------------------------------------------

def dist2(
    lat0,
    lon0,
    lat,
    lon,
):

    dlat = lat - lat0

    dlon = (
        (lon - lon0 + 180.0)
        % 360.0
    ) - 180.0

    scale = np.cos(
        np.deg2rad(lat0)
    )

    return (
        dlat * dlat
        + (dlon * scale) ** 2
    )


# Use IIRS points as anchors.
# They are sparse, so select every ~25th point.
step = max(
    1,
    len(ii_lat) // 500,
)

anchors = np.arange(
    0,
    len(ii_lat),
    step,
)

pairs = []

for k in anchors:

    lat0 = ii_lat[k]
    lon0 = ii_lon[k]

    d2 = dist2(
        lat0,
        lon0,
        tm_lat,
        tm_lon,
    )

    j = int(
        np.argmin(d2)
    )

    err = float(
        np.sqrt(d2[j])
    )

    if err < 0.03:

        pairs.append(
            (
                err,
                k,
                j,
            )
        )

print()
print(
    "IIRS anchors:",
    len(anchors),
)

print(
    "TMC2/IIRS pairs < 0.03 deg:",
    len(pairs),
)

if not pairs:

    best = min(
        (
            (
                float(
                    np.sqrt(
                        dist2(
                            ii_lat[k],
                            ii_lon[k],
                            tm_lat,
                            tm_lon,
                        ).min()
                    )
                ),
                k,
            )
            for k in anchors
        ),
        key=lambda x: x[0],
    )

    print(
        "Minimum geographic error:",
        best[0],
    )

    raise RuntimeError(
        "No TMC2/IIRS geographic pairs found."
    )

# ------------------------------------------------------------
# SPATIAL DIVERSITY
# ------------------------------------------------------------

pairs.sort(
    key=lambda x: x[0]
)

selected = []

for err, k, j in pairs:

    lat = ii_lat[k]
    lon = ii_lon[k]

    duplicate = False

    for _, pk, _ in selected:

        d = np.sqrt(
            dist2(
                lat,
                lon,
                ii_lat[pk],
                ii_lon[pk],
            )
        )

        if d < 0.05:

            duplicate = True
            break

    if duplicate:
        continue

    selected.append(
        (err, k, j)
    )

    if len(selected) >= 12:
        break

print(
    "Spatial candidates:",
    len(selected),
)

# ------------------------------------------------------------
# OPEN PRODUCTS
# ------------------------------------------------------------

tm_reader = open_pds4_image(TMC_DIR)
ii_reader = open_pds4_image(IIR_DIR)

print("TMC2 image:", tm_reader.shape)
print("IIRS cube:", ii_reader.shape)

# ------------------------------------------------------------
# NORMALIZATION
# ------------------------------------------------------------

def norm(x):

    x = np.asarray(
        x,
        dtype=np.float32,
    )

    x = np.nan_to_num(
        x,
        nan=0,
        posinf=0,
        neginf=0,
    )

    lo, hi = np.percentile(
        x,
        [2, 98],
    )

    if hi <= lo:
        return np.zeros(
            x.shape,
            dtype=np.uint8,
        )

    return (
        np.clip(
            (x - lo)
            / (hi - lo),
            0,
            1,
        )
        * 255
    ).astype(np.uint8)


def edges(x):

    x = norm(x)

    return cv2.Canny(
        x,
        30,
        100,
    )


def corr(a, b):

    a = a.astype(
        np.float32
    ).ravel()

    b = b.astype(
        np.float32
    ).ravel()

    if (
        a.std() == 0
        or b.std() == 0
    ):
        return 0.0

    return float(
        np.corrcoef(a, b)[0, 1]
    )


# ------------------------------------------------------------
# REPRESENT IIRS
# ------------------------------------------------------------

def iirs_patch(
    scan,
    pixel,
    size=15,
):

    half = size // 2

    rows = []

    for band in range(
        0,
        ii_reader.shape[0],
    ):

        r = ii_reader.read_band_window(
            band,
            max(0, int(scan) - half),
            max(0, int(pixel) - half),
            size,
            size,
        )

        rows.append(r)

    return np.stack(
        rows,
        axis=0,
    )


def spectral_mean(cube):

    return np.mean(
        cube,
        axis=0,
    )


def spectral_gradient(cube):

    return np.mean(
        np.abs(
            np.diff(
                cube,
                axis=0,
            )
        ),
        axis=0,
    )


# ------------------------------------------------------------
# SCREEN
# ------------------------------------------------------------

results = []

for n, (
    geo_err,
    ik,
    tk,
) in enumerate(
    selected,
    1,
):

    i_scan = ii_scan[ik]
    i_pix = ii_pix[ik]

    t_scan = tm_scan[tk]
    t_pix = tm_pix[tk]

    print()
    print("-" * 70)

    print(
        f"A{n:02d}",
        "geo_error=",
        f"{geo_err:.6f}",
    )

    print(
        "IIRS:",
        f"({i_scan:.0f},{i_pix:.0f})",
        "geo=(",
        f"{ii_lat[ik]:.6f},",
        f"{ii_lon[ik]:.6f})",
    )

    print(
        "TMC2:",
        f"({t_scan:.0f},{t_pix:.0f})",
        "geo=(",
        f"{tm_lat[tk]:.6f},",
        f"{tm_lon[tk]:.6f})",
    )

    try:

        # TMC2 ~5 m/px, IIRS ~80 m/px.
        # Use ~17x spatial scale ratio.
        tm_half = 150
        ii_size = 21

        tm_roi = tm_reader.read_window(
            max(
                0,
                int(t_scan) - tm_half,
            ),
            max(
                0,
                int(t_pix) - tm_half,
            ),
            2 * tm_half + 1,
            2 * tm_half + 1,
        )

        cube = iirs_patch(
            i_scan,
            i_pix,
            ii_size,
        )

        rep_mean = spectral_mean(
            cube
        )

        rep_grad = spectral_gradient(
            cube
        )

        # Resize IIRS representation to TMC2 ROI.
        t_shape = (
            tm_roi.shape[1],
            tm_roi.shape[0],
        )

        mean_up = cv2.resize(
            rep_mean,
            t_shape,
            interpolation=cv2.INTER_CUBIC,
        )

        grad_up = cv2.resize(
            rep_grad,
            t_shape,
            interpolation=cv2.INTER_CUBIC,
        )

        tm_edge = edges(
            tm_roi
        )

        mean_edge = edges(
            mean_up
        )

        grad_edge = edges(
            grad_up
        )

        intensity_mean = corr(
            norm(tm_roi),
            norm(mean_up),
        )

        edge_mean = corr(
            tm_edge,
            mean_edge,
        )

        edge_grad = corr(
            tm_edge,
            grad_edge,
        )

        structural = max(
            edge_mean,
            edge_grad,
        )

        print(
            "intensity_corr:",
            f"{intensity_mean:.4f}",
        )

        print(
            "edge_mean:",
            f"{edge_mean:.4f}",
        )

        print(
            "edge_gradient:",
            f"{edge_grad:.4f}",
        )

        print(
            "STRUCTURAL SCORE:",
            f"{structural:.4f}",
        )

        panel = np.hstack([
            norm(tm_roi),
            norm(mean_up),
        ])

        cv2.imwrite(
            str(
                OUT
                / f"A{n:02d}.png"
            ),
            panel,
        )

        results.append({
            "id": f"A{n:02d}",
            "geo_error": geo_err,
            "iirs_scan": float(i_scan),
            "iirs_pixel": float(i_pix),
            "tmc2_scan": float(t_scan),
            "tmc2_pixel": float(t_pix),
            "intensity_corr": intensity_mean,
            "edge_mean": edge_mean,
            "edge_gradient": edge_grad,
            "structural_score": structural,
        })

    except Exception as e:

        print(
            "ERROR:",
            type(e).__name__,
            str(e),
        )


results.sort(
    key=lambda x:
        x["structural_score"],
    reverse=True,
)

with open(
    OUT / "candidates.json",
    "w",
    encoding="utf-8",
) as f:

    json.dump(
        results,
        f,
        indent=2,
    )

print()
print("=" * 70)
print("TMC2 ↔ IIRS CANDIDATE RANKING")
print("=" * 70)

for r in results:

    print(
        r["id"],
        "structural=",
        f"{r['structural_score']:.4f}",
        "edge=",
        f"{max(r['edge_mean'], r['edge_gradient']):.4f}",
        "geo=",
        f"{r['geo_error']:.5f}",
    )

print()
print(
    "OUTPUT:",
    OUT.resolve(),
)
