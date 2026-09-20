import os

import cocotb
import numpy as np
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

from tb.reference.sobel_reference import compare_gray, sobel_rgb


W = int(os.environ["IMG_WIDTH"])
H = int(os.environ["IMG_HEIGHT"])
N = W * H
CONTROL, THRESHOLD, STATUS, FRAME_COUNT = 0x00, 0x04, 0x08, 0x0C


async def settle():
    await Timer(1, unit="ns")


def coord(index):
    return divmod(index, W)


def ramp_rgb(offset=32):
    image = np.empty((H, W, 3), dtype=np.uint8)
    for row in range(H):
        for col in range(W):
            value = offset + row + col
            assert 0 <= value <= 255
            image[row, col] = value
    return image


def pack_rgb(pixel):
    return (int(pixel[0]) << 16) | (int(pixel[1]) << 8) | int(pixel[2])


def source_idle(dut):
    dut.s_tdata.value = 0
    dut.s_tvalid.value = 0
    dut.s_tuser.value = 0
    dut.s_tlast.value = 0


def apb_idle(dut):
    dut.psel.value = 0
    dut.penable.value = 0
    dut.pwrite.value = 0
    dut.paddr.value = 0
    dut.pwdata.value = 0


def drive_token(dut, image, index):
    row, col = coord(index)
    dut.s_tdata.value = pack_rgb(image[row, col])
    dut.s_tvalid.value = 1
    dut.s_tuser.value = int(index == 0)
    dut.s_tlast.value = int(col == W - 1)


