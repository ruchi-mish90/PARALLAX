from pathlib import Path
import numpy as np
import cv2

TMC2_ROOT = Path(r"C:\Users\graj6\Downloads\P0001\ch2_tmc_ncn_20230605T1503198538_d_img_n18")
IIRS_ROOT = Path(r"C:\Users\graj6\Downloads\P0001\ch2_iir_nci_20221209T1908498944_d_img_n18")

OUT = Path("results/P0001_A01_MATCH_V2")
OUT.mkdir(parents=True, exist_ok=True)

# Geometry measured from the real P0001 products
X_SCALE = 9.6805
Y_SCALE = 8.1776

TMC2_LINE = 119200
TMC2_SAMPLE = 2300

IIRS_LINE = 1450
IIRS_SAMPLE = 50

TMC2_SIZE = 1001
IIRS_SIZE = 101


def norm01(x):
    x = np.asarray(x, dtype=np.float32)
    good = np.isfinite(x)

    if not good.any():
        return np.zeros_like(x)

    lo, hi = np.percentile(x[good], [2, 98])

    if hi <= lo:
        return np.zeros_like(x)

    return np.clip((x - lo) / (hi - lo), 0, 1)


def load_data():
    tmc2_path = next(TMC2_ROOT.rglob("*.img"))
    iirs_path = next(IIRS_ROOT.rglob("*.qub"))

    print("TMC2:", tmc2_path)
    print("IIRS:", iirs_path)

    tmc2 = np.memmap(
        tmc2_path,
        dtype="<u2",
        mode="r",
        shape=(153244, 4000),
        order="C"
    )

    iirs = np.memmap(
        iirs_path,
        dtype="<f4",
        mode="r",
        shape=(256, 10075, 250),
        order="C"
    )

    return tmc2, iirs


def extract_tmc2(tmc2):
    h = TMC2_SIZE // 2

    patch = np.asarray(
        tmc2[
            TMC2_LINE - h:TMC2_LINE + h + 1,
            TMC2_SAMPLE - h:TMC2_SAMPLE + h + 1
        ],
        dtype=np.float32
    )

    return norm01(patch)


def extract_iirs(iirs):
    h = IIRS_SIZE // 2

    cube = np.asarray(
        iirs[
            :,
            IIRS_LINE - h:IIRS_LINE + h + 1,
            IIRS_SAMPLE - h:IIRS_SAMPLE + h + 1
        ],
        dtype=np.float32
    )

    reps = {}

    for band in [128, 160, 192, 224]:
        reps[f"band_{band}"] = cube[band - 1]

    reps["spectral_gradient"] = np.nanmean(
        np.abs(np.diff(cube, axis=0)),
        axis=0
    )

    return {
        k: norm01(v)
        for k, v in reps.items()
    }


def prepare_tmc2(tmc2):
    # Physical-scale blur before reduction.
    blurred = cv2.GaussianBlur(
        tmc2,
        (0, 0),
        sigmaX=X_SCALE / 2.0,
        sigmaY=Y_SCALE / 2.0
    )

    reduced_w = int(round(TMC2_SIZE / X_SCALE))
    reduced_h = int(round(TMC2_SIZE / Y_SCALE))

    low = cv2.resize(
        blurred,
        (reduced_w, reduced_h),
        interpolation=cv2.INTER_AREA
    )

    # Final common grid.
    common = cv2.resize(
        low,
        (IIRS_SIZE, IIRS_SIZE),
        interpolation=cv2.INTER_LINEAR
    )

    return norm01(common)


def enhance(x):
    x = norm01(x)

    # Mild local contrast enhancement.
    u8 = (x * 255).astype(np.uint8)

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    return clahe.apply(u8)


