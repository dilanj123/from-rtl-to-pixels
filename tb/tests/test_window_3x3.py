import os

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


IMG_WIDTH = int(os.environ["IMG_WIDTH"])
IMG_HEIGHT = int(os.environ["IMG_HEIGHT"])


def label(frame: int, row: int, col: int) -> int:
    return (101 * frame + 16 * row + col + 1) & 0xFF


async def settle():
    await Timer(1, unit="ns")


def tap_values(dut):
    return (
        int(dut.p00_o.value),
        int(dut.p01_o.value),
        int(dut.p02_o.value),
        int(dut.p10_o.value),
        int(dut.p11_o.value),
        int(dut.p12_o.value),
        int(dut.p20_o.value),
        int(dut.p21_o.value),
        int(dut.p22_o.value),
    )


def expected_taps(frame: int, row: int, col: int):
    return (
        label(frame, row - 2, col - 2),
        label(frame, row - 2, col - 1),
        label(frame, row - 2, col),
        label(frame, row - 1, col - 2),
        label(frame, row - 1, col - 1),
        label(frame, row - 1, col),
        label(frame, row, col - 2),
        label(frame, row, col - 1),
        label(frame, row, col),
    )


async def assert_invalid(dut):
    assert int(dut.window_valid_o.value) == 0
    assert int(dut.window_row_o.value) == 0
    assert int(dut.window_col_o.value) == 0
    assert tap_values(dut) == (0,) * 9