async def start_and_reset(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst.value = 1
    source_idle(dut)
    dut.m_tready.value = 0
    apb_idle(dut)
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    await settle()
    dut.rst.value = 0
    await settle()
    assert int(dut.m_tvalid.value) == 0


async def apb_read(dut, addr):
    dut.psel.value = 1
    dut.penable.value = 0
    dut.pwrite.value = 0
    dut.paddr.value = addr
    dut.pwdata.value = 0
    await RisingEdge(dut.clk)
    dut.penable.value = 1
    await settle()
    assert int(dut.pready.value) == 1
    assert int(dut.pslverr.value) == 0
    result = int(dut.prdata.value)
    await RisingEdge(dut.clk)
    apb_idle(dut)
    await settle()
    return result


async def apb_write(dut, addr, value):
    dut.psel.value = 1
    dut.penable.value = 0
    dut.pwrite.value = 1
    dut.paddr.value = addr
    dut.pwdata.value = value
    await RisingEdge(dut.clk)
    dut.penable.value = 1
    await settle()
    assert int(dut.pready.value) == 1
    assert int(dut.pslverr.value) == 0
    await RisingEdge(dut.clk)
    apb_idle(dut)
    await settle()


async def configure(dut, threshold, bypass, run_enable=1):
    await apb_write(dut, CONTROL, int(bool(run_enable)) | (int(bool(bypass)) << 1))
    await apb_write(dut, THRESHOLD, threshold)


async def accept_prefix(dut, image, count):
    assert 1 <= count <= W and count < N
    dut.m_tready.value = 1
    for index in range(count):
        drive_token(dut, image, index)
        await settle()
        assert int(dut.s_tready.value) == 1
        assert int(dut.m_tvalid.value) == 0
        await RisingEdge(dut.clk)
        await settle()
    source_idle(dut)
    return count


async def complete_frame(dut, image, start_index, threshold, bypass, label):
    accepted = start_index
    outputs = []
    dut.m_tready.value = 1
    for _ in range(30 * N + 500):
        if accepted < N:
            drive_token(dut, image, accepted)
        else:
            source_idle(dut)
        await settle()
        input_transfer = bool(int(dut.s_tvalid.value) and int(dut.s_tready.value))
        output_transfer = bool(int(dut.m_tvalid.value) and int(dut.m_tready.value))
        if output_transfer:
            oi = len(outputs)
            row, col = coord(oi)
            assert int(dut.m_tuser.value) == int(oi == 0)
            assert int(dut.m_tlast.value) == int(col == W - 1)
            outputs.append(int(dut.m_tdata.value))
        await RisingEdge(dut.clk)
        if input_transfer:
            accepted += 1
        await settle()
        if accepted == N and len(outputs) == N:
            break
    else:
        raise AssertionError(f"{label}: frame timeout")
    source_idle(dut)
    await settle()
    assert int(dut.m_tvalid.value) == 0
    actual = np.array(outputs, dtype=np.uint8).reshape(H, W)
    expected = sobel_rgb(image, threshold=threshold, bypass_threshold=bool(bypass))
    result = compare_gray(expected, actual)
    print(f"config frame: label={label} threshold={threshold} bypass={bypass} accepted_input={accepted} accepted_output={len(outputs)} mismatch_count={result['mismatch_count']}")
    assert accepted == N and len(outputs) == N
    assert result["mismatch_count"] == 0, result["mismatches"]


async def first_pixel(dut, image):
    drive_token(dut, image, 0)
    dut.m_tready.value = 1
    await settle()
    assert int(dut.s_tready.value) == 1
    await RisingEdge(dut.clk)
    source_idle(dut)
    await settle()
    return 1


async def same_edge_write_sof(dut, image, addr, value):
    source_idle(dut)
    dut.m_tready.value = 1
    dut.psel.value = 1
    dut.penable.value = 0
    dut.pwrite.value = 1
    dut.paddr.value = addr
    dut.pwdata.value = value
    await RisingEdge(dut.clk)
    dut.penable.value = 1
    drive_token(dut, image, 0)
    await settle()
    assert int(dut.pready.value) == 1
    assert int(dut.s_tready.value) == 1
    await RisingEdge(dut.clk)
    source_idle(dut)
    apb_idle(dut)
    await settle()
    return 1


def distinct(image, ta, ba, tb, bb):
    a = sobel_rgb(image, threshold=ta, bypass_threshold=bool(ba))
    b = sobel_rgb(image, threshold=tb, bypass_threshold=bool(bb))
    assert not np.array_equal(a, b)


@cocotb.test()
async def idle_shadow_write_sets_pending_and_sof_activates(dut):
    await start_and_reset(dut)
    image = ramp_rgb()
    await configure(dut, 20, 1)
    status = await apb_read(dut, STATUS)
    assert ((status >> 2) & 1) == 1 and (status & 1) == 0
    first = await first_pixel(dut, image)
    status = await apb_read(dut, STATUS)
    assert ((status >> 2) & 1) == 0 and (status & 1) == 1
    await complete_frame(dut, image, first, 20, 1, "idle-shadow-activation")
    assert await apb_read(dut, FRAME_COUNT) == 1
    assert (await apb_read(dut, STATUS) & 0xF) == 0


@cocotb.test()
async def midframe_threshold_write_applies_only_next_frame(dut):
    await start_and_reset(dut)
    image0, image1 = ramp_rgb(32), ramp_rgb(48)
    old, new = 10, 20
    distinct(image0, old, 0, new, 0); distinct(image1, old, 0, new, 0)
    await configure(dut, old, 0)
    prefix = await accept_prefix(dut, image0, W)
    assert ((await apb_read(dut, STATUS) >> 2) & 1) == 0
    await apb_write(dut, THRESHOLD, new)
    assert ((await apb_read(dut, STATUS) >> 2) & 1) == 1
    await complete_frame(dut, image0, prefix, old, 0, "midframe-threshold-current")
    assert await apb_read(dut, FRAME_COUNT) == 1
    status = await apb_read(dut, STATUS); assert ((status >> 2) & 1) == 1 and (status & 1) == 0
    first = await first_pixel(dut, image1)
    assert ((await apb_read(dut, STATUS) >> 2) & 1) == 0
    await complete_frame(dut, image1, first, new, 0, "midframe-threshold-next")
    assert await apb_read(dut, FRAME_COUNT) == 2


@cocotb.test()
async def midframe_bypass_write_applies_only_next_frame(dut):
    await start_and_reset(dut)
    image0, image1 = ramp_rgb(40), ramp_rgb(56)
    threshold = 20
    distinct(image0, threshold, 0, threshold, 1); distinct(image1, threshold, 0, threshold, 1)
    await configure(dut, threshold, 0)
    prefix = await accept_prefix(dut, image0, W)
    await apb_write(dut, CONTROL, 1 | (1 << 1))
    assert ((await apb_read(dut, STATUS) >> 2) & 1) == 1
    await complete_frame(dut, image0, prefix, threshold, 0, "midframe-bypass-current")
    status = await apb_read(dut, STATUS); assert ((status >> 2) & 1) == 1 and (status & 1) == 0
    first = await first_pixel(dut, image1)
    assert ((await apb_read(dut, STATUS) >> 2) & 1) == 0
    await complete_frame(dut, image1, first, threshold, 1, "midframe-bypass-next")
    assert await apb_read(dut, FRAME_COUNT) == 2


@cocotb.test()
async def same_edge_threshold_write_and_sof_uses_preedge_shadow(dut):
    await start_and_reset(dut)
    image0, image1 = ramp_rgb(36), ramp_rgb(52)
    old, new = 10, 20
    distinct(image0, old, 0, new, 0)
    await configure(dut, old, 0)
    first = await same_edge_write_sof(dut, image0, THRESHOLD, new)
    status = await apb_read(dut, STATUS); assert ((status >> 2) & 1) == 1 and (status & 1) == 1
    await complete_frame(dut, image0, first, old, 0, "same-edge-threshold-current")
    status = await apb_read(dut, STATUS); assert ((status >> 2) & 1) == 1 and (status & 1) == 0
    first = await first_pixel(dut, image1)
    assert ((await apb_read(dut, STATUS) >> 2) & 1) == 0
    await complete_frame(dut, image1, first, new, 0, "same-edge-threshold-next")
    assert await apb_read(dut, FRAME_COUNT) == 2


@cocotb.test()
async def same_edge_bypass_write_and_sof_uses_preedge_shadow(dut):
    await start_and_reset(dut)
    image0, image1 = ramp_rgb(44), ramp_rgb(60)
    threshold = 20
    distinct(image0, threshold, 0, threshold, 1)
    await configure(dut, threshold, 0)
    first = await same_edge_write_sof(dut, image0, CONTROL, 1 | (1 << 1))
    status = await apb_read(dut, STATUS); assert ((status >> 2) & 1) == 1 and (status & 1) == 1
    await complete_frame(dut, image0, first, threshold, 0, "same-edge-bypass-current")
    status = await apb_read(dut, STATUS); assert ((status >> 2) & 1) == 1 and (status & 1) == 0
    first = await first_pixel(dut, image1)
    assert ((await apb_read(dut, STATUS) >> 2) & 1) == 0
    await complete_frame(dut, image1, first, threshold, 1, "same-edge-bypass-next")
    assert await apb_read(dut, FRAME_COUNT) == 2


@cocotb.test()
async def run_enable_clear_midframe_finishes_current_and_blocks_next(dut):
    await start_and_reset(dut)
    image0, image1 = ramp_rgb(34), ramp_rgb(50)
    threshold = 10
    await configure(dut, threshold, 0)
    prefix = await accept_prefix(dut, image0, W)
    assert (await apb_read(dut, STATUS) & 1) == 1
    await apb_write(dut, CONTROL, 0)
    assert (await apb_read(dut, CONTROL) & 1) == 0
    await complete_frame(dut, image0, prefix, threshold, 0, "run-enable-current-frame")
    assert await apb_read(dut, FRAME_COUNT) == 1
    assert (await apb_read(dut, STATUS) & 0x3) == 0
    drive_token(dut, image1, 0); dut.m_tready.value = 1; await settle()
    assert int(dut.s_tready.value) == 0
    await RisingEdge(dut.clk); source_idle(dut); await settle()
    assert await apb_read(dut, FRAME_COUNT) == 1
    await apb_write(dut, CONTROL, 1)
    first = await first_pixel(dut, image1)
    await complete_frame(dut, image1, first, threshold, 0, "run-enable-reenabled-frame")
    assert await apb_read(dut, FRAME_COUNT) == 2
    assert (await apb_read(dut, STATUS) & 0xF) == 0
