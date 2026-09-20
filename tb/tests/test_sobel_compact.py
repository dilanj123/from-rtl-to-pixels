import random

import cocotb
from cocotb.triggers import Timer


TAP_NAMES = (
    "p00_i",
    "p01_i",
    "p02_i",
    "p10_i",
    "p12_i",
    "p20_i",
    "p21_i",
    "p22_i",
)

GX_COEFFS = (
    -1,
    0,
    +1,
    -2,
    +2,
    -1,
    0,
    +1,
)

GY_COEFFS = (
    -1,
    -2,
    -1,
    0,
    0,
    +1,
    +2,
    +1,
)


async def settle():
    await Timer(1, unit="ns")


def sobel_oracle(values):
    (
        p00,
        p01,
        p02,
        p10,
        p12,
        p20,
        p21,
        p22,
    ) = values

    gx = (
        -p00
        + p02
        - 2 * p10
        + 2 * p12
        - p20
        + p22
    )

    gy = (
        -p00
        - 2 * p01
        - p02
        + p20
        + 2 * p21
        + p22
    )

    assert -1020 <= gx <= 1020
    assert -1020 <= gy <= 1020

    return gx, gy


def signed12(signal):
    raw = int(signal.value)

    assert 0 <= raw < (1 << 12)

    if raw & (1 << 11):
        raw -= 1 << 12

    return raw


async def check_values(
    dut,
    values,
    *,
    expected=None,
    context="",
):
    assert len(values) == len(TAP_NAMES)

    for name, value in zip(TAP_NAMES, values):
        assert 0 <= value <= 255
        getattr(dut, name).value = value

    await settle()

    oracle = sobel_oracle(values)

    if expected is not None:
        assert oracle == expected, (
            f"{context}: oracle disagreement "
            f"expected={expected} oracle={oracle}"
        )

    actual = (
        signed12(dut.gx_o),
        signed12(dut.gy_o),
    )

    assert actual == oracle, (
        f"{context}: values={values} "
        f"expected={oracle} actual={actual}"
    )

    return actual


@cocotb.test()
async def flat_windows_have_zero_gradient(dut):
    for value in (0, 1, 127, 255):
        values = (value,) * 8

        await check_values(
            dut,
            values,
            expected=(0, 0),
            context=f"flat value={value}",
        )


@cocotb.test()
async def individual_tap_coefficients_are_exact(dut):
    for tap_index, tap_name in enumerate(TAP_NAMES):
        values = [0] * 8
        values[tap_index] = 255

        expected = (
            GX_COEFFS[tap_index] * 255,
            GY_COEFFS[tap_index] * 255,
        )

        await check_values(
            dut,
            tuple(values),
            expected=expected,
            context=f"single active tap {tap_name}",
        )


@cocotb.test()
async def vertical_edges_reach_both_gx_extremes(dut):
    positive = (
        0,
        0,
        255,
        0,
        255,
        0,
        0,
        255,
    )

    negative = (
        255,
        0,
        0,
        255,
        0,
        255,
        0,
        0,
    )

    await check_values(
        dut,
        positive,
        expected=(1020, 0),
        context="positive vertical edge",
    )

    await check_values(
        dut,
        negative,
        expected=(-1020, 0),
        context="negative vertical edge",
    )


@cocotb.test()
async def horizontal_edges_reach_both_gy_extremes(dut):
    positive = (
        0,
        0,
        0,
        0,
        0,
        255,
        255,
        255,
    )

    negative = (
        255,
        255,
        255,
        0,
        0,
        0,
        0,
        0,
    )

    await check_values(
        dut,
        positive,
        expected=(0, 1020),
        context="positive horizontal edge",
    )

    await check_values(
        dut,
        negative,
        expected=(0, -1020),
        context="negative horizontal edge",
    )


@cocotb.test()
async def asymmetric_window_checks_kernel_orientation(dut):
    values = (
        1,
        2,
        3,
        4,
        6,
        7,
        8,
        9,
    )

    await check_values(
        dut,
        values,
        expected=(8, 24),
        context="asymmetric orientation window",
    )


@cocotb.test()
async def exhaustive_binary_extreme_windows(dut):
    observed_gx = []
    observed_gy = []

    for pattern in range(1 << 8):
        values = tuple(
            255 if (pattern >> bit) & 1 else 0
            for bit in range(8)
        )

        gx, gy = await check_values(
            dut,
            values,
            context=f"binary pattern=0x{pattern:02x}",
        )

        observed_gx.append(gx)
        observed_gy.append(gy)

    assert min(observed_gx) == -1020
    assert max(observed_gx) == 1020

    assert min(observed_gy) == -1020
    assert max(observed_gy) == 1020


@cocotb.test()
async def deterministic_random_windows_match_oracle(dut):
    rng = random.Random(0x50BE1)

    for vector_index in range(4096):
        values = tuple(
            rng.randrange(256)
            for _ in range(8)
        )

        await check_values(
            dut,
            values,
            context=f"random vector={vector_index}",
        )
