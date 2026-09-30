from pathlib import Path
import numpy as np
import cv2
import json
import time

from parallex.io.pds4_image import open_pds4_image
from parallex.matching.sift import SIFTMatcher
from parallex.matching.rift import RIFTMatcher
from parallex.matching.hopc import HOPCMatcher
from parallex.matching.cfog import CFOGMatcher


ROOT = Path(r"C:\Users\graj6\Downloads\P0001")

TMC_DIR = next(
    ROOT.glob("ch2_tmc_ncn_*")
)

IIR_DIR = next(
    ROOT.glob("ch2_iir_nci_*")
)

TMC_GEO = next(
    TMC_DIR.rglob("*_g_grd_*.csv")
)

IIR_GEO = next(
    IIR_DIR.rglob("*_g_grd_*.csv")
)

OUT = Path(
    "results/P0001_TMC2_IIRS_MATCH"
)

OUT.mkdir(
    parents=True,
    exist_ok=True,
)


print("=" * 75)
print("PARALLAX REAL P0001 — TMC2 ↔ IIRS MATCH TEST")
print("=" * 75)


# ------------------------------------------------------------
# GEOMETRY
# ------------------------------------------------------------

def load_geo(path):

    d = np.genfromtxt(
        path,
        delimiter=",",
        names=True,
        dtype=None,
        encoding="utf-8",
    )

    return {
        "lat": np.asarray(
            d["Latitude"],
            dtype=np.float64,
        ),
        "lon": np.asarray(
            d["Longitude"],
            dtype=np.float64,
        ),
        "pixel": np.asarray(
            d["Pixel"],
            dtype=np.float64,
        ),
        "scan": np.asarray(
            d["Scan"],
            dtype=np.float64,
        ),
    }


tm = load_geo(TMC_GEO)
ii = load_geo(IIR_GEO)


def valid(g):

    m = (
        np.isfinite(g["lat"])
        & np.isfinite(g["lon"])
    )

    for k in g:
        g[k] = g[k][m]

    return g


tm = valid(tm)
ii = valid(ii)


def d2(
    lat0,
    lon0,
    lat,
    lon,
):

    dlat = lat - lat0

    dlon = (
        (lon - lon0 + 180)
        % 360
    ) - 180

    scale = np.cos(
        np.deg2rad(lat0)
    )

    return (
        dlat * dlat
        + (dlon * scale) ** 2
    )


# ------------------------------------------------------------
# USE THE BEST EXISTING P0001 GEOMETRY CANDIDATES
# ------------------------------------------------------------

anchors = []

for k in range(
    len(ii["lat"])
):

    lat0 = ii["lat"][k]
    lon0 = ii["lon"][k]

    dist = d2(
        lat0,
        lon0,
        tm["lat"],
        tm["lon"],
    )

    j = int(
        np.argmin(dist)
    )

    err = float(
        np.sqrt(dist[j])
    )

    if err < 0.005:

        anchors.append(
            (
                err,
                k,
                j,
            )
        )


anchors.sort(
    key=lambda x: x[0]
)


# Spatially separate candidates.
selected = []

for p in anchors:

    err, i, t = p

    lat = ii["lat"][i]
    lon = ii["lon"][i]

    duplicate = False

    for old in selected:

        oi = old[1]

        if np.sqrt(
            d2(
                lat,
                lon,
                ii["lat"][oi],
                ii["lon"][oi],
            )
        ) < 0.08:

            duplicate = True
            break

    if duplicate:
        continue

    selected.append(p)

    if len(selected) >= 5:
        break


print(
    "P0001 candidates:",
    len(selected),
)

for n, (err, i, t) in enumerate(
    selected,
    1,
):

    print(
        f"A{n}: "
        f"geo_error={err:.6f} "
        f"IIRS=({ii['scan'][i]:.0f},"
        f"{ii['pixel'][i]:.0f}) "
        f"TMC2=({tm['scan'][t]:.0f},"
        f"{tm['pixel'][t]:.0f})"
    )


# ------------------------------------------------------------
# OPEN REAL P0001 DATA
# ------------------------------------------------------------

tm_reader = open_pds4_image(
    TMC_DIR
)

ii_reader = open_pds4_image(
    IIR_DIR
)

print(
    "TMC2:",
    tm_reader.shape
)

print(
    "IIRS:",
    ii_reader.shape
)


# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------

def normalize(x):

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
    ).astype(
        np.uint8
    )


def clahe(x):

    x = normalize(x)

    c = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8),
    )

    return c.apply(x)


def gradient(x):

    x = x.astype(
        np.float32
    )

    gx = cv2.Sobel(
        x,
        cv2.CV_32F,
        1,
        0,
        ksize=3,
    )

    gy = cv2.Sobel(
        x,
        cv2.CV_32F,
        0,
        1,
        ksize=3,
    )

    return cv2.magnitude(
        gx,
        gy,
    )


def corr(a, b):

    a = a.astype(
        np.float32
    ).ravel()

    b = b.astype(
        np.float32
    ).ravel()

    if (
        a.std() < 1e-6
        or b.std() < 1e-6
    ):
        return 0.0

    return float(
        np.corrcoef(
            a,
            b,
        )[0, 1]
    )


# ------------------------------------------------------------
# IIRS CUBE EXTRACTION
# ------------------------------------------------------------

def read_cube(
    scan,
    pixel,
    size=61,
):

    half = size // 2

    r0 = max(
        0,
        int(scan) - half,
    )

    c0 = max(
        0,
        int(pixel) - half,
    )

    bands = []

    for b in range(
        ii_reader.shape[0]
    ):

        bands.append(
            ii_reader.read_band_window(
                b,
                r0,
                c0,
                size,
                size,
            )
        )

    return np.stack(
        bands,
        axis=0,
    )


# ------------------------------------------------------------
# PCA-1
# ------------------------------------------------------------

def pca1(cube):

    b, h, w = cube.shape

    x = cube.reshape(
        b,
        h * w,
    ).astype(
        np.float32
    )

    x = np.nan_to_num(
        x,
        nan=0,
        posinf=0,
        neginf=0,
    )

    x -= x.mean(
        axis=1,
        keepdims=True,
    )

    # covariance in spectral space
    cov = (
        x @ x.T
    )

    vals, vecs = np.linalg.eigh(
        cov
    )

    v = vecs[:, -1]

    return (
        v @ x
    ).reshape(
        h,
        w,
    )


# ------------------------------------------------------------
# MATCHERS
# ------------------------------------------------------------

matchers = [
    (
        "sift",
        SIFTMatcher(),
    ),
    (
        "rift",
        RIFTMatcher(),
    ),
    (
        "hopc",
        HOPCMatcher(),
    ),
    (
        "cfog",
        CFOGMatcher(),
    ),
]


results = []


# ------------------------------------------------------------
# TEST CANDIDATES
# ------------------------------------------------------------

