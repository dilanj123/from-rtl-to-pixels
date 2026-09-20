import random

import cocotb
from cocotb.triggers import Timer

MIN_GRADIENT = -1020
MAX_GRADIENT = 1020

async def settle():
    await Timer(1, unit="ns")

def magnitude_oracle(gx: int, gy: int):
    assert MIN_GRADIENT <= gx <= MAX_GRADIENT
    assert MIN_GRADIENT <= gy <= MAX_GRADIENT
    magnitude = abs(gx) + abs(gy)
    assert 0 <= magnitude <= 2040
    return magnitude, min(magnitude, 255)

def signed12_raw(value: int) -> int:
    assert -(1 << 11) <= value < (1 << 11)
    return value & 0xFFF

async def check_values(dut, gx: int, gy: int, *, expected=None, context=""):
    assert MIN_GRADIENT <= gx <= MAX_GRADIENT
    assert MIN_GRADIENT <= gy <= MAX_GRADIENT
    dut.gx_i.value = signed12_raw(gx)
    dut.gy_i.value = signed12_raw(gy)
    await settle()
    oracle = magnitude_oracle(gx, gy)
    if expected is not None:
        assert oracle == expected, f"{context}: oracle disagreement expected={expected} oracle={oracle}"
    actual = (int(dut.magnitude_o.value), int(dut.magnitude_clamped_o.value))
    assert actual == oracle, f"{context}: gx={gx} gy={gy} expected={oracle} actual={actual}"
    return actual

@cocotb.test()
async def zero_small_values_and_absolute_signs(dut):
    cases = ((0, 0, (0, 0)), (1, 0, (1, 1)), (-1, 0, (1, 1)), (0, 1, (1, 1)), (0, -1, (1, 1)), (127, -63, (190, 190)), (-127, 63, (190, 190)))
    for index, (gx, gy, expected) in enumerate(cases):
        await check_values(dut, gx, gy, expected=expected, context=f"small/sign case={index}")

@cocotb.test()
async def clamp_boundary_is_exact(dut):
    cases = ((254, 0, (254, 254)), (255, 0, (255, 255)), (256, 0, (256, 255)), (128, 127, (255, 255)), (128, 128, (256, 255)), (-128, 127, (255, 255)), (-128, -128, (256, 255)))
    for index, (gx, gy, expected) in enumerate(cases):
        await check_values(dut, gx, gy, expected=expected, context=f"clamp boundary case={index}")

@cocotb.test()
async def maximum_required_gradient_cases(dut):
    cases = ((1020, 0, (1020, 255)), (-1020, 0, (1020, 255)), (0, 1020, (1020, 255)), (0, -1020, (1020, 255)), (1020, 1020, (2040, 255)), (1020, -1020, (2040, 255)), (-1020, 1020, (2040, 255)), (-1020, -1020, (2040, 255)))
    for index, (gx, gy, expected) in enumerate(cases):
        await check_values(dut, gx, gy, expected=expected, context=f"maximum-range case={index}")

@cocotb.test()
async def sign_symmetry_is_exact(dut):
    magnitudes = ((3, 7), (100, 200), (255, 765), (511, 509), (1020, 1020))
    for gx_abs, gy_abs in magnitudes:
        expected = magnitude_oracle(gx_abs, gy_abs)
        for gx_sign in (-1, 1):
            for gy_sign in (-1, 1):
                await check_values(dut, gx_sign * gx_abs, gy_sign * gy_abs, expected=expected, context=f"sign symmetry gx_abs={gx_abs} gy_abs={gy_abs} gx_sign={gx_sign} gy_sign={gy_sign}")

@cocotb.test()
async def exhaustive_gx_axis_matches_oracle(dut):
    for gx in range(MIN_GRADIENT, MAX_GRADIENT + 1):
        await check_values(dut, gx, 0, context=f"gx-axis gx={gx}")

@cocotb.test()
async def exhaustive_gy_axis_matches_oracle(dut):
    for gy in range(MIN_GRADIENT, MAX_GRADIENT + 1):
        await check_values(dut, 0, gy, context=f"gy-axis gy={gy}")

@cocotb.test()
async def deterministic_random_gradient_pairs_match_oracle(dut):
    rng = random.Random(0xC1A4F)
    for vector_index in range(4096):
        gx = rng.randint(MIN_GRADIENT, MAX_GRADIENT)
        gy = rng.randint(MIN_GRADIENT, MAX_GRADIENT)
        await check_values(dut, gx, gy, context=f"random vector={vector_index}")
