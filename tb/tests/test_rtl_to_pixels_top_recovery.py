import os

import cocotb
import numpy as np

from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

from tb.reference.sobel_reference import compare_gray, sobel_rgb


W = int(os.environ["IMG_WIDTH"])
H = int(os.environ["IMG_HEIGHT"])
N = W * H

CONTROL = 0x00
THRESHOLD = 0x04
STATUS = 0x08
FRAME_COUNT = 0x0C


async def settle():
    await Timer(1, unit="ns")


def coord(index):
    return divmod(index, W)


def deterministic_rgb(seed):
    rng = np.random.default_rng(seed)
    return rng.integers(
        0,
        256,
        size=(H, W, 3),
        dtype=np.uint8,
    )


def pack_rgb(pixel):
    return (
        (int(pixel[0]) << 16)
        | (int(pixel[1]) << 8)
        | int(pixel[2])
    )


def source_idle(dut):
    dut.s_tdata.value = 0
    dut.s_tvalid.value = 0
    dut.s_tuser.value = 0
    dut.s_tlast.value = 0


def drive_token(dut, image, index, user=None, last=None):
    row, col = coord(index)

    dut.s_tdata.value = pack_rgb(image[row, col])
    dut.s_tvalid.value = 1

    dut.s_tuser.value = (
        int(index == 0)
        if user is None
        else int(bool(user))
    )

    dut.s_tlast.value = (
        int(col == W - 1)
        if last is None
        else int(bool(last))
    )


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

    value = int(dut.prdata.value)

    await RisingEdge(dut.clk)

    dut.psel.value = 0
    dut.penable.value = 0
    dut.pwrite.value = 0
    dut.paddr.value = 0
    dut.pwdata.value = 0

    await settle()

    return value


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

    dut.psel.value = 0
    dut.penable.value = 0
    dut.pwrite.value = 0
    dut.paddr.value = 0
    dut.pwdata.value = 0

    await settle()


async def configure(dut, threshold, bypass):
    await apb_write(
        dut,
        CONTROL,
        1 | (int(bool(bypass)) << 1),
    )

    await apb_write(
        dut,
        THRESHOLD,
        threshold,
    )


async def pulse_reset(dut):
    source_idle(dut)

    dut.m_tready.value = 0

    dut.psel.value = 0
    dut.penable.value = 0
    dut.pwrite.value = 0
    dut.paddr.value = 0
    dut.pwdata.value = 0

    dut.rst.value = 1
    await settle()

    assert int(dut.s_tready.value) == 0

    await RisingEdge(dut.clk)
    await settle()

    assert int(dut.m_tvalid.value) == 0

    dut.rst.value = 0
    await settle()


async def start_and_reset(dut):
    cocotb.start_soon(
        Clock(dut.clk, 10, unit="ns").start()
    )

    dut.rst.value = 0

    source_idle(dut)
    dut.m_tready.value = 0

    dut.psel.value = 0
    dut.penable.value = 0
    dut.pwrite.value = 0
    dut.paddr.value = 0
    dut.pwdata.value = 0

    await pulse_reset(dut)


async def assert_reset_defaults(dut):
    assert int(dut.m_tvalid.value) == 0

    assert await apb_read(dut, CONTROL) == 0
    assert await apb_read(dut, THRESHOLD) == 128
    assert await apb_read(dut, STATUS) == 0
    assert await apb_read(dut, FRAME_COUNT) == 0

    image = deterministic_rgb(0x9000)

    drive_token(dut, image, 0)

    dut.m_tready.value = 1
    await settle()

    assert int(dut.s_tready.value) == 0

    source_idle(dut)


async def send_valid_prefix(dut, image, count):
    assert 0 <= count <= N

    transferred_outputs = 0

    dut.m_tready.value = 1

    for index in range(count):
        drive_token(dut, image, index)

        await settle()

        assert int(dut.s_tready.value) == 1

        if (
            int(dut.m_tvalid.value)
            and int(dut.m_tready.value)
        ):
            transferred_outputs += 1

        await RisingEdge(dut.clk)
        await settle()

    source_idle(dut)

    return transferred_outputs


