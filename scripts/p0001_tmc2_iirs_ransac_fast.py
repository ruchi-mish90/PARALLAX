import os
import time
import numpy as np
import cv2

TMC2_IMG = r"C:\Users\graj6\Downloads\P0001\ch2_tmc_ncn_20230605T1503198538_d_img_n18\data\calibrated\20230605\ch2_tmc_ncn_20230605T1503198538_d_img_n18.img"
IIRS_IMG = r"C:\Users\graj6\Downloads\P0001\ch2_iir_nci_20221209T1908498944_d_img_n18\data\calibrated\20221209\ch2_iir_nci_20221209T1908498944_d_img_n18.qub"

TMC2_SHAPE = (153244, 4000)
IIRS_SHAPE = (256, 10075, 250)

TMC2_DTYPE = np.dtype("<u2")
IIRS_DTYPE = np.dtype("<f4")

SX = 9.6805
SY = 8.1776

BAND = 224
PATCH = 41
SEARCH = 20

# Stable coarse seeds from the previous experiment.
SEEDS = {
    "A01": {
        "iirs": (1450, 50),
        "tmc2": (119200, 2300),
        "dx": 6,
        "dy": -5,
    },
    "A03": {
        "iirs": (1800, 0),
        "tmc2": (113500, 1200),
        "dx": 3,
        "dy": 18,
    },
}


def norm(x):
    x = np.asarray(x, dtype=np.float32)
    lo, hi = np.percentile(x, [2, 98])
    if hi <= lo:
        return np.zeros_like(x, dtype=np.float32)
    return np.clip((x - lo) / (hi - lo), 0, 1)


