import time
import cv2
import numpy as np
from scipy.ndimage import maximum_filter

from .base import MatchResult, Matcher


def _frequency_grid(shape):
    h, w = shape
    fy = np.fft.fftfreq(h)
    fx = np.fft.fftfreq(w)
    fx, fy = np.meshgrid(fx, fy)

    radius = np.sqrt(fx * fx + fy * fy)
    theta = np.arctan2(fy, fx)
    radius[0, 0] = 1.0

    return radius, theta


def log_gabor_filter(
    shape,
    radial_frequency,
    radial_sigma,
    orientation,
    angular_sigma,
):
    radius, theta = _frequency_grid(shape)

    radial = np.exp(
        -(
            np.log(radius / radial_frequency) ** 2
        ) / (
            2.0 * radial_sigma ** 2
        )
    )

    angle_difference = np.angle(
        np.exp(1j * (theta - orientation))
    )

    angular = np.exp(
        -(
            angle_difference ** 2
        ) / (
            2.0 * angular_sigma ** 2
        )
    )

    return radial * angular


def log_gabor_responses(
    image,
    n_scales=4,
    n_orientations=6,
    min_wavelength=3.0,
    multiplier=2.1,
    sigma_on_f=0.55,
):
    image = np.asarray(
        image,
        dtype=np.float32,
    )

    if image.ndim != 2:
        raise ValueError(
            "RIFT expects a 2-D grayscale image"
        )

    image = image - np.mean(image)

    h, w = image.shape
    image_fft = np.fft.fft2(image)

    angular_sigma = (
        np.pi / n_orientations
    )

    radius, theta = _frequency_grid(
        image.shape
    )

    even = np.empty(
        (n_scales, n_orientations, h, w),
        dtype=np.float32,
    )

    odd = np.empty_like(even)
    amplitudes = np.empty_like(even)

    for scale in range(n_scales):

        wavelength = (
            min_wavelength *
            multiplier ** scale
        )

        radial_frequency = (
            1.0 / wavelength
        )

        for orientation_index in range(
            n_orientations
        ):

            orientation = (
                orientation_index *
                np.pi /
                n_orientations
            )

            filt = log_gabor_filter(
                image.shape,
                radial_frequency,
                sigma_on_f,
                orientation,
                angular_sigma,
            )

            filtered_fft = (
                image_fft * filt
            )

            even_response = np.real(
                np.fft.ifft2(
                    filtered_fft
                )
            )

            odd_response = np.real(
                np.fft.ifft2(
                    filtered_fft *
                    (
                        1j *
                        np.sin(
                            theta - orientation
                        )
                    )
                )
            )

            even[
                scale,
                orientation_index
            ] = even_response

            odd[
                scale,
                orientation_index
            ] = odd_response

            amplitudes[
                scale,
                orientation_index
            ] = np.sqrt(
                even_response ** 2 +
                odd_response ** 2
            )

    return even, odd, amplitudes


def phase_congruency(
    even_responses,
    odd_responses,
    noise_threshold=0.1,
    epsilon=1e-8,
):
    even = np.asarray(
        even_responses,
        dtype=np.float32,
    )

    odd = np.asarray(
        odd_responses,
        dtype=np.float32,
    )

    if even.shape != odd.shape:
        raise ValueError(
            "Even and odd responses must have "
            "the same shape"
        )

    amplitude = np.sqrt(
        even ** 2 +
        odd ** 2
    )

    energy_even = np.sum(
        even,
        axis=0,
    )

    energy_odd = np.sum(
        odd,
        axis=0,
    )

    local_energy = np.sqrt(
        energy_even ** 2 +
        energy_odd ** 2
    )

    total_amplitude = np.sum(
        amplitude,
        axis=0,
    )

    noise_floor = (
        noise_threshold *
        np.mean(
            amplitude,
            axis=0,
        )
    )

    numerator = np.maximum(
        local_energy - noise_floor,
        0.0,
    )

    pc = numerator / (
        total_amplitude +
        epsilon
    )

    return np.clip(
        pc,
        0.0,
        1.0,
    ).astype(np.float32)


