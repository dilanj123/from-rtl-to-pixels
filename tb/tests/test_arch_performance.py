import json
import os

import cocotb
import numpy as np
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

W = int(os.environ.get("IMG_WIDTH", "640"))
H = int(os.environ.get("IMG_HEIGHT", "480"))
N = W * H


def pixel(i):
    row, col = divmod(i, W)
    return (
        (17 * row + 31 * col + 3) & 255,
        (43 * row + 11 * col + 19) & 255,
        (7 * row + 53 * col + 101) & 255,
    )


def pack(pixel_value):
    return (pixel_value[0] << 16) | (pixel_value[1] << 8) | pixel_value[2]


async def settle():
    await Timer(1, units="ns")


async def apb(d,addr,val=None):
    d.psel.value = 1
    d.penable.value = 0
    d.pwrite.value = int(val is not None)
    d.paddr.value = addr
    d.pwdata.value = 0 if val is None else val
    await RisingEdge(d.clk)
    d.penable.value = 1
    await settle()
    output = int(d.prdata.value)
    assert int(d.pready.value) == 1
    assert int(d.pslverr.value) == 0
    await RisingEdge(d.clk)
    d.psel.value = 0
    d.penable.value = 0
    d.pwrite.value = 0
    return output


@cocotb.test()
async def canonical_performance(d):
    cocotb.start_soon(Clock(d.clk, 10, units="ns").start())
    initial_values = {
        "rst": 1,
        "s_tvalid": 0,
        "m_tready": 0,
        "psel": 0,
        "penable": 0,
        "pwrite": 0,
        "paddr": 0,
        "pwdata": 0,
        "s_tdata": 0,
        "s_tuser": 0,
        "s_tlast": 0,
    }
    for signal, value in initial_values.items():
        getattr(d, signal).value = value

    await RisingEdge(d.clk)
    await RisingEdge(d.clk)
    d.rst.value = 0
    await apb(d, 0, 3)
    await apb(d, 4, 0)

    d.m_tready.value = 1
    input_cycles = []
    output_cycles = []
    outputs = []
    inputs_accepted = 0
    cycle = 0

    while len(output_cycles) < N:
        if inputs_accepted < N:
            d.s_tdata.value = pack(pixel(inputs_accepted))
            d.s_tvalid.value = 1
            d.s_tuser.value = int(inputs_accepted == 0)
            d.s_tlast.value = int(inputs_accepted % W == W - 1)
        else:
            d.s_tvalid.value = 0
            d.s_tuser.value = 0
            d.s_tlast.value = 0

        await settle()
        if int(d.s_tvalid.value) and int(d.s_tready.value):
            input_cycles.append(cycle)
            inputs_accepted += 1
        if int(d.m_tvalid.value) and int(d.m_tready.value):
            output_cycles.append(cycle)
            outputs.append(int(d.m_tdata.value))
            assert int(d.m_tuser.value) == (len(outputs) == 1)
            assert int(d.m_tlast.value) == ((len(outputs) - 1) % W == W - 1)

        await RisingEdge(d.clk)
        cycle += 1
        if cycle > 2 * N + 5000:
            raise AssertionError("performance timeout")

    assert inputs_accepted == N
    assert len(outputs) == N
    frame_count = await apb(d, 12)

    def deltas(cycles):
        return [later - earlier for earlier, later in zip(cycles, cycles[1:])]

    input_ii = deltas(input_cycles)
    output_ii = deltas(output_cycles)
    result = {
        "dimensions": f"{W}x{H}",
        "accepted_input_count": inputs_accepted,
        "accepted_output_count": len(outputs),
        "frame_count": frame_count,
        "first_input_cycle": input_cycles[0],
        "last_input_cycle": input_cycles[-1],
        "first_output_cycle": output_cycles[0],
        "last_output_cycle": output_cycles[-1],
        "first_output_latency_cycles": output_cycles[0] - input_cycles[0],
        "frame_completion_cycles": output_cycles[-1] - input_cycles[0] + 1,
        "input_ii_min": min(input_ii),
        "input_ii_max": max(input_ii),
        "output_ii_min": min(output_ii),
        "output_ii_max": max(output_ii),
        "metadata_correct": True,
    }
    with open(os.environ["PERF_JSON"], "w") as handle:
        json.dump(result, handle, indent=2)
    print("PERF_RESULT", json.dumps(result, sort_keys=True))
    assert frame_count == 1
    assert result["input_ii_max"] == 1
    assert result["output_ii_max"] == 1
