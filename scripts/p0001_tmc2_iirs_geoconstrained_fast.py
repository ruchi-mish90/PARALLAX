import os
import time
import numpy as np
import cv2

TMC2_IMG = r"C:\Users\graj6\Downloads\P0001\ch2_tmc_ncn_20230605T1503198538_d_img_n18\data\calibrated\20230605\ch2_tmc_ncn_20230605T1503198538_d_img_n18.img"
IIRS_IMG = r"C:\Users\graj6\Downloads\P0001\ch2_iir_nci_20221209T1908498944_d_img_n18\data\calibrated\20221209\ch2_iir_nci_20221209T1908498944_d_img_n18.qub"

PAIRS = {
    "A01": ((1450, 50), (119200, 2300)),
    "A03": ((1800, 0), (113500, 1200)),
}

TMC2_SHAPE = (153244, 4000)
IIRS_SHAPE = (256, 10075, 250)

SX = 9.6805
SY = 8.1776

TMC2_DTYPE = np.dtype("<u2")
IIRS_DTYPE = np.dtype("<f4")

BAND = 224
TMC2_SIZE = 1001
TEMPLATE_SIZE = 41
SEARCH_RADIUS = 20


def norm(x):
    x = np.asarray(x, dtype=np.float32)
    lo, hi = np.percentile(x, [2, 98])
    if hi <= lo:
        return np.zeros_like(x, dtype=np.float32)
    return np.clip((x - lo) / (hi - lo), 0, 1).astype(np.float32)


def grad(x):
    x = np.ascontiguousarray(x, dtype=np.float32)
    gx = cv2.Sobel(x, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(x, cv2.CV_32F, 0, 1, ksize=3)
    return cv2.magnitude(gx, gy)


def extract_iirs(cube, line, sample):
    half = TEMPLATE_SIZE // 2

    l0 = line - half
    s0 = sample - half
    l1 = l0 + TEMPLATE_SIZE
    s1 = s0 + TEMPLATE_SIZE

    out = np.zeros((TEMPLATE_SIZE, TEMPLATE_SIZE), dtype=np.float32)

    src_l0 = max(0, l0)
    src_s0 = max(0, s0)
    src_l1 = min(IIRS_SHAPE[1], l1)
    src_s1 = min(IIRS_SHAPE[2], s1)

    if src_l1 > src_l0 and src_s1 > src_s0:
        dst_l0 = src_l0 - l0
        dst_s0 = src_s0 - s0

        out[
            dst_l0:dst_l0 + (src_l1-src_l0),
            dst_s0:dst_s0 + (src_s1-src_s0)
        ] = cube[BAND, src_l0:src_l1, src_s0:src_s1]

    return norm(out)


def extract_tmc2(img, line, sample):
    half = TMC2_SIZE // 2

    l0 = max(0, line-half)
    s0 = max(0, sample-half)
    l1 = min(TMC2_SHAPE[0], l0+TMC2_SIZE)
    s1 = min(TMC2_SHAPE[1], s0+TMC2_SIZE)

    patch = np.asarray(img[l0:l1, s0:s1], dtype=np.float32)

    out = np.zeros((TMC2_SIZE, TMC2_SIZE), dtype=np.float32)
    out[:patch.shape[0], :patch.shape[1]] = patch

    return norm(out)


def main():

    print("=" * 70)
    print("PARALLAX FAST GEOMETRY-CONSTRAINED TMC2 <-> IIRS")
    print("=" * 70)
    print(f"Band: {BAND}")
    print(f"Physical scale ratio: X={SX:.4f}, Y={SY:.4f}")
    print(f"Template: {TEMPLATE_SIZE}x{TEMPLATE_SIZE}")
    print(f"Search radius: +/-{SEARCH_RADIUS} IIRS pixels")
    print()

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

    for name, (iirs_xy, tmc2_xy) in PAIRS.items():

        start = time.time()

        iline, isample = iirs_xy
        tline, tsample = tmc2_xy

        print("-" * 60)
        print(name)
        print(f"IIRS=({iline},{isample}) TMC2=({tline},{tsample})")

        template = extract_iirs(iirs, iline, isample)
        template_g = grad(template)

        tpatch = extract_tmc2(tmc2, tline, tsample)

        # Convert TMC2 to approximately IIRS physical sampling.
        reduced_w = int(round(TMC2_SIZE / SX))
        reduced_h = int(round(TMC2_SIZE / SY))

        reduced = cv2.resize(
            tpatch,
            (reduced_w, reduced_h),
            interpolation=cv2.INTER_AREA
        )

        reduced_g = grad(reduced)

        cy = reduced.shape[0] // 2
        cx = reduced.shape[1] // 2

        # IMPORTANT:
        # Search window must be larger than the template.
        crop_radius = SEARCH_RADIUS + TEMPLATE_SIZE // 2

        y0 = max(0, cy - crop_radius)
        y1 = min(reduced.shape[0], cy + crop_radius + 1)

        x0 = max(0, cx - crop_radius)
        x1 = min(reduced.shape[1], cx + crop_radius + 1)

        search = reduced[y0:y1, x0:x1]
        search_g = reduced_g[y0:y1, x0:x1]

        if (
            search.shape[0] < TEMPLATE_SIZE
            or search.shape[1] < TEMPLATE_SIZE
        ):
            print("SKIP: insufficient search area")
            continue

        search = np.ascontiguousarray(search, dtype=np.float32)
        search_g = np.ascontiguousarray(search_g, dtype=np.float32)
        template = np.ascontiguousarray(template, dtype=np.float32)
        template_g = np.ascontiguousarray(template_g, dtype=np.float32)

        result_i = cv2.matchTemplate(
            search,
            template,
            cv2.TM_CCOEFF_NORMED
        )

        result_g = cv2.matchTemplate(
            search_g,
            template_g,
            cv2.TM_CCOEFF_NORMED
        )

        _, score_i, _, loc_i = cv2.minMaxLoc(result_i)
        _, score_g, _, loc_g = cv2.minMaxLoc(result_g)

        combined_map = 0.4 * result_i + 0.6 * result_g

        _, score_c, _, loc_c = cv2.minMaxLoc(combined_map)

        # Convert match location into displacement
        # relative to the geometry-predicted center.
        predicted_x = search.shape[1] // 2 - TEMPLATE_SIZE // 2
        predicted_y = search.shape[0] // 2 - TEMPLATE_SIZE // 2

        dx = loc_c[0] - predicted_x
        dy = loc_c[1] - predicted_y

        print(f"intensity NCC : {score_i:.5f}")
        print(f"gradient NCC  : {score_g:.5f}")
        print(f"combined NCC  : {score_c:.5f}")
        print(f"best location : {loc_c}")
        print(f"displacement  : dx={dx:+d}, dy={dy:+d}")

        # Stability check: compare central result against boundary.
        boundary = (
            loc_c[0] <= 1
            or loc_c[1] <= 1
            or loc_c[0] >= result_i.shape[1]-2
            or loc_c[1] >= result_i.shape[0]-2
        )

        print(f"boundary_peak : {boundary}")
        print(f"elapsed       : {time.time()-start:.3f}s")

    print()
    print("=" * 70)
    print(f"TOTAL TIME: {time.time()-t0:.3f}s")
    print("FAST TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()