def orientation_moments(
    phase_congruency_maps,
    orientations,
    epsilon=1e-8,
):
    pc = np.asarray(
        phase_congruency_maps,
        dtype=np.float32,
    )

    orientations = np.asarray(
        orientations,
        dtype=np.float32,
    )

    if pc.ndim != 3:
        raise ValueError(
            "PC must have shape "
            "(orientations,H,W)"
        )

    if pc.shape[0] != len(orientations):
        raise ValueError(
            "Number of orientations does not "
            "match phase congruency maps"
        )

    cos_o = np.cos(
        orientations
    )[:, None, None]

    sin_o = np.sin(
        orientations
    )[:, None, None]

    x = np.sum(
        pc * cos_o,
        axis=0,
    )

    y = np.sum(
        pc * sin_o,
        axis=0,
    )

    a = x * x
    b = 2.0 * x * y
    c = y * y

    delta = np.sqrt(
        (a - c) ** 2 +
        b ** 2
    )

    max_moment = 0.5 * (
        a + c + delta
    )

    min_moment = 0.5 * (
        a + c - delta
    )

    dominant_orientation = (
        0.5 *
        np.arctan2(
            b,
            a - c + epsilon,
        )
    )

    return (
        min_moment.astype(np.float32),
        max_moment.astype(np.float32),
        dominant_orientation.astype(np.float32),
    )


def maximum_index_map(amplitudes):
    amplitudes = np.asarray(
        amplitudes,
        dtype=np.float32,
    )

    orientation_amplitude = np.sum(
        amplitudes,
        axis=0,
    )

    return np.argmax(
        orientation_amplitude,
        axis=0,
    ).astype(np.int32)


def compute_rift_core(
    image,
    n_scales=4,
    n_orientations=6,
    min_wavelength=3.0,
    multiplier=2.1,
    sigma_on_f=0.55,
):
    even, odd, amplitudes = (
        log_gabor_responses(
            image,
            n_scales=n_scales,
            n_orientations=n_orientations,
            min_wavelength=min_wavelength,
            multiplier=multiplier,
            sigma_on_f=sigma_on_f,
        )
    )

    pc = phase_congruency(
        even,
        odd,
    )

    orientations = (
        np.arange(n_orientations)
        * np.pi /
        n_orientations
    )

    min_moment, max_moment, dominant = (
        orientation_moments(
            pc,
            orientations,
        )
    )

    mim = maximum_index_map(
        amplitudes
    )

    return {
        "even": even,
        "odd": odd,
        "amplitudes": amplitudes,
        "phase_congruency": pc,
        "min_moment": min_moment,
        "max_moment": max_moment,
        "dominant_orientation": dominant,
        "mim": mim,
        "orientations": orientations,
    }


