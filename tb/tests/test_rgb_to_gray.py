import numpy as np
import cocotb
from cocotb.triggers import Timer

from tb.reference.sobel_reference import rgb_to_gray


async def check_rgb(dut, r: int, g: int, b: int) -> None:
    dut.rgb_i.value = (r << 16) | (g << 8) | b
    await Timer(1, unit="ns")

    rgb = np.array([[[r, g, b]]], dtype=np.uint8)
    expected = int(rgb_to_gray(rgb)[0, 0])

    assert int(dut.gray_o.value) == expected, (
        f"RGB=({r},{g},{b}) "
        f"expected={expected} actual={int(dut.gray_o.value)}"
    )


@cocotb.test()
async def directed_values(dut):
    vectors = [
        (0, 0, 0),
        (255, 255, 255),
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (1, 0, 0),
        (2, 0, 0),
        (1, 1, 1),
        (127, 127, 127),
        (128, 128, 128),
        (254, 254, 254),
        (255, 128, 0),
        (17, 93, 201),
    ]

    for vector in vectors:
        await check_rgb(dut, *vector)


@cocotb.test()
async def grayscale_identity_exhaustive(dut):
    for value in range(256):
        await check_rgb(dut, value, value, value)


@cocotb.test()
async def deterministic_random_vectors(dut):
    rng = np.random.default_rng(0x534F4245)

    for r, g, b in rng.integers(
        0,
        256,
        size=(2048, 3),
        dtype=np.uint16,
    ):
        await check_rgb(dut, int(r), int(g), int(b))
