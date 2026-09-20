import hashlib
import os
from pathlib import Path

import cocotb
import numpy as np
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

from tb.reference.sobel_reference import compare_gray, load_rgb, save_diff, save_gray, sobel_rgb

W = int(os.environ["IMG_WIDTH"])
H = int(os.environ["IMG_HEIGHT"])
N = W * H
CASE_KIND = os.environ.get("CASE_KIND", "random")
IMAGE_PATH = os.environ.get("IMAGE_PATH", "")
RESULTS_DIR = Path(os.environ.get("RESULTS_DIR", "results/processed"))
CONTROL, THRESHOLD, STATUS, FRAME_COUNT = 0x00, 0x04, 0x08, 0x0C


async def settle():
    await Timer(1, unit="ns")


def coord(index):
    return divmod(index, W)


def pack_rgb(pixel):
    return (int(pixel[0]) << 16) | (int(pixel[1]) << 8) | int(pixel[2])


def idle(dut):
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


def drive(dut, image, index):
    row, col = coord(index)
    dut.s_tdata.value = pack_rgb(image[row, col])
    dut.s_tvalid.value = 1
    dut.s_tuser.value = int(index == 0)
    dut.s_tlast.value = int(col == W - 1)


async def reset(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst.value = 1
    idle(dut); apb_idle(dut); dut.m_tready.value = 0
    await RisingEdge(dut.clk); await RisingEdge(dut.clk); await settle()
    dut.rst.value = 0; await settle()
    assert int(dut.m_tvalid.value) == 0


async def apb_read(dut, addr):
    dut.psel.value = 1; dut.penable.value = 0; dut.pwrite.value = 0
    dut.paddr.value = addr; dut.pwdata.value = 0
    await RisingEdge(dut.clk)
    dut.penable.value = 1; await settle()
    assert int(dut.pready.value) == 1 and int(dut.pslverr.value) == 0
    value = int(dut.prdata.value)
    await RisingEdge(dut.clk); apb_idle(dut); await settle()
    return value


async def apb_write(dut, addr, value):
    dut.psel.value = 1; dut.penable.value = 0; dut.pwrite.value = 1
    dut.paddr.value = addr; dut.pwdata.value = value
    await RisingEdge(dut.clk)
    dut.penable.value = 1; await settle()
    assert int(dut.pready.value) == 1 and int(dut.pslverr.value) == 0
    await RisingEdge(dut.clk); apb_idle(dut); await settle()


async def configure(dut, threshold, bypass):
    await apb_write(dut, CONTROL, 1 | (int(bool(bypass)) << 1))
    await apb_write(dut, THRESHOLD, threshold)


def random_image(seed):
    return np.random.default_rng(seed).integers(0, 256, size=(H, W, 3), dtype=np.uint8)


async def run_frame(dut, image, threshold, bypass, label):
    await configure(dut, threshold, bypass)
    accepted = 0; outputs = []; dut.m_tready.value = 1
    for cycle in range(4 * N + 4 * W + 5000):
        if accepted < N: drive(dut, image, accepted)
        else: idle(dut)
        await settle()
        input_transfer = bool(int(dut.s_tvalid.value) and int(dut.s_tready.value))
        output_transfer = bool(int(dut.m_tvalid.value) and int(dut.m_tready.value))
        if output_transfer:
            oi = len(outputs); _row, col = coord(oi)
            assert int(dut.m_tuser.value) == int(oi == 0)
            assert int(dut.m_tlast.value) == int(col == W - 1)
            outputs.append(int(dut.m_tdata.value))
        await RisingEdge(dut.clk)
        if input_transfer: accepted += 1
        await settle()
        if accepted == N and len(outputs) == N:
            total_cycles = cycle + 1; break
    else:
        raise AssertionError(f"{label}: frame timeout")
    idle(dut); dut.m_tready.value = 1; await settle()
    assert int(dut.m_tvalid.value) == 0
    actual = np.array(outputs, dtype=np.uint8).reshape(H, W)
    expected = sobel_rgb(image, threshold=threshold, bypass_threshold=bool(bypass))
    result = compare_gray(expected, actual)
    digest = hashlib.sha256(image.tobytes()).hexdigest()
    print(f"dimension image frame: label={label} width={W} height={H} threshold={threshold} bypass={bypass} accepted_input={accepted} accepted_output={len(outputs)} mismatch_count={result['mismatch_count']} cycles={total_cycles} input_sha256={digest}")
    assert accepted == N and len(outputs) == N and result["mismatch_count"] == 0, result.get("mismatches")
    assert (await apb_read(dut, STATUS) & 0xF) == 0
    return actual, expected, result


@cocotb.test()
async def dimension_and_image_regression(dut):
    await reset(dut)
    if CASE_KIND == "random":
        configs = [(17, 0), (128, 1), (223, 0)]
        for frame_index, (threshold, bypass) in enumerate(configs):
            seed = (0xC0FFEE ^ (W << 20) ^ (H << 8) ^ (frame_index * 0x9E3779B1)) & 0xFFFFFFFF
            await run_frame(dut, random_image(seed), threshold, bypass, f"random-{frame_index}")
            assert await apb_read(dut, FRAME_COUNT) == frame_index + 1
        print(f"dimension random summary: width={W} height={H} frames=3 final_frame_count={await apb_read(dut, FRAME_COUNT)}")
    elif CASE_KIND == "real":
        path = Path(IMAGE_PATH); assert IMAGE_PATH and path.is_file()
        image = load_rgb(path); assert image.shape == (H, W, 3), image.shape
        print(f"real image provenance: path={path} width={W} height={H} file_sha256={hashlib.sha256(path.read_bytes()).hexdigest()}")
        actual, expected, result = await run_frame(dut, image, 128, 0, "public-real-image")
        assert await apb_read(dut, FRAME_COUNT) == 1
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        ref = RESULTS_DIR / "gate3-real-reference.png"
        rtl = RESULTS_DIR / "gate3-real-rtl.png"
        diff = RESULTS_DIR / "gate3-real-diff.png"
        save_gray(ref, expected); save_gray(rtl, actual); save_diff(diff, expected, actual)
        assert result["mismatch_count"] == 0 and np.count_nonzero(result["diff"]) == 0
        print(f"real image outputs: reference={ref} rtl={rtl} diff={diff} diff_nonzero=0")
    else:
        raise AssertionError("CASE_KIND must be 'random' or 'real'")