async def run_complete_frame(
    dut,
    image,
    threshold,
    bypass,
    label,
):
    accepted_inputs = 0
    outputs = []

    dut.m_tready.value = 1

    max_cycles = 30 * N + 500

    for _cycle in range(max_cycles):
        if accepted_inputs < N:
            drive_token(
                dut,
                image,
                accepted_inputs,
            )
        else:
            source_idle(dut)

        await settle()

        input_transfer = bool(
            int(dut.s_tvalid.value)
            and int(dut.s_tready.value)
        )

        output_transfer = bool(
            int(dut.m_tvalid.value)
            and int(dut.m_tready.value)
        )

        if output_transfer:
            output_index = len(outputs)
            _row, col = coord(output_index)

            assert int(dut.m_tuser.value) == int(
                output_index == 0
            )

            assert int(dut.m_tlast.value) == int(
                col == W - 1
            )

            outputs.append(
                int(dut.m_tdata.value)
            )

            assert len(outputs) <= N

        await RisingEdge(dut.clk)

        if input_transfer:
            accepted_inputs += 1

        await settle()

        if (
            accepted_inputs == N
            and len(outputs) == N
        ):
            break
    else:
        raise AssertionError(
            f"{label}: complete-frame timeout"
        )

    source_idle(dut)
    dut.m_tready.value = 1

    await settle()

    assert int(dut.m_tvalid.value) == 0

    actual = np.array(
        outputs,
        dtype=np.uint8,
    ).reshape(H, W)

    expected = sobel_rgb(
        image,
        threshold=threshold,
        bypass_threshold=bool(bypass),
    )

    result = compare_gray(
        expected,
        actual,
    )

    print(
        "recovery frame: "
        f"label={label} "
        f"accepted_input={accepted_inputs} "
        f"accepted_output={len(outputs)} "
        f"mismatch_count={result['mismatch_count']}"
    )

    assert accepted_inputs == N
    assert len(outputs) == N
    assert result["mismatch_count"] == 0, (
        result["mismatches"]
    )


async def recover_after_reset(dut, label, seed):
    await assert_reset_defaults(dut)

    threshold = (53 + 17 * seed) & 0xFF
    bypass = seed & 1

    await configure(
        dut,
        threshold,
        bypass,
    )

    await run_complete_frame(
        dut,
        deterministic_rgb(0xA000 + seed),
        threshold,
        bypass,
        label,
    )

    assert await apb_read(
        dut,
        FRAME_COUNT,
    ) == 1

    assert (
        await apb_read(dut, STATUS)
        & 0xF
    ) == 0


async def reset_after_prefix(
    dut,
    prefix_count,
    label,
    seed,
):
    await start_and_reset(dut)

    await configure(
        dut,
        91,
        0,
    )

    await send_valid_prefix(
        dut,
        deterministic_rgb(0x8000 + seed),
        prefix_count,
    )

    assert await apb_read(
        dut,
        FRAME_COUNT,
    ) == 0

    await pulse_reset(dut)

    await recover_after_reset(
        dut,
        label,
        seed,
    )


async def send_malformed_token(
    dut,
    image,
    index,
    user,
    last,
):
    drive_token(
        dut,
        image,
        index,
        user=user,
        last=last,
    )

    dut.m_tready.value = 1

    await settle()

    assert int(dut.s_tready.value) == 1

    output_transfer = bool(
        int(dut.m_tvalid.value)
        and int(dut.m_tready.value)
    )

    await RisingEdge(dut.clk)

    source_idle(dut)

    await settle()

    assert int(dut.m_tvalid.value) == 0

    return int(output_transfer)


async def wait_for_prior_output_transfer(
    dut,
    label,
    max_wait_cycles=8,
):
    """
    Establish the architecture-neutral precondition for metadata-abort
    cases that explicitly require an output from the incomplete frame
    to have escaped before the malformed input is accepted.

    No input pixel is accepted while waiting.  Only already-created
    downstream tokens are allowed to advance.
    """
    source_idle(dut)
    dut.m_tready.value = 1

    for wait_cycle in range(max_wait_cycles):
        await settle()

        output_transfer = bool(
            int(dut.m_tvalid.value)
            and int(dut.m_tready.value)
        )

        await RisingEdge(dut.clk)
        await settle()

        if output_transfer:
            print(
                "partial-output precondition: "
                f"label={label} "
                f"extra_idle_cycles={wait_cycle + 1} "
                "prior_output_transfer=1"
            )
            return 1

    raise AssertionError(
        f"{label}: required prior external output transfer "
        f"not reached within {max_wait_cycles} source-idle cycles"
    )