def detect_rift_keypoints(
    min_moment,
    max_moment,
    max_keypoints=1000,
    corner_percentile=99.0,
    edge_percentile=99.0,
    nms_size=7,
    border=48,
):
    min_moment = np.asarray(
        min_moment,
        dtype=np.float32,
    )

    max_moment = np.asarray(
        max_moment,
        dtype=np.float32,
    )

    h, w = min_moment.shape

    if h <= 2 * border or w <= 2 * border:
        return np.empty(
            (0, 2),
            dtype=np.float32,
        )

    threshold = np.percentile(
        min_moment,
        corner_percentile,
    )

    local_max = (
        min_moment ==
        maximum_filter(
            min_moment,
            size=nms_size,
        )
    )

    corner_mask = (
        local_max &
        (min_moment >= threshold)
    )

    edge_norm = cv2.normalize(
        max_moment,
        None,
        0,
        255,
        cv2.NORM_MINMAX,
    ).astype(np.uint8)

    fast = cv2.FastFeatureDetector_create(
        threshold=10,
        nonmaxSuppression=True,
    )

    edge_keypoints = fast.detect(
        edge_norm,
        None,
    )

    edge_points = np.array(
        [
            kp.pt
            for kp in edge_keypoints
        ],
        dtype=np.float32,
    )

    cy, cx = np.where(
        corner_mask
    )

    corner_points = np.column_stack(
        [cx, cy]
    ).astype(np.float32)

    def valid_border(points):
        if len(points) == 0:
            return points

        keep = (
            (points[:, 0] >= border) &
            (points[:, 0] < w - border) &
            (points[:, 1] >= border) &
            (points[:, 1] < h - border)
        )

        return points[keep]

    corner_points = valid_border(
        corner_points
    )

    edge_points = valid_border(
        edge_points
    )

    candidates = []

    for x, y in corner_points:
        candidates.append(
            (
                x,
                y,
                float(
                    min_moment[
                        int(round(y)),
                        int(round(x))
                    ]
                ),
            )
        )

    for x, y in edge_points:
        candidates.append(
            (
                x,
                y,
                float(
                    max_moment[
                        int(round(y)),
                        int(round(x))
                    ]
                ),
            )
        )

    if not candidates:
        return np.empty(
            (0, 2),
            dtype=np.float32,
        )

    candidates.sort(
        key=lambda v: v[2],
        reverse=True,
    )

    selected = []

    min_distance = max(
        4.0,
        min(h, w) / 80.0,
    )

    min_distance_sq = (
        min_distance ** 2
    )

    for x, y, score in candidates:

        if all(
            (x - px) ** 2 +
            (y - py) ** 2
            >= min_distance_sq
            for px, py, _ in selected
        ):
            selected.append(
                (x, y, score)
            )

        if len(selected) >= max_keypoints:
            break

    return np.asarray(
        [
            [x, y]
            for x, y, _ in selected
        ],
        dtype=np.float32,
    )


def _descriptor_patch_indices(
    keypoints,
    image_shape,
    patch_size,
):
    h, w = image_shape

    half = patch_size // 2

    x = np.rint(
        keypoints[:, 0]
    ).astype(np.int32)

    y = np.rint(
        keypoints[:, 1]
    ).astype(np.int32)

    offsets = np.arange(
        -half,
        half,
        dtype=np.int32,
    )

    oy, ox = np.meshgrid(
        offsets,
        offsets,
        indexing="ij",
    )

    xx = (
        x[:, None, None] +
        ox[None, :, :]
    )

    yy = (
        y[:, None, None] +
        oy[None, :, :]
    )

    valid = (
        (xx >= 0) &
        (xx < w) &
        (yy >= 0) &
        (yy < h)
    )

    xx = np.clip(
        xx,
        0,
        w - 1,
    )

    yy = np.clip(
        yy,
        0,
        h - 1,
    )

    return yy, xx, valid


def mim_descriptor(
    mim,
    keypoints,
    patch_size=72,
    grid_size=6,
    n_orientations=6,
):
    """
    Vectorized RIFT MIM descriptor.

    Default dimension:

        6 × 6 × 6 = 216
    """

    mim = np.asarray(
        mim,
        dtype=np.int32,
    )

    keypoints = np.asarray(
        keypoints,
        dtype=np.float32,
    )

    descriptor_dim = (
        grid_size *
        grid_size *
        n_orientations
    )

    if len(keypoints) == 0:
        return np.empty(
            (0, descriptor_dim),
            dtype=np.float32,
        )

    yy, xx, valid = (
        _descriptor_patch_indices(
            keypoints,
            mim.shape,
            patch_size,
        )
    )

    patches = mim[
        yy,
        xx,
    ]

    patches = np.clip(
        patches,
        0,
        n_orientations - 1,
    )

    h, w = patches.shape[1:]

    cell_h = h / grid_size
    cell_w = w / grid_size

    py = np.arange(h)
    px = np.arange(w)

    cell_y = np.minimum(
        (py / cell_h).astype(np.int32),
        grid_size - 1,
    )

    cell_x = np.minimum(
        (px / cell_w).astype(np.int32),
        grid_size - 1,
    )

    cell_index = (
        cell_y[:, None] *
        grid_size +
        cell_x[None, :]
    )

    orientation = patches

    feature_index = (
        cell_index[None, :, :] *
        n_orientations +
        orientation
    )

    center = (
        patch_size - 1
    ) / 2.0

    gy, gx = np.mgrid[
        0:h,
        0:w,
    ]

    sigma = patch_size / 2.0

    gaussian = np.exp(
        -(
            (gx - center) ** 2 +
            (gy - center) ** 2
        ) /
        (
            2.0 * sigma ** 2
        )
    ).astype(np.float32)

    weights = (
        gaussian[None, :, :] *
        valid.astype(np.float32)
    )

    descriptors = np.zeros(
        (
            len(keypoints),
            descriptor_dim,
        ),
        dtype=np.float32,
    )

    flat_index = (
        feature_index
        .reshape(len(keypoints), -1)
    )

    flat_weight = (
        weights
        .reshape(len(keypoints), -1)
    )

    for i in range(
        len(keypoints)
    ):
        np.add.at(
            descriptors[i],
            flat_index[i],
            flat_weight[i],
        )

    norms = np.linalg.norm(
        descriptors,
        axis=1,
        keepdims=True,
    )

    descriptors /= np.maximum(
        norms,
        1e-8,
    )

    return descriptors.astype(
        np.float32
    )