async def start_and_reset(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst.value = 1

    dut.pixel_commit_i.value = 0
    dut.frame_start_i.value = 0

    dut.row_i.value = 0
    dut.col_i.value = 0

    dut.pixel_i.value = 0

    dut.prev_row1_i.value = 0
    dut.prev_row1_valid_i.value = 0

    dut.prev_row2_i.value = 0
    dut.prev_row2_valid_i.value = 0

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    await settle()

    dut.rst.value = 0
    await settle()

    await assert_invalid(dut)


async def drive_commit(dut, frame: int, row: int, col: int):
    dut.pixel_commit_i.value = 1
    dut.frame_start_i.value = int(row == 0 and col == 0)

    dut.row_i.value = row
    dut.col_i.value = col

    dut.pixel_i.value = label(frame, row, col)

    if row >= 1:
        dut.prev_row1_i.value = label(frame, row - 1, col)
        dut.prev_row1_valid_i.value = 1
    else:
        dut.prev_row1_i.value = 0
        dut.prev_row1_valid_i.value = 0

    if row >= 2:
        dut.prev_row2_i.value = label(frame, row - 2, col)
        dut.prev_row2_valid_i.value = 1
    else:
        dut.prev_row2_i.value = 0
        dut.prev_row2_valid_i.value = 0

    # The window is a pre-write view for this committed input pixel.
    await settle()

    expected_valid = row >= 2 and col >= 2

    if expected_valid:
        assert int(dut.window_valid_o.value) == 1
        assert int(dut.window_row_o.value) == row - 1
        assert int(dut.window_col_o.value) == col - 1

        actual = tap_values(dut)
        expected = expected_taps(frame, row, col)

        assert actual == expected, (
            f"input=({row},{col}) "
            f"center=({row - 1},{col - 1}) "
            f"expected={expected} actual={actual}"
        )
    else:
        await assert_invalid(dut)

    await RisingEdge(dut.clk)

    dut.pixel_commit_i.value = 0
    dut.frame_start_i.value = 0

    await settle()
    await assert_invalid(dut)

    return expected_valid


async def drive_frame(dut, frame: int):
    count = 0

    for row in range(IMG_HEIGHT):
        for col in range(IMG_WIDTH):
            if await drive_commit(dut, frame, row, col):
                count += 1

    return count


async def drive_non_commit_noise(dut, cycle: int):
    dut.pixel_commit_i.value = 0

    # Deliberately toggle all other inputs. With no commit, none of this
    # may affect horizontal history.
    dut.frame_start_i.value = cycle & 1

    dut.row_i.value = (cycle + 1) % IMG_HEIGHT
    dut.col_i.value = (cycle * 3 + 1) % IMG_WIDTH

    dut.pixel_i.value = (0xA0 + cycle) & 0xFF

    dut.prev_row1_i.value = (0x50 + cycle) & 0xFF
    dut.prev_row1_valid_i.value = cycle & 1

    dut.prev_row2_i.value = (0xD0 + cycle) & 0xFF
    dut.prev_row2_valid_i.value = (cycle + 1) & 1

    await settle()
    await assert_invalid(dut)

    await RisingEdge(dut.clk)
    await settle()

    await assert_invalid(dut)


@cocotb.test()
async def first_valid_window_has_exact_taps(dut):
    await start_and_reset(dut)

    valid_count = 0

    for row in range(3):
        last_col = IMG_WIDTH if row < 2 else 3

        for col in range(last_col):
            valid = await drive_commit(
                dut,
                frame=0,
                row=row,
                col=col,
            )

            if valid:
                valid_count += 1

                assert row == 2
                assert col == 2
                assert int(dut.window_valid_o.value) == 0

    assert valid_count == 1


@cocotb.test()
async def every_interior_window_has_exact_taps(dut):
    await start_and_reset(dut)

    actual_count = await drive_frame(dut, frame=0)
    expected_count = (IMG_WIDTH - 2) * (IMG_HEIGHT - 2)

    assert actual_count == expected_count


@cocotb.test()
async def row_transition_clears_horizontal_history(dut):
    await start_and_reset(dut)

    # Fill the first two rows completely. Their final columns must not
    # contaminate the beginning of row two.
    for row in range(2):
        for col in range(IMG_WIDTH):
            await drive_commit(dut, 0, row, col)

    await drive_commit(dut, 0, 2, 0)
    await drive_commit(dut, 0, 2, 1)

    # First valid window of the new row must use columns 0,1,2,
    # not tail columns from the preceding row.
    valid = await drive_commit(dut, 0, 2, 2)

    assert valid


@cocotb.test()
async def non_commit_cycles_hold_horizontal_history(dut):
    await start_and_reset(dut)

    for row in range(2):
        for col in range(IMG_WIDTH):
            await drive_commit(dut, 0, row, col)

    await drive_commit(dut, 0, 2, 0)

    for cycle in range(4):
        await drive_non_commit_noise(dut, cycle)

    await drive_commit(dut, 0, 2, 1)

    for cycle in range(4, 8):
        await drive_non_commit_noise(dut, cycle)

    valid = await drive_commit(dut, 0, 2, 2)

    assert valid


@cocotb.test()
async def reset_invalidates_horizontal_history(dut):
    await start_and_reset(dut)

    for row in range(2):
        for col in range(IMG_WIDTH):
            await drive_commit(dut, 0, row, col)

    await drive_commit(dut, 0, 2, 0)
    await drive_commit(dut, 0, 2, 1)

    dut.pixel_commit_i.value = 0
    dut.frame_start_i.value = 0
    dut.rst.value = 1

    await settle()
    await assert_invalid(dut)

    await RisingEdge(dut.clk)
    await settle()

    dut.rst.value = 0
    await settle()

    await assert_invalid(dut)

    # Distinct frame labels make stale horizontal data obvious.
    for row in range(3):
        last_col = IMG_WIDTH if row < 2 else 3

        for col in range(last_col):
            await drive_commit(dut, 1, row, col)


@cocotb.test()
async def new_frame_start_invalidates_old_horizontal_history(dut):
    await start_and_reset(dut)

    count0 = await drive_frame(dut, frame=0)

    assert count0 == (IMG_WIDTH - 2) * (IMG_HEIGHT - 2)

    # No reset between frames. The frame-start/column-zero update must
    # ensure no old-frame horizontal history can enter frame one.
    count1 = await drive_frame(dut, frame=1)

    assert count1 == (IMG_WIDTH - 2) * (IMG_HEIGHT - 2)


@cocotb.test()
async def rows_zero_one_and_cols_zero_one_never_valid(dut):
    await start_and_reset(dut)

    for row in range(IMG_HEIGHT):
        for col in range(IMG_WIDTH):
            valid = await drive_commit(dut, 0, row, col)

            if row < 2 or col < 2:
                assert not valid
            else:
                assert valid
