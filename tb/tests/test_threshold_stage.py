import random

import cocotb
from cocotb.triggers import Timer


async def settle():
    await Timer(1, unit="ns")


def threshold_oracle(magnitude: int, threshold: int, bypass: int) -> int:
    assert 0 <= magnitude <= 255
    assert 0 <= threshold <= 255
    assert bypass in (0, 1)
    if bypass:
        return magnitude
    if magnitude < threshold:
        return 0
    return magnitude


async def check_values(dut, magnitude, threshold, bypass, *, expected=None, context=""):
    assert 0 <= magnitude <= 255
    assert 0 <= threshold <= 255
    assert bypass in (0, 1)
    dut.magnitude_i.value = magnitude
    dut.threshold_i.value = threshold
    dut.bypass_threshold_i.value = bypass
    await settle()
    oracle = threshold_oracle(magnitude, threshold, bypass)
    if expected is not None:
        assert oracle == expected, f"{context}: oracle disagreement expected={expected} oracle={oracle}"
    actual = int(dut.edge_o.value)
    assert actual == oracle, f"{context}: magnitude={magnitude} threshold={threshold} bypass={bypass} expected={oracle} actual={actual}"


@cocotb.test()
async def directed_boundary_semantics_are_exact(dut):
    cases = ((0, 0, 0, 0), (1, 0, 0, 1), (0, 1, 0, 0),
             (126, 128, 0, 0), (127, 128, 0, 0), (128, 128, 0, 128),
             (129, 128, 0, 129), (254, 255, 0, 0), (255, 255, 0, 255),
             (0, 255, 1, 0), (127, 255, 1, 127), (255, 255, 1, 255))
    for index, (magnitude, threshold, bypass, expected) in enumerate(cases):
        await check_values(dut, magnitude, threshold, bypass, expected=expected, context=f"directed case={index}")


@cocotb.test()
async def exhaustive_threshold_domain_matches_oracle(dut):
    for threshold in range(256):
        for magnitude in range(256):
            await check_values(dut, magnitude, threshold, 0, context=f"threshold mode magnitude={magnitude} threshold={threshold}")


@cocotb.test()
async def bypass_returns_input_exactly(dut):
    for threshold in (0, 1, 127, 255):
        for magnitude in range(256):
            await check_values(dut, magnitude, threshold, 1, expected=magnitude, context=f"bypass magnitude={magnitude} threshold={threshold}")


@cocotb.test()
async def deterministic_random_both_modes_match_oracle(dut):
    rng = random.Random(0x7A235)
    for vector_index in range(4096):
        await check_values(dut, rng.randrange(256), rng.randrange(256), rng.randrange(2), context=f"random vector={vector_index}")
