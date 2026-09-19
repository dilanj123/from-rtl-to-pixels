import os

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


IMG_WIDTH = int(os.environ["IMG_WIDTH"])
IMG_HEIGHT = int(os.environ["IMG_HEIGHT"])


async def settle():
    await Timer(1, unit="ns")


async def start_and_reset(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst.value = 1
    dut.accept_i.value = 0
    dut.s_tuser_i.value = 0
    dut.s_tlast_i.value = 0

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    await settle()

    dut.rst.value = 0
    await settle()

    assert int(dut.waiting_for_sof_o.value) == 1
    assert int(dut.row_o.value) == 0
    assert int(dut.col_o.value) == 0
    assert int(dut.pixel_commit_o.value) == 0
    assert int(dut.sof_accept_o.value) == 0
    assert int(dut.last_input_accept_o.value) == 0
    assert int(dut.metadata_error_o.value) == 0


async def accept_checked(
    dut,
    *,
    sof,
    eol,
    row,
    col,
    commit,
    sof_event=False,
    last_event=False,
    error=False,
):
    dut.accept_i.value = 1
    dut.s_tuser_i.value = int(sof)
    dut.s_tlast_i.value = int(eol)

    await settle()

    assert int(dut.row_o.value) == row
    assert int(dut.col_o.value) == col

    assert int(dut.pixel_commit_o.value) == int(commit)
    assert int(dut.sof_accept_o.value) == int(sof_event)
    assert int(dut.last_input_accept_o.value) == int(last_event)
    assert int(dut.metadata_error_o.value) == int(error)

    await RisingEdge(dut.clk)

    dut.accept_i.value = 0
    dut.s_tuser_i.value = 0
    dut.s_tlast_i.value = 0

    await settle()


async def send_valid_pixel(dut, row, col):
    await accept_checked(
        dut,
        sof=(row == 0 and col == 0),
        eol=(col == IMG_WIDTH - 1),
        row=row,
        col=col,
        commit=True,
        sof_event=(row == 0 and col == 0),
        last_event=(
            row == IMG_HEIGHT - 1
            and col == IMG_WIDTH - 1
        ),
        error=False,
    )


async def send_valid_frame(dut):
    for row in range(IMG_HEIGHT):
        for col in range(IMG_WIDTH):
            await send_valid_pixel(dut, row, col)


@cocotb.test()
async def correct_frame_tracks_coordinates(dut):
    await start_and_reset(dut)

    await send_valid_frame(dut)

    assert int(dut.waiting_for_sof_o.value) == 1
    assert int(dut.row_o.value) == 0
    assert int(dut.col_o.value) == 0


@cocotb.test()
async def non_accept_cycles_hold_position(dut):
    await start_and_reset(dut)

    await send_valid_pixel(dut, 0, 0)

    assert int(dut.waiting_for_sof_o.value) == 0
    assert int(dut.row_o.value) == 0
    assert int(dut.col_o.value) == 1

    for cycle in range(6):
        dut.accept_i.value = 0
        dut.s_tuser_i.value = cycle & 1
        dut.s_tlast_i.value = (cycle >> 1) & 1

        await settle()

        assert int(dut.row_o.value) == 0
        assert int(dut.col_o.value) == 1
        assert int(dut.pixel_commit_o.value) == 0
        assert int(dut.sof_accept_o.value) == 0
        assert int(dut.last_input_accept_o.value) == 0
        assert int(dut.metadata_error_o.value) == 0

        await RisingEdge(dut.clk)
        await settle()

        assert int(dut.row_o.value) == 0
        assert int(dut.col_o.value) == 1

    await send_valid_pixel(dut, 0, 1)


@cocotb.test()
async def missing_and_unexpected_sof_abort(dut):
    await start_and_reset(dut)

    await accept_checked(
        dut,
        sof=False,
        eol=False,
        row=0,
        col=0,
        commit=False,
        error=True,
    )

    assert int(dut.waiting_for_sof_o.value) == 1
    assert int(dut.row_o.value) == 0
    assert int(dut.col_o.value) == 0

    await send_valid_pixel(dut, 0, 0)

    await accept_checked(
        dut,
        sof=True,
        eol=False,
        row=0,
        col=1,
        commit=False,
        error=True,
    )

    assert int(dut.waiting_for_sof_o.value) == 1
    assert int(dut.row_o.value) == 0
    assert int(dut.col_o.value) == 0


@cocotb.test()
async def premature_and_missing_eol_abort(dut):
    await start_and_reset(dut)

    await send_valid_pixel(dut, 0, 0)

    await accept_checked(
        dut,
        sof=False,
        eol=True,
        row=0,
        col=1,
        commit=False,
        error=True,
    )

    assert int(dut.waiting_for_sof_o.value) == 1

    await send_valid_pixel(dut, 0, 0)

    for col in range(1, IMG_WIDTH - 1):
        await send_valid_pixel(dut, 0, col)

    await accept_checked(
        dut,
        sof=False,
        eol=False,
        row=0,
        col=IMG_WIDTH - 1,
        commit=False,
        error=True,
    )

    assert int(dut.waiting_for_sof_o.value) == 1
    assert int(dut.row_o.value) == 0
    assert int(dut.col_o.value) == 0


@cocotb.test()
async def recovery_requires_new_valid_sof(dut):
    await start_and_reset(dut)

    await send_valid_pixel(dut, 0, 0)

    await accept_checked(
        dut,
        sof=False,
        eol=True,
        row=0,
        col=1,
        commit=False,
        error=True,
    )

    assert int(dut.waiting_for_sof_o.value) == 1

    await accept_checked(
        dut,
        sof=False,
        eol=False,
        row=0,
        col=0,
        commit=False,
        error=True,
    )

    assert int(dut.waiting_for_sof_o.value) == 1

    await send_valid_frame(dut)

    assert int(dut.waiting_for_sof_o.value) == 1


@cocotb.test()
async def synchronous_reset_aborts_partial_frame(dut):
    await start_and_reset(dut)

    await send_valid_pixel(dut, 0, 0)
    await send_valid_pixel(dut, 0, 1)

    assert int(dut.waiting_for_sof_o.value) == 0

    dut.rst.value = 1
    dut.accept_i.value = 0
    dut.s_tuser_i.value = 1
    dut.s_tlast_i.value = 1

    await settle()

    assert int(dut.pixel_commit_o.value) == 0
    assert int(dut.sof_accept_o.value) == 0
    assert int(dut.last_input_accept_o.value) == 0
    assert int(dut.metadata_error_o.value) == 0

    await RisingEdge(dut.clk)
    await settle()

    assert int(dut.waiting_for_sof_o.value) == 1
    assert int(dut.row_o.value) == 0
    assert int(dut.col_o.value) == 0

    dut.rst.value = 0
    dut.s_tuser_i.value = 0
    dut.s_tlast_i.value = 0

    await settle()

    await send_valid_pixel(dut, 0, 0)


@cocotb.test()
async def exact_last_pixel_event_and_return_to_wait_sof(dut):
    await start_and_reset(dut)

    coordinates = [
        (row, col)
        for row in range(IMG_HEIGHT)
        for col in range(IMG_WIDTH)
    ]

    for row, col in coordinates[:-1]:
        await send_valid_pixel(dut, row, col)

    last_row = IMG_HEIGHT - 1
    last_col = IMG_WIDTH - 1

    assert int(dut.waiting_for_sof_o.value) == 0
    assert int(dut.row_o.value) == last_row
    assert int(dut.col_o.value) == last_col

    await send_valid_pixel(dut, last_row, last_col)

    assert int(dut.waiting_for_sof_o.value) == 1
    assert int(dut.row_o.value) == 0
    assert int(dut.col_o.value) == 0
