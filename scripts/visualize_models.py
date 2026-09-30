from pathlib import Path
import cv2
import numpy as np
import sys

ROOT = Path(__file__).resolve().parents[1]
P0001 = ROOT.parent / "P0001"

sys.path.insert(0, str(ROOT / "src"))

from parallex.io.image_loader import open_raw_image
from parallex.routing.engine import RoutingEngine


def find_file(pattern):
    hits = list(P0001.rglob(pattern))
    if not hits:
        raise FileNotFoundError(pattern)
    return hits[0]


def normalize(img):
    img = np.asarray(img, dtype=np.float32)
    lo, hi = np.percentile(img, [1, 99])

    if hi <= lo:
        lo = float(img.min())
        hi = float(img.max())

    img = np.clip((img - lo) / max(hi - lo, 1e-6), 0, 1)
    return (img * 255).astype(np.uint8)


def extract_points(result):
    matches = getattr(result, "matches", None)

    if matches is None:
        return None, None

    matches = np.asarray(matches)

    if matches.size == 0:
        return None, None

    # Direct coordinate representation
    if matches.ndim == 3 and matches.shape[-2:] == (2, 2):
        return (
            matches[:, 0, :].astype(np.float32),
            matches[:, 1, :].astype(np.float32),
        )

    # Index-based representation
    if matches.ndim == 2 and matches.shape[1] == 2:
        kpa = getattr(result, "keypoints_a", None)
        kpb = getattr(result, "keypoints_b", None)

        if kpa is None or kpb is None:
            return None, None

        kpa = np.asarray(kpa)
        kpb = np.asarray(kpb)

        ia = matches[:, 0].astype(np.int64)
        ib = matches[:, 1].astype(np.int64)

        valid = (
            (ia >= 0) &
            (ia < len(kpa)) &
            (ib >= 0) &
            (ib < len(kpb))
        )

        return (
            kpa[ia[valid]].astype(np.float32),
            kpb[ib[valid]].astype(np.float32),
        )

    # Direct [x_a,y_a,x_b,y_b]
    if matches.ndim == 2 and matches.shape[1] == 4:
        return (
            matches[:, 0:2].astype(np.float32),
            matches[:, 2:4].astype(np.float32),
        )

    return None, None


def draw_matches(image_a, image_b, pts_a, pts_b, output, title):

    a = normalize(image_a)
    b = normalize(image_b)

    a = cv2.cvtColor(a, cv2.COLOR_GRAY2BGR)
    b = cv2.cvtColor(b, cv2.COLOR_GRAY2BGR)

    h = max(a.shape[0], b.shape[0])
    w = a.shape[1] + b.shape[1]

    canvas = np.zeros((h, w, 3), dtype=np.uint8)

    canvas[:a.shape[0], :a.shape[1]] = a
    canvas[:b.shape[0], a.shape[1]:] = b

    offset = a.shape[1]

    n = min(len(pts_a), len(pts_b))

    # Draw every match if <= 300.
    # Otherwise sample evenly so the image remains readable.
    if n > 300:
        indices = np.linspace(0, n - 1, 300).astype(int)
    else:
        indices = np.arange(n)

    for i in indices:

        xa, ya = pts_a[i]
        xb, yb = pts_b[i]

        p1 = (int(round(xa)), int(round(ya)))
        p2 = (int(round(xb + offset)), int(round(yb)))

        cv2.line(
            canvas,
            p1,
            p2,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

        cv2.circle(
            canvas,
            p1,
            3,
            (255, 255, 255),
            -1,
            cv2.LINE_AA,
        )

        cv2.circle(
            canvas,
            p2,
            3,
            (255, 255, 255),
            -1,
            cv2.LINE_AA,
        )

    cv2.putText(
        canvas,
        title,
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        canvas,
        f"Matches: {n}",
        (20, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.imwrite(str(output), canvas)


# ------------------------------------------------------------
# Load exact P0001 TMC2 ROI used in controlled positive test
# ------------------------------------------------------------

img_path = find_file(
    "ch2_tmc_ncn_20230605T1503198538_d_img_n18.img"
)

reader = open_raw_image(
    img_path,
    lines=153244,
    samples=4000,
    dtype=np.uint16,
)

row = 70000
col = 1200
height = 1200
width = 1200

image_a = reader.read_window(
    row=row,
    col=col,
    height=height,
    width=width,
)

image_a = normalize(image_a)

# Same controlled transformation as the successful test
M = cv2.getRotationMatrix2D(
    (width / 2, height / 2),
    2.0,
    1.0,
)

M[0, 2] += 18.0
M[1, 2] += -12.0

image_b = cv2.warpAffine(
    image_a,
    M,
    (width, height),
    flags=cv2.INTER_LINEAR,
    borderMode=cv2.BORDER_REFLECT,
)

out = (
    ROOT
    / "results"
    / "P0001_CONTROLLED_POSITIVE"
    / "model_visualizations"
)

out.mkdir(parents=True, exist_ok=True)

cv2.imwrite(str(out / "input_A.png"), image_a)
cv2.imwrite(str(out / "input_B.png"), image_b)

print()
print("Output directory:")
print(out)
print()

# ------------------------------------------------------------
# Run each backend matcher DIRECTLY
# ------------------------------------------------------------

engine = RoutingEngine()

models = [
    "sift",
    "hopc",
    "cfog",
    "loftr",
    "superpoint_lightglue",
]

for model in models:

    print("=" * 70)
    print("MODEL:", model)

    model_dir = out / model
    model_dir.mkdir(parents=True, exist_ok=True)

    try:

        result = engine.run_matcher(
            model,
            image_a,
            image_b,
        )

        if result is None:
            print("No result returned.")
            continue

        matches = getattr(result, "matches", None)

        if matches is None:
            print("Matcher returned no matches attribute.")
            continue

        matches = np.asarray(matches)

        print("Raw match representation:", matches.shape)

        pts_a, pts_b = extract_points(result)

        if pts_a is None:
            print("Could not extract coordinates.")
            continue

        print("Actual coordinates:", len(pts_a))

        scores = getattr(result, "scores", None)

        if scores is not None:
            scores = np.asarray(scores).reshape(-1)
            print("Scores:", len(scores))

        np.save(model_dir / "points_a.npy", pts_a)
        np.save(model_dir / "points_b.npy", pts_b)

        if scores is not None:
            np.save(model_dir / "scores.npy", scores)

        draw_matches(
            image_a,
            image_b,
            pts_a,
            pts_b,
            model_dir / "raw_matches.png",
            f"{model.upper()} — RAW BACKEND MATCHES",
        )

        print("Saved:")
        print(model_dir / "raw_matches.png")

    except Exception as exc:

        print("STATUS: FAILED")
        print(type(exc).__name__ + ":", exc)

print()
print("=" * 70)
print("DONE")
print(out)