async def abort_and_recover(
    dut,
    label,
    bad_index,
    bad_user,
    bad_last,
    require_prior_output,
    seed,
):
    await start_and_reset(dut)

    threshold = 119
    bypass = 1

    await configure(
        dut,
        threshold,
        bypass,
    )

    image = deterministic_rgb(
        0xB000 + seed
    )

    prior_outputs = await send_valid_prefix(
        dut,
        image,
        bad_index,
    )

    if (
        require_prior_output
        and prior_outputs == 0
    ):
        prior_outputs += await wait_for_prior_output_transfer(
            dut,
            label,
        )

    prior_outputs += await send_malformed_token(
        dut,
        image,
        bad_index,
        bad_user,
        bad_last,
    )

    if require_prior_output:
        assert prior_outputs > 0

    await RisingEdge(dut.clk)
    await settle()

    status = await apb_read(
        dut,
        STATUS,
    )

    assert ((status >> 3) & 1) == 1

    assert await apb_read(
        dut,
        FRAME_COUNT,
    ) == 0

    restart_probe = deterministic_rgb(
        0xC000 + seed
    )

    drive_token(
        dut,
        restart_probe,
        0,
        user=0,
        last=0,
    )

    dut.m_tready.value = 1

    await settle()

    assert int(dut.s_tready.value) == 0

    await RisingEdge(dut.clk)
    await settle()

    source_idle(dut)

    recovery = deterministic_rgb(
        0xD000 + seed
    )

    await run_complete_frame(
        dut,
        recovery,
        threshold,
        bypass,
        label,
    )

    assert await apb_read(
        dut,
        FRAME_COUNT,
    ) == 1

    status = await apb_read(
        dut,
        STATUS,
    )

    assert (status & 0x7) == 0
    assert ((status >> 3) & 1) == 1

    print(
        "metadata abort: "
        f"label={label} "
        f"bad_index={bad_index} "
        f"prior_output_transfers={prior_outputs} "
        "aborted_frame_count=0 "
        "recovered_frame_count=1"
    )

    await apb_write(
        dut,
        STATUS,
        0x0000_0008,
    )

    assert (
        await apb_read(dut, STATUS)
        & 0xF
    ) == 0


@cocotb.test()
async def idle_reset_restores_defaults_and_clean_recovery(dut):
    await start_and_reset(dut)

    await recover_after_reset(
        dut,
        "idle-reset",
        1,
    )


@cocotb.test()
async def reset_immediately_before_frame_blocks_acceptance(dut):
    await start_and_reset(dut)

    await configure(
        dut,
        77,
        1,
    )

    image = deterministic_rgb(0x8102)

    drive_token(dut, image, 0)

    dut.m_tready.value = 1

    await settle()

    assert int(dut.s_tready.value) == 1

    dut.rst.value = 1

    await settle()

    assert int(dut.s_tready.value) == 0

    await RisingEdge(dut.clk)
    await settle()

    source_idle(dut)

    assert int(dut.m_tvalid.value) == 0

    dut.rst.value = 0
    await settle()

    await recover_after_reset(
        dut,
        "reset-before-frame",
        2,
    )


@cocotb.test()
async def reset_after_first_accepted_pixel_recovers(dut):
    await reset_after_prefix(
        dut,
        1,
        "reset-after-first-pixel",
        3,
    )


@cocotb.test()
async def reset_mid_line_recovers(dut):
    await reset_after_prefix(
        dut,
        2,
        "reset-mid-line",
        4,
    )


@cocotb.test()
async def reset_after_eol_recovers(dut):
    await reset_after_prefix(
        dut,
        W,
        "reset-after-eol",
        5,
    )


@cocotb.test()
async def reset_late_frame_recovers(dut):
    await reset_after_prefix(
        dut,
        N - 1,
        "reset-late-frame",
        6,
    )


@cocotb.test()
async def reset_during_drain_recovers(dut):
    await start_and_reset(dut)

    await configure(
        dut,
        101,
        0,
    )

    image = deterministic_rgb(0x8207)

    await send_valid_prefix(
        dut,
        image,
        N,
    )

    dut.m_tready.value = 0
    await settle()

    status = await apb_read(
        dut,
        STATUS,
    )

    assert (status & 0x1) == 1
    assert ((status >> 1) & 1) == 1

    assert await apb_read(
        dut,
        FRAME_COUNT,
    ) == 0

    await pulse_reset(dut)

    await recover_after_reset(
        dut,
        "reset-during-drain",
        7,
    )


@cocotb.test()
async def early_eol_aborts_and_recovers(dut):
    await abort_and_recover(
        dut,
        "early-eol",
        1,
        0,
        1,
        False,
        8,
    )


@cocotb.test()
async def missing_row_eol_aborts_and_recovers(dut):
    await abort_and_recover(
        dut,
        "missing-row-eol",
        W - 1,
        0,
        0,
        False,
        9,
    )


@cocotb.test()
async def unexpected_sof_after_partial_output_aborts_and_recovers(dut):
    bad_index = min(
        N - 2,
        W + 2,
    )

    _row, col = coord(bad_index)

    await abort_and_recover(
        dut,
        "unexpected-sof",
        bad_index,
        1,
        int(col == W - 1),
        True,
        10,
    )


@cocotb.test()
async def missing_final_eol_aborts_without_frame_completion(dut):
    await abort_and_recover(
        dut,
        "missing-final-eol",
        N - 1,
        0,
        0,
        True,
        11,
    )