for n, (
    geo_error,
    ii_idx,
    tm_idx,
) in enumerate(
    selected,
    1,
):

    print()
    print("=" * 75)
    print(
        f"CANDIDATE A{n:02d}"
    )
    print("=" * 75)

    i_scan = ii["scan"][ii_idx]
    i_pix = ii["pixel"][ii_idx]

    t_scan = tm["scan"][tm_idx]
    t_pix = tm["pixel"][tm_idx]

    print(
        "IIRS:",
        i_scan,
        i_pix,
    )

    print(
        "TMC2:",
        t_scan,
        t_pix,
    )

    # ~5 km context on each side.
    TMC_HALF = 500
    IIRS_SIZE = 61

    tmc = tm_reader.read_window(
        max(
            0,
            int(t_scan) - TMC_HALF,
        ),
        max(
            0,
            int(t_pix) - TMC_HALF,
        ),
        2 * TMC_HALF + 1,
        2 * TMC_HALF + 1,
    )

    cube = read_cube(
        i_scan,
        i_pix,
        IIRS_SIZE,
    )

    reps = {}

    reps["spectral_mean"] = np.mean(
        cube,
        axis=0,
    )

    reps["spectral_gradient"] = np.mean(
        np.abs(
            np.diff(
                cube,
                axis=0,
            )
        ),
        axis=0,
    )

    reps["pca1"] = pca1(
        cube
    )

    # A few widely separated bands.
    for band in (
        32,
        64,
        96,
        128,
        160,
        192,
        224,
    ):

        reps[
            f"band_{band}"
        ] = cube[band]

    candidate_result = {
        "id": f"A{n:02d}",
        "geo_error": geo_error,
        "representations": {},
    }


    # --------------------------------------------------------
    # REPRESENTATION SCREEN
    # --------------------------------------------------------

    for name, rep in reps.items():

        rep = cv2.resize(
            rep.astype(
                np.float32
            ),
            (
                tmc.shape[1],
                tmc.shape[0],
            ),
            interpolation=cv2.INTER_CUBIC,
        )

        t_norm = normalize(
            tmc
        )

        r_norm = normalize(
            rep
        )

        t_grad = gradient(
            t_norm
        )

        r_grad = gradient(
            r_norm
        )

        intensity = corr(
            t_norm,
            r_norm,
        )

        grad_corr = corr(
            t_grad,
            r_grad,
        )

        candidate_result[
            "representations"
        ][name] = {
            "intensity_corr":
                intensity,
            "gradient_corr":
                grad_corr,
        }

        print(
            f"{name:20s}",
            "intensity=",
            f"{intensity: .4f}",
            "gradient=",
            f"{grad_corr: .4f}",
        )

        # Save the most useful representations.
        if name in (
            "spectral_mean",
            "spectral_gradient",
            "pca1",
        ):

            panel = np.hstack([
                normalize(tmc),
                normalize(rep),
            ])

            cv2.imwrite(
                str(
                    OUT
                    / f"A{n:02d}_{name}.png"
                ),
                panel,
            )


    # --------------------------------------------------------
    # RUN MATCHERS ON BEST REPRESENTATIONS
    # --------------------------------------------------------

    best_names = sorted(
        reps.keys(),
        key=lambda name:
            max(
                candidate_result[
                    "representations"
                ][name][
                    "intensity_corr"
                ],
                candidate_result[
                    "representations"
                ][name][
                    "gradient_corr"
                ],
            ),
        reverse=True,
    )[:3]


    candidate_result[
        "tested_match_representations"
    ] = best_names


    for rep_name in best_names:

        rep = reps[
            rep_name
        ]

        rep = cv2.resize(
            rep.astype(
                np.float32
            ),
            (
                512,
                512,
            ),
            interpolation=cv2.INTER_CUBIC,
        )

        target = cv2.resize(
            tmc.astype(
                np.float32
            ),
            (
                512,
                512,
            ),
            interpolation=cv2.INTER_AREA,
        )

        target = clahe(
            target
        )

        rep = clahe(
            rep
        )

        print()
        print(
            "MATCH:",
            rep_name,
        )

        for matcher_name, matcher in matchers:

            t0 = time.perf_counter()

            try:

                r = matcher.match(
                    target,
                    rep,
                )

                elapsed = (
                    time.perf_counter()
                    - t0
                )

                if hasattr(
                    r,
                    "points_a",
                ):

                    count = min(
                        len(r.points_a),
                        len(r.points_b),
                    )

                elif isinstance(
                    r,
                    dict,
                ):

                    count = min(
                        len(
                            r.get(
                                "points_a",
                                [],
                            )
                        ),
                        len(
                            r.get(
                                "points_b",
                                [],
                            )
                        ),
                    )

                else:

                    count = 0

                print(
                    " ",
                    matcher_name,
                    "matches=",
                    count,
                    "time=",
                    f"{elapsed:.2f}s",
                )

                candidate_result.setdefault(
                    "matches",
                    {},
                ).setdefault(
                    rep_name,
                    {},
                )[matcher_name] = {
                    "matches": int(count),
                    "runtime_sec":
                        elapsed,
                }

            except Exception as e:

                elapsed = (
                    time.perf_counter()
                    - t0
                )

                print(
                    " ",
                    matcher_name,
                    "ERROR:",
                    type(e).__name__,
                )

                candidate_result.setdefault(
                    "matches",
                    {},
                ).setdefault(
                    rep_name,
                    {},
                )[matcher_name] = {
                    "matches": 0,
                    "runtime_sec":
                        elapsed,
                    "error":
                        (
                            f"{type(e).__name__}: "
                            f"{e}"
                        ),
                }

    results.append(
        candidate_result
    )


with open(
    OUT / "match_test.json",
    "w",
    encoding="utf-8",
) as f:

    json.dump(
        results,
        f,
        indent=2,
    )


print()
print("=" * 75)
print("P0001 MATCH TEST COMPLETE")
print("=" * 75)
print(
    "OUTPUT:",
    OUT.resolve(),
)
