import numpy as np
import pytest

from tb.reference.sobel_reference import (
    compare_gray,
    load_rgb,
    rgb_to_gray,
    save_gray,
    save_rgb,
    sobel_gray,
    sobel_rgb,
    solid_rgb,
)


def test_grayscale_known_values():
    rgb = np.array(
        [[
            [0, 0, 0],
            [255, 255, 255],
            [255, 0, 0],
            [0, 255, 0],
            [0, 0, 255],
        ]],
        dtype=np.uint8,
    )

    assert rgb_to_gray(rgb).tolist() == [[0, 255, 77, 149, 29]]


def test_grayscale_rounding_boundary():
    rgb = np.array(
        [[[1, 0, 0], [2, 0, 0]]],
        dtype=np.uint8,
    )

    assert rgb_to_gray(rgb).tolist() == [[0, 1]]


@pytest.mark.parametrize(
    "gray",
    [
        np.array([[0, 0, 10]] * 3, dtype=np.uint8),
        np.array([[10, 10, 0]] * 3, dtype=np.uint8),
        np.array([[0, 0, 0], [0, 0, 0], [10, 10, 10]], dtype=np.uint8),
        np.array([[10, 10, 10], [0, 0, 0], [0, 0, 0]], dtype=np.uint8),
    ],
)
def test_edge_polarities_have_expected_l1_magnitude(gray):
    out = sobel_gray(gray, bypass_threshold=True)

    assert out[1, 1] == 40
    assert np.count_nonzero(out) == 1


def test_threshold_equal_below_and_bypass():
    gray = np.array([[0, 0, 10]] * 3, dtype=np.uint8)

    assert sobel_gray(gray, threshold=40)[1, 1] == 40
    assert sobel_gray(gray, threshold=41)[1, 1] == 0
    assert sobel_gray(gray, threshold=255, bypass_threshold=True)[1, 1] == 40


def test_saturation_and_zero_borders():
    gray = np.array([[0, 0, 255]] * 3, dtype=np.uint8)

    out = sobel_gray(gray, bypass_threshold=True)

    assert out[1, 1] == 255
    assert np.all(out[0, :] == 0)
    assert np.all(out[-1, :] == 0)
    assert np.all(out[:, 0] == 0)
    assert np.all(out[:, -1] == 0)


def test_complete_vertical_edge_image():
    gray = np.array(
        [
            [0, 0, 255, 255, 255],
            [0, 0, 255, 255, 255],
            [0, 0, 255, 255, 255],
            [0, 0, 255, 255, 255],
            [0, 0, 255, 255, 255],
        ],
        dtype=np.uint8,
    )
    rgb = np.repeat(gray[..., None], 3, axis=2)

    expected = np.array(
        [
            [0, 0, 0, 0, 0],
            [0, 255, 255, 0, 0],
            [0, 255, 255, 0, 0],
            [0, 255, 255, 0, 0],
            [0, 0, 0, 0, 0],
        ],
        dtype=np.uint8,
    )

    np.testing.assert_array_equal(
        sobel_rgb(rgb, bypass_threshold=True),
        expected,
    )


def test_compare_gray_reports_coordinates_values_and_diff():
    expected = np.array([[0, 1], [2, 3]], dtype=np.uint8)
    actual = np.array([[0, 2], [2, 1]], dtype=np.uint8)

    result = compare_gray(expected, actual)

    assert result["mismatch_count"] == 2
    assert result["mismatches"] == [
        (0, 1, 1, 2),
        (1, 1, 3, 1),
    ]
    np.testing.assert_array_equal(
        result["diff"],
        np.array([[0, 1], [0, 2]], dtype=np.uint8),
    )


def test_image_io_and_generation(tmp_path):
    rgb = solid_rgb(3, 4, (12, 34, 56))

    rgb_path = tmp_path / "rgb.png"
    gray_path = tmp_path / "gray.png"

    save_rgb(rgb_path, rgb)
    np.testing.assert_array_equal(load_rgb(rgb_path), rgb)

    gray = rgb_to_gray(rgb)
    save_gray(gray_path, gray)

    assert gray_path.exists()


@pytest.mark.parametrize("shape", [(2, 3), (3, 2)])
def test_sobel_rejects_illegal_dimensions(shape):
    gray = np.zeros(shape, dtype=np.uint8)

    with pytest.raises(ValueError):
        sobel_gray(gray)