def rotated_mim_descriptors(
    mim,
    keypoints,
    patch_size=72,
    grid_size=6,
    n_orientations=6,
):
    """
    Rotation variants generated by circularly shifting
    orientation labels. Descriptor construction remains
    vectorized.
    """

    variants = []

    for shift in range(
        n_orientations
    ):

        shifted = (
            mim + shift
        ) % n_orientations

        variants.append(
            mim_descriptor(
                shifted,
                keypoints,
                patch_size=patch_size,
                grid_size=grid_size,
                n_orientations=n_orientations,
            )
        )

    return variants


class RIFTMatcher(Matcher):

    def __init__(
        self,
        n_scales=4,
        n_orientations=6,
        patch_size=72,
        max_keypoints=1000,
        ratio_test=0.80,
        rotation_invariant=True,
    ):
        self.n_scales = n_scales
        self.n_orientations = n_orientations
        self.patch_size = patch_size
        self.max_keypoints = max_keypoints
        self.ratio_test = ratio_test
        self.rotation_invariant = (
            rotation_invariant
        )

    @staticmethod
    def _prepare_image(image):
        image = np.asarray(
            image,
            dtype=np.float32,
        )

        if image.ndim != 2:
            raise ValueError(
                "RIFT expects grayscale 2-D images"
            )

        finite = np.isfinite(image)

        if not finite.any():
            return np.zeros_like(
                image,
                dtype=np.float32,
            )

        values = image[finite]

        lo = np.percentile(
            values,
            1,
        )

        hi = np.percentile(
            values,
            99,
        )

        if hi <= lo:
            return np.zeros_like(
                image,
                dtype=np.float32,
            )

        image = np.clip(
            (image - lo) /
            (hi - lo),
            0,
            1,
        )

        return image.astype(
            np.float32
        )

    @staticmethod
    def _best_variant_distances(
        descriptors_a,
        descriptors_b_variants,
    ):
        best = None

        for db in descriptors_b_variants:

            if len(db) == 0:
                continue

            aa = np.sum(
                descriptors_a ** 2,
                axis=1,
                keepdims=True,
            )

            bb = np.sum(
                db ** 2,
                axis=1,
                keepdims=True,
            ).T

            distances_sq = (
                aa +
                bb -
                2.0 *
                descriptors_a @ db.T
            )

            distances_sq = np.maximum(
                distances_sq,
                0.0,
            )

            distances = np.sqrt(
                distances_sq
            )

            if best is None:
                best = distances
            else:
                best = np.minimum(
                    best,
                    distances,
                )

        return best

    def match(
        self,
        image_a,
        image_b,
    ):

        start = time.perf_counter()

        image_a = self._prepare_image(
            image_a
        )

        image_b = self._prepare_image(
            image_b
        )

        core_a = compute_rift_core(
            image_a,
            n_scales=self.n_scales,
            n_orientations=self.n_orientations,
        )

        core_b = compute_rift_core(
            image_b,
            n_scales=self.n_scales,
            n_orientations=self.n_orientations,
        )

        keypoints_a = detect_rift_keypoints(
            core_a["min_moment"],
            core_a["max_moment"],
            max_keypoints=self.max_keypoints,
            border=self.patch_size // 2 + 2,
        )

        keypoints_b = detect_rift_keypoints(
            core_b["min_moment"],
            core_b["max_moment"],
            max_keypoints=self.max_keypoints,
            border=self.patch_size // 2 + 2,
        )

        if (
            len(keypoints_a) == 0 or
            len(keypoints_b) == 0
        ):

            runtime_ms = (
                time.perf_counter() -
                start
            ) * 1000.0

            return MatchResult(
                keypoints_a=keypoints_a,
                keypoints_b=keypoints_b,
                matches=np.empty(
                    (0, 2),
                    dtype=np.int32,
                ),
                scores=np.empty(
                    (0,),
                    dtype=np.float32,
                ),
                model_name="RIFT",
                runtime_ms=runtime_ms,
                metadata={
                    "descriptor_dimension":
                        216,
                    "rotation_invariant":
                        self.rotation_invariant,
                },
            )

        descriptors_a = mim_descriptor(
            core_a["mim"],
            keypoints_a,
            patch_size=self.patch_size,
            grid_size=6,
            n_orientations=self.n_orientations,
        )

        if self.rotation_invariant:

            descriptors_b_variants = (
                rotated_mim_descriptors(
                    core_b["mim"],
                    keypoints_b,
                    patch_size=self.patch_size,
                    grid_size=6,
                    n_orientations=self.n_orientations,
                )
            )

        else:

            descriptors_b_variants = [
                mim_descriptor(
                    core_b["mim"],
                    keypoints_b,
                    patch_size=self.patch_size,
                    grid_size=6,
                    n_orientations=self.n_orientations,
                )
            ]

        distances = (
            self._best_variant_distances(
                descriptors_a,
                descriptors_b_variants,
            )
        )

        matches = []
        scores = []

        if distances is not None:

            for i in range(
                distances.shape[0]
            ):

                row = distances[i]

                if len(row) < 2:
                    continue

                order = np.argsort(
                    row
                )

                best_idx = int(
                    order[0]
                )

                second_idx = int(
                    order[1]
                )

                best_distance = float(
                    row[best_idx]
                )

                second_distance = float(
                    row[second_idx]
                )

                if (
                    best_distance <
                    self.ratio_test *
                    second_distance
                ):

                    matches.append(
                        [
                            i,
                            best_idx,
                        ]
                    )

                    scores.append(
                        1.0 /
                        (
                            1.0 +
                            best_distance
                        )
                    )

        if matches:

            matches = np.asarray(
                matches,
                dtype=np.int32,
            )

            scores = np.asarray(
                scores,
                dtype=np.float32,
            )

        else:

            matches = np.empty(
                (0, 2),
                dtype=np.int32,
            )

            scores = np.empty(
                (0,),
                dtype=np.float32,
            )

        runtime_ms = (
            time.perf_counter() -
            start
        ) * 1000.0

        return MatchResult(
            keypoints_a=keypoints_a,
            keypoints_b=keypoints_b,
            matches=matches,
            scores=scores,
            model_name="RIFT",
            runtime_ms=runtime_ms,
            metadata={
                "n_scales":
                    self.n_scales,
                "n_orientations":
                    self.n_orientations,
                "patch_size":
                    self.patch_size,
                "descriptor_dimension":
                    (
                        6 *
                        6 *
                        self.n_orientations
                    ),
                "rotation_invariant":
                    self.rotation_invariant,
                "ratio_test":
                    self.ratio_test,
            },
        )


__all__ = [
    "log_gabor_filter",
    "log_gabor_responses",
    "phase_congruency",
    "orientation_moments",
    "maximum_index_map",
    "compute_rift_core",
    "detect_rift_keypoints",
    "mim_descriptor",
    "rotated_mim_descriptors",
    "RIFTMatcher",
]