def grad(x):
    x = np.ascontiguousarray(x, dtype=np.float32)
    gx = cv2.Sobel(x, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(x, cv2.CV_32F, 0, 1, ksize=3)
    return cv2.magnitude(gx, gy)


def get_iirs(cube, line, sample):
    h = PATCH // 2
    l0 = line - h
    s0 = sample - h
    l1 = l0 + PATCH
    s1 = s0 + PATCH

    out = np.zeros((PATCH, PATCH), dtype=np.float32)

    a = max(0, l0)
    b = max(0, s0)
    c = min(IIRS_SHAPE[1], l1)
    d = min(IIRS_SHAPE[2], s1)

    if c > a and d > b:
        out[a-l0:c-l0, b-s0:d-s0] = cube[BAND, a:c, b:d]

    return norm(out)


def get_tmc2(img, line, sample, size=801):
    h = size // 2
    l0 = max(0, line-h)
    s0 = max(0, sample-h)
    l1 = min(TMC2_SHAPE[0], l0+size)
    s1 = min(TMC2_SHAPE[1], s0+size)

    x = np.asarray(img[l0:l1, s0:s1], dtype=np.float32)

    out = np.zeros((size, size), dtype=np.float32)
    out[:x.shape[0], :x.shape[1]] = x
    return norm(out)


def match_one(tmc2, iirs_template):
    reduced = cv2.resize(
        tmc2,
        (int(round(tmc2.shape[1] / SX)),
         int(round(tmc2.shape[0] / SY))),
        interpolation=cv2.INTER_AREA
    )

    rg = grad(reduced)
    tg = grad(iirs_template)

    cy = reduced.shape[0] // 2
    cx = reduced.shape[1] // 2

    radius = SEARCH + PATCH // 2

    y0 = max(0, cy-radius)
    y1 = min(reduced.shape[0], cy+radius+1)
    x0 = max(0, cx-radius)
    x1 = min(reduced.shape[1], cx+radius+1)

    search = reduced[y0:y1, x0:x1]
    search_g = rg[y0:y1, x0:x1]

    ri = cv2.matchTemplate(
        np.ascontiguousarray(search, dtype=np.float32),
        np.ascontiguousarray(iirs_template, dtype=np.float32),
        cv2.TM_CCOEFF_NORMED
    )

    rgm = cv2.matchTemplate(
        np.ascontiguousarray(search_g, dtype=np.float32),
        np.ascontiguousarray(tg, dtype=np.float32),
        cv2.TM_CCOEFF_NORMED
    )

    combined = 0.4 * ri + 0.6 * rgm

    _, score, _, loc = cv2.minMaxLoc(combined)

    predicted = (
        search.shape[1] // 2 - PATCH // 2,
        search.shape[0] // 2 - PATCH // 2
    )

    return float(score), loc, (
        loc[0] - predicted[0],
        loc[1] - predicted[1]
    )


def main():
    print("=" * 70)
    print("PARALLAX TMC2 <-> IIRS MULTI-POINT GEOMETRIC VERIFICATION")
    print("=" * 70)

    if not os.path.isfile(TMC2_IMG):
        raise FileNotFoundError(TMC2_IMG)
    if not os.path.isfile(IIRS_IMG):
        raise FileNotFoundError(IIRS_IMG)

    t0 = time.time()

    tmc2 = np.memmap(
        TMC2_IMG,
        dtype=TMC2_DTYPE,
        mode="r",
        shape=TMC2_SHAPE
    )

    iirs = np.memmap(
        IIRS_IMG,
        dtype=IIRS_DTYPE,
        mode="r",
        shape=IIRS_SHAPE
    )

    # Local offsets in IIRS pixels.
    offsets = [
        (-10, -10), (0, -10), (10, -10),
        (-10,   0), (0,   0), (10,  0),
        (-10,  10), (0,  10), (10, 10),
    ]

    pts_iirs = []
    pts_tmc = []
    scores = []

    for name, seed in SEEDS.items():

        iline, isample = seed["iirs"]
        tline, tsample = seed["tmc2"]

        print()
        print("-" * 60)
        print(name)

        # Seed displacement is in IIRS-scale pixels.
        seed_dx = seed["dx"]
        seed_dy = seed["dy"]

        for ox, oy in offsets:

            il = iline + oy
            ip = isample + ox

            # Keep inside IIRS bounds.
            if il < 20 or il >= IIRS_SHAPE[1]-20:
                continue
            if ip < 0 or ip >= IIRS_SHAPE[2]-1:
                continue

            # Geometry maps IIRS displacement to TMC2 pixels.
            tl = int(round(tline + oy * SY + seed_dy * SY))
            tp = int(round(tsample + ox * SX + seed_dx * SX))

            if tl < 500 or tl >= TMC2_SHAPE[0]-500:
                continue
            if tp < 500 or tp >= TMC2_SHAPE[1]-500:
                continue

            template = get_iirs(iirs, il, ip)
            patch = get_tmc2(tmc2, tl, tp)

            score, loc, disp = match_one(patch, template)

            print(
                f"offset=({ox:+3d},{oy:+3d}) "
                f"score={score:.4f} "
                f"local=({disp[0]:+3d},{disp[1]:+3d})"
            )

            # Accept only reasonably strong coarse matches.
            if score >= 0.18:
                final_x = ip + ox * 0
                final_y = il + oy * 0

                # Correct correspondence in original TMC2 pixel space.
                tx = tp + int(round(disp[0] * SX))
                ty = tl + int(round(disp[1] * SY))

                pts_iirs.append([float(ip), float(il)])
                pts_tmc.append([float(tx), float(ty)])
                scores.append(score)

    print()
    print("=" * 70)
    print(f"CANDIDATE CORRESPONDENCES: {len(pts_iirs)}")

    if len(pts_iirs) < 4:
        print("NOT ENOUGH CORRESPONDENCES FOR RANSAC")
        print(f"TOTAL TIME: {time.time()-t0:.3f}s")
        return

    A = np.asarray(pts_iirs, dtype=np.float32)
    B = np.asarray(pts_tmc, dtype=np.float32)

    # Normalize coordinates before affine estimation.
    A0 = A - A.mean(axis=0)
    B0 = B - B.mean(axis=0)

    # Scale TMC2 to IIRS physical sampling.
    B_scaled = B0 / np.array([SX, SY], dtype=np.float32)

    M, mask = cv2.estimateAffinePartial2D(
        A0,
        B_scaled,
        method=cv2.RANSAC,
        ransacReprojThreshold=3.0,
        maxIters=1000,
        confidence=0.99
    )

    if M is None:
        print("RANSAC: FAILED")
        print(f"TOTAL TIME: {time.time()-t0:.3f}s")
        return

    mask = mask.ravel().astype(bool)

    pred = cv2.transform(
        A0.reshape(-1, 1, 2),
        M
    ).reshape(-1, 2)

    errors = np.linalg.norm(pred - B_scaled, axis=1)

    print(f"RANSAC INLIERS: {int(mask.sum())}/{len(mask)}")
    print(f"INLIER RATIO: {mask.mean():.4f}")
    print(f"MEDIAN ERROR: {np.median(errors):.4f} IIRS-pixel")
    print(f"MEAN ERROR: {np.mean(errors):.4f} IIRS-pixel")
    print(f"MAX INLIER ERROR: {np.max(errors[mask]) if mask.any() else float('nan'):.4f}")

    print()
    print("AFFINE MODEL")
    print(M)

    print()
    print("INLIER CORRESPONDENCES")
    for i in range(len(A)):
        if mask[i]:
            print(
                f"IIRS=({A[i,0]:.1f},{A[i,1]:.1f}) "
                f"TMC2=({B[i,0]:.1f},{B[i,1]:.1f}) "
                f"error={errors[i]:.3f}"
            )

    print()
    print("=" * 70)
    print(f"TOTAL TIME: {time.time()-t0:.3f}s")
    print("GEOMETRIC VERIFICATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
