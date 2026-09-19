import os

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


IMG_WIDTH = int(os.environ["IMG_WIDTH"])


def label(frame: int, row: int, col: int) -> int:
    return (97 * frame + 24 * row + col + 1) & 0xFF


async def settle():
    await Timer(1, unit="ns")


async def start_and_reset(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst.value = 1
    dut.pixel_commit_i.value = 0
    dut.frame_start_i.value = 0
    dut.col_i.value = 0
    dut.pixel_i.value = 0

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    await settle()

    dut.rst.value = 0
    await settle()

    assert int(dut.prev_row1_valid_o.value) == 0
    assert int(dut.prev_row2_valid_o.value) == 0
    assert int(dut.prev_row1_o.value) == 0
    assert int(dut.prev_row2_o.value) == 0


async def commit_pixel(
    dut,
    *,
    frame,
    row,
    col,
    expected_prev1=None,
    expected_prev2=None,
    frame_start=False,
):
    dut.pixel_commit_i.value = 1
    dut.frame_start_i.value = int(frame_start)
    dut.col_i.value = col
    dut.pixel_i.value = label(frame, row, col)

    # History must be visible before the committing rising edge.
    await settle()

    if expected_prev1 is None:
        assert int(dut.prev_row1_valid_o.value) == 0
        assert int(dut.prev_row1_o.value) == 0
    else:
        assert int(dut.prev_row1_valid_o.value) == 1
        assert int(dut.prev_row1_o.value) == expected_prev1

    if expected_prev2 is None:
        assert int(dut.prev_row2_valid_o.value) == 0
        assert int(dut.prev_row2_o.value) == 0
    else:
        assert int(dut.prev_row2_valid_o.value) == 1
        assert int(dut.prev_row2_o.value) == expected_prev2

    await RisingEdge(dut.clk)

    dut.pixel_commit_i.value = 0
    dut.frame_start_i.value = 0
    dut.pixel_i.value = 0

    await settle()

    assert int(dut.prev_row1_valid_o.value) == 0
    assert int(dut.prev_row2_valid_o.value) == 0
    assert int(dut.prev_row1_o.value) == 0
    assert int(dut.prev_row2_o.value) == 0


async def write_row(dut, frame: int, row: int):
    for col in range(IMG_WIDTH):
        await commit_pixel(
            dut,
            frame=frame,
            row=row,
            col=col,
            expected_prev1=(
                None
                if row == 0
                else label(frame, row - 1, col)
            ),
            expected_prev2=(
                None
                if row < 2
                else label(frame, row - 2, col)
            ),
            frame_start=(row == 0 and col == 0),
        )


@cocotb.test()
async def first_row_has_no_valid_history(dut):
    await start_and_reset(dut)

    for col in range(IMG_WIDTH):
        await commit_pixel(
            dut,
            frame=0,
            row=0,
            col=col,
            frame_start=(col == 0),
        )


@cocotb.test()
async def second_row_exposes_one_previous_row(dut):
    await start_and_reset(dut)

    await write_row(dut, 0, 0)

    for col in range(IMG_WIDTH):
        await commit_pixel(
            dut,
            frame=0,
            row=1,
            col=col,
            expected_prev1=label(0, 0, col),
        )


@cocotb.test()
async def third_and_later_rows_expose_two_previous_rows(dut):
    await start_and_reset(dut)

    await write_row(dut, 0, 0)
    await write_row(dut, 0, 1)

    for col in range(IMG_WIDTH):
        await commit_pixel(
            dut,
            frame=0,
            row=2,
            col=col,
            expected_prev1=label(0, 1, col),
            expected_prev2=label(0, 0, col),
        )

    for col in range(IMG_WIDTH):
        await commit_pixel(
            dut,
            frame=0,
            row=3,
            col=col,
            expected_prev1=label(0, 2, col),
            expected_prev2=label(0, 1, col),
        )


@cocotb.test()
async def exact_column_correspondence_across_row_boundary(dut):
    await start_and_reset(dut)

    await write_row(dut, 0, 0)

    for col in range(IMG_WIDTH):
        await commit_pixel(
            dut,
            frame=0,
            row=1,
            col=col,
            expected_prev1=label(0, 0, col),
        )

    await commit_pixel(
        dut,
        frame=0,
        row=2,
        col=0,
        expected_prev1=label(0, 1, 0),
        expected_prev2=label(0, 0, 0),
    )


@cocotb.test()
async def non_commit_cycles_do_not_modify_history(dut):
    await start_and_reset(dut)

    await write_row(dut, 0, 0)

    target = IMG_WIDTH // 2

    for col in range(target):
        await commit_pixel(
            dut,
            frame=0,
            row=1,
            col=col,
            expected_prev1=label(0, 0, col),
        )

    for bogus in (0xA5, 0x5A, 0xFF):
        dut.pixel_commit_i.value = 0
        dut.frame_start_i.value = 0
        dut.col_i.value = target
        dut.pixel_i.value = bogus

        await settle()

        assert int(dut.prev_row1_valid_o.value) == 0
        assert int(dut.prev_row2_valid_o.value) == 0
        assert int(dut.prev_row1_o.value) == 0
        assert int(dut.prev_row2_o.value) == 0

        await RisingEdge(dut.clk)
        await settle()

    await commit_pixel(
        dut,
        frame=0,
        row=1,
        col=target,
        expected_prev1=label(0, 0, target),
    )

    for col in range(target + 1, IMG_WIDTH):
        await commit_pixel(
            dut,
            frame=0,
            row=1,
            col=col,
            expected_prev1=label(0, 0, col),
        )

    for col in range(IMG_WIDTH):
        await commit_pixel(
            dut,
            frame=0,
            row=2,
            col=col,
            expected_prev1=label(0, 1, col),
            expected_prev2=label(0, 0, col),
        )


@cocotb.test()
async def reset_invalidates_old_memory_without_clearing_ram(dut):
    await start_and_reset(dut)

    await write_row(dut, 0, 0)
    await write_row(dut, 0, 1)
    await write_row(dut, 0, 2)

    dut.rst.value = 1
    dut.pixel_commit_i.value = 0
    dut.frame_start_i.value = 0

    await RisingEdge(dut.clk)
    await settle()

    dut.rst.value = 0
    await settle()

    assert int(dut.prev_row1_valid_o.value) == 0
    assert int(dut.prev_row2_valid_o.value) == 0

    # Distinct new-frame values ensure stale RAM would be visible if
    # history invalidation/update ordering were wrong.
    await write_row(dut, 1, 0)
    await write_row(dut, 1, 1)
    await write_row(dut, 1, 2)


@cocotb.test()
async def new_frame_start_invalidates_prior_frame_history(dut):
    await start_and_reset(dut)

    await write_row(dut, 0, 0)
    await write_row(dut, 0, 1)
    await write_row(dut, 0, 2)

    # Start a distinct frame without clearing RAM.
    await write_row(dut, 1, 0)
    await write_row(dut, 1, 1)
    await write_row(dut, 1, 2)