def run_sift(a, b):
    sift = cv2.SIFT_create(
        nfeatures=2000,
        contrastThreshold=0.01,
        edgeThreshold=10,
        sigma=1.2
    )

    kp1, des1 = sift.detectAndCompute(a, None)
    kp2, des2 = sift.detectAndCompute(b, None)

    if des1 is None or des2 is None:
        return {
            "keypoints_a": len(kp1),
            "keypoints_b": len(kp2),
            "raw": 0,
            "filtered": 0,
            "inliers": 0,
            "rmse": None,
            "coverage": 0.0,
            "kp1": kp1,
            "kp2": kp2,
            "good": [],
            "mask": None
        }

    matcher = cv2.BFMatcher(cv2.NORM_L2)

    knn = matcher.knnMatch(des1, des2, k=2)

    good = []

    for pair in knn:
        if len(pair) != 2:
            continue

        m, n = pair

        if m.distance < 0.75 * n.distance:
            good.append(m)

    result = {
        "keypoints_a": len(kp1),
        "keypoints_b": len(kp2),
        "raw": len(knn),
        "filtered": len(good),
        "inliers": 0,
        "rmse": None,
        "coverage": 0.0,
        "kp1": kp1,
        "kp2": kp2,
        "good": good,
        "mask": None
    }

    if len(good) < 4:
        return result

    pts1 = np.float32(
        [kp1[m.queryIdx].pt for m in good]
    )

    pts2 = np.float32(
        [kp2[m.trainIdx].pt for m in good]
    )

    H, mask = cv2.findHomography(
        pts1,
        pts2,
        cv2.RANSAC,
        3.0
    )

    if H is None or mask is None:
        return result

    mask = mask.ravel().astype(bool)

    in1 = pts1[mask]
    in2 = pts2[mask]

    result["inliers"] = int(mask.sum())
    result["mask"] = mask

    if len(in1) > 0:
        pred = cv2.perspectiveTransform(
            in1.reshape(-1, 1, 2),
            H
        ).reshape(-1, 2)

        err = np.linalg.norm(
            pred - in2,
            axis=1
        )

        result["rmse"] = float(
            np.sqrt(np.mean(err ** 2))
        )

        # Spatial coverage of inlier points.
        if len(in1) >= 2:
            x = in1[:, 0]
            y = in1[:, 1]

            area = (
                (x.max() - x.min())
                *
                (y.max() - y.min())
            )

            total = float(
                (a.shape[1] - 1)
                *
                (a.shape[0] - 1)
            )

            result["coverage"] = min(
                1.0,
                max(0.0, area / total)
            )

    return result


def save_matches(name, a, b, result):

    kp1 = result["kp1"]
    kp2 = result["kp2"]
    good = result["good"]
    mask = result["mask"]

    if not good:
        return

    if mask is None:
        draw = good
    else:
        draw = [
            m
            for i, m in enumerate(good)
            if mask[i]
        ]

    vis = cv2.drawMatches(
        a,
        kp1,
        b,
        kp2,
        draw,
        None,
        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
    )

    cv2.imwrite(
        str(OUT / f"{name}_inliers.png"),
        vis
    )


def main():

    print("=" * 70)
    print("PARALLAX A01 V2 - REAL CORRESPONDENCE TEST")
    print("=" * 70)

    print("X scale:", X_SCALE)
    print("Y scale:", Y_SCALE)

    tmc2, iirs = load_data()

    tmc2_raw = extract_tmc2(tmc2)
    iirs_reps = extract_iirs(iirs)

    tmc2_common = prepare_tmc2(tmc2_raw)

    tmc2_img = enhance(tmc2_common)

    print()
    print("TMC2 common grid:", tmc2_common.shape)

    rows = []

    for name, iirs_rep in iirs_reps.items():

        iirs_img = enhance(iirs_rep)

        result = run_sift(
            tmc2_img,
            iirs_img
        )

        rows.append(
            (
                name,
                result["keypoints_a"],
                result["keypoints_b"],
                result["raw"],
                result["filtered"],
                result["inliers"],
                result["rmse"],
                result["coverage"]
            )
        )

        save_matches(
            name,
            tmc2_img,
            iirs_img,
            result
        )

        print()
        print(name)
        print("  keypoints TMC2 :", result["keypoints_a"])
        print("  keypoints IIRS :", result["keypoints_b"])
        print("  raw matches     :", result["raw"])
        print("  filtered        :", result["filtered"])
        print("  RANSAC inliers  :", result["inliers"])
        print("  RMSE            :", result["rmse"])
        print("  coverage        :", result["coverage"])

    with open(
        OUT / "results.csv",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "representation,"
            "keypoints_tmc2,"
            "keypoints_iirs,"
            "raw,"
            "filtered,"
            "inliers,"
            "rmse,"
            "coverage\n"
        )

        for row in rows:
            f.write(
                ",".join(
                    "" if v is None else str(v)
                    for v in row
                )
                + "\n"
            )

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for row in sorted(
        rows,
        key=lambda r: (
            r[5],
            r[7]
        ),
        reverse=True
    ):
        print(
            f"{row[0]:20s}"
            f" inliers={row[5]:4d}"
            f" filtered={row[4]:4d}"
            f" coverage={row[7]:.4f}"
            f" rmse={row[6]}"
        )

    print()
    print("Saved:", OUT)


if __name__ == "__main__":
    main()
