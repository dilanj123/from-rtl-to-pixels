"""Independent whole-image Sobel reference model."""

from pathlib import Path

import numpy as np
from PIL import Image


def _require_rgb(image: np.ndarray) -> None:
    if image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("RGB image must have shape (H, W, 3) and dtype uint8")


def _require_gray(image: np.ndarray) -> None:
    if image.dtype != np.uint8 or image.ndim != 2:
        raise ValueError("grayscale image must have shape (H, W) and dtype uint8")


def solid_rgb(height: int, width: int, rgb: tuple[int, int, int]) -> np.ndarray:
    if height < 1 or width < 1:
        raise ValueError("height and width must be positive")
    if any(not 0 <= x <= 255 for x in rgb):
        raise ValueError("RGB components must be in range 0..255")

    image = np.empty((height, width, 3), dtype=np.uint8)
    image[:] = rgb
    return image


def rgb_to_gray(rgb: np.ndarray) -> np.ndarray:
    """Y = (77R + 150G + 29B + 128) >> 8."""
    _require_rgb(rgb)

    wide = rgb.astype(np.uint32)
    y = (
        77 * wide[..., 0]
        + 150 * wide[..., 1]
        + 29 * wide[..., 2]
        + 128
    ) >> 8

    return y.astype(np.uint8)


def sobel_gray(
    gray: np.ndarray,
    threshold: int = 128,
    bypass_threshold: bool = False,
) -> np.ndarray:
    """Apply frozen zero-border Sobel/L1/clamp/threshold behaviour."""
    _require_gray(gray)

    height, width = gray.shape
    if height < 3 or width < 3:
        raise ValueError("image dimensions must both be at least 3")
    if not 0 <= threshold <= 255:
        raise ValueError("threshold must be in range 0..255")

    g = gray.astype(np.int32)

    p00 = g[:-2, :-2]
    p01 = g[:-2, 1:-1]
    p02 = g[:-2, 2:]
    p10 = g[1:-1, :-2]
    p12 = g[1:-1, 2:]
    p20 = g[2:, :-2]
    p21 = g[2:, 1:-1]
    p22 = g[2:, 2:]

    gx = -p00 + p02 - 2 * p10 + 2 * p12 - p20 + p22
    gy = -p00 - 2 * p01 - p02 + p20 + 2 * p21 + p22

    magnitude = np.abs(gx) + np.abs(gy)
    m8 = np.minimum(magnitude, 255).astype(np.uint8)

    if not bypass_threshold:
        m8 = np.where(m8 < threshold, 0, m8).astype(np.uint8)

    output = np.zeros_like(gray)
    output[1:-1, 1:-1] = m8
    return output


def sobel_rgb(
    rgb: np.ndarray,
    threshold: int = 128,
    bypass_threshold: bool = False,
) -> np.ndarray:
    return sobel_gray(
        rgb_to_gray(rgb),
        threshold=threshold,
        bypass_threshold=bypass_threshold,
    )


def compare_gray(
    expected: np.ndarray,
    actual: np.ndarray,
    max_report: int = 16,
) -> dict:
    _require_gray(expected)
    _require_gray(actual)

    if expected.shape != actual.shape:
        raise ValueError("expected and actual shapes differ")
    if max_report < 0:
        raise ValueError("max_report must be non-negative")

    mismatch_mask = expected != actual
    coordinates = np.argwhere(mismatch_mask)[:max_report]

    mismatches = [
        (
            int(row),
            int(col),
            int(expected[row, col]),
            int(actual[row, col]),
        )
        for row, col in coordinates
    ]

    diff = np.abs(
        expected.astype(np.int16) - actual.astype(np.int16)
    ).astype(np.uint8)

    return {
        "mismatch_count": int(np.count_nonzero(mismatch_mask)),
        "mismatches": mismatches,
        "diff": diff,
    }


def load_rgb(path: str | Path) -> np.ndarray:
    with Image.open(path) as image:
        return np.array(image.convert("RGB"), dtype=np.uint8)


def save_rgb(path: str | Path, image: np.ndarray) -> None:
    _require_rgb(image)
    Image.fromarray(image).save(path)


def save_gray(path: str | Path, image: np.ndarray) -> None:
    _require_gray(image)
    Image.fromarray(image).save(path)


def save_diff(
    path: str | Path,
    expected: np.ndarray,
    actual: np.ndarray,
) -> None:
    result = compare_gray(expected, actual)
    save_gray(path, result["diff"])
