import os

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


IMG_WIDTH = int(os.environ["IMG_WIDTH"])
IMG_HEIGHT = int(os.environ["IMG_HEIGHT"])

FRAME_PIXELS = IMG_WIDTH * IMG_HEIGHT
LIVE_START_INDEX = IMG_WIDTH + 1
LIVE_OUTPUT_COUNT = FRAME_PIXELS - (IMG_WIDTH + 1)
DRAIN_OUTPUT_COUNT = IMG_WIDTH + 1


def output_coord(index: int):
    return divmod(index, IMG_WIDTH)


def is_border(row: int, col: int) -> bool:
    return (
        row == 0
        or row == IMG_HEIGHT - 1
        or col == 0
        or col == IMG_WIDTH - 1
    )


async def settle():
    await Timer(1, unit="ns")


async def assert_invalid_output(dut):
    assert int(dut.output_valid_o.value) == 0
    assert int(dut.output_row_o.value) == 0
    assert int(dut.output_col_o.value) == 0
    assert int(dut.output_border_o.value) == 0
    assert int(dut.frame_done_o.value) == 0


async def start_and_reset(dut):
    cocotb.start_soon(
        Clock(dut.clk, 10, unit="ns").start()
    )

    dut.rst.value = 1

    dut.pixel_commit_i.value = 0
    dut.frame_start_i.value = 0
    dut.last_input_accept_i.value = 0
    dut.frame_abort_i.value = 0

    dut.output_ready_i.value = 0

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    await settle()

    dut.rst.value = 0
    await settle()

    assert int(dut.waiting_for_sof_o.value) == 1
    assert int(dut.processing_o.value) == 0
    assert int(dut.draining_o.value) == 0

    assert int(dut.input_allow_o.value) == 1

    await assert_invalid_output(dut)


async def commit_input(
    dut,
    input_index: int,
    *,
    ready: int = 1,
):
    dut.output_ready_i.value = ready

    dut.pixel_commit_i.value = 1
    dut.frame_start_i.value = int(input_index == 0)
    dut.last_input_accept_i.value = int(
        input_index == FRAME_PIXELS - 1
    )

    await settle()

    expected_live = (
        input_index >= LIVE_START_INDEX
    )

    assert int(dut.input_allow_o.value) == 1

    if expected_live:
        output_index = (
            input_index - LIVE_START_INDEX
        )

        row, col = output_coord(output_index)

        assert int(dut.output_valid_o.value) == 1
        assert int(dut.output_row_o.value) == row
        assert int(dut.output_col_o.value) == col
        assert int(dut.output_border_o.value) == int(
            is_border(row, col)
        )
    else:
        await assert_invalid_output(dut)

    assert int(dut.frame_done_o.value) == 0

    await RisingEdge(dut.clk)

    dut.pixel_commit_i.value = 0
    dut.frame_start_i.value = 0
    dut.last_input_accept_i.value = 0

    await settle()

    if input_index == FRAME_PIXELS - 1:
        assert int(dut.processing_o.value) == 0
        assert int(dut.draining_o.value) == 1

        assert int(dut.input_allow_o.value) == 0

        assert int(dut.output_valid_o.value) == 1
    else:
        assert int(dut.processing_o.value) == 1
        assert int(dut.draining_o.value) == 0

        await assert_invalid_output(dut)

    return expected_live


async def drain_position(
    dut,
    output_index: int,
    *,
    ready: int,
):
    row, col = output_coord(output_index)

    dut.pixel_commit_i.value = 0
    dut.frame_start_i.value = 0
    dut.last_input_accept_i.value = 0

    dut.output_ready_i.value = ready

    await settle()

    assert int(dut.draining_o.value) == 1
    assert int(dut.processing_o.value) == 0

    assert int(dut.input_allow_o.value) == 0

    assert int(dut.output_valid_o.value) == 1
    assert int(dut.output_row_o.value) == row
    assert int(dut.output_col_o.value) == col

    assert int(dut.output_border_o.value) == int(
        is_border(row, col)
    )

    # By the frozen alignment, every drain position is a border.
    assert is_border(row, col)

    final_position = (
        output_index == FRAME_PIXELS - 1
    )

    assert int(dut.frame_done_o.value) == int(
        ready and final_position
    )

    await RisingEdge(dut.clk)
    await settle()

    if not ready:
        assert int(dut.draining_o.value) == 1

        assert int(dut.output_valid_o.value) == 1
        assert int(dut.output_row_o.value) == row
        assert int(dut.output_col_o.value) == col
        assert int(dut.output_border_o.value) == 1
    elif final_position:
        assert int(dut.waiting_for_sof_o.value) == 1
        assert int(dut.processing_o.value) == 0
        assert int(dut.draining_o.value) == 0

        assert int(dut.input_allow_o.value) == 1

        await assert_invalid_output(dut)

    return bool(ready)


async def enter_drain(dut):
    live_count = 0

    for input_index in range(FRAME_PIXELS):
        if await commit_input(
            dut,
            input_index,
            ready=1,
        ):
            live_count += 1

    assert live_count == LIVE_OUTPUT_COUNT

    first_drain_index = LIVE_OUTPUT_COUNT

    row, col = output_coord(first_drain_index)

    assert int(dut.output_valid_o.value) == 1
    assert int(dut.output_row_o.value) == row
    assert int(dut.output_col_o.value) == col

    return live_count


@cocotb.test()
async def exact_initial_delay_and_first_output(dut):
    await start_and_reset(dut)

    # No output exists for input indices 0 through IMG_WIDTH.
    # Downstream readiness must not block this initial fill.
    for input_index in range(IMG_WIDTH + 1):
        await commit_input(
            dut,
            input_index,
            ready=0,
        )

    # The next committed input would create logical output position 0.
    # With downstream blocked it must therefore be backpressured.
    dut.pixel_commit_i.value = 0
    dut.frame_start_i.value = 0
    dut.last_input_accept_i.value = 0
    dut.output_ready_i.value = 0

    await settle()

    assert int(dut.input_allow_o.value) == 0
    await assert_invalid_output(dut)

    # Once downstream admits a token, input index IMG_WIDTH+1 may commit
    # and must produce output index zero.
    await commit_input(
        dut,
        IMG_WIDTH + 1,
        ready=1,
    )


@cocotb.test()
async def full_frame_mapping_count_and_border_classification(dut):
    await start_and_reset(dut)

    live_positions = []

    for input_index in range(FRAME_PIXELS):
        expected_live = (
            input_index >= LIVE_START_INDEX
        )

        dut.output_ready_i.value = 1
        dut.pixel_commit_i.value = 1
        dut.frame_start_i.value = int(
            input_index == 0
        )
        dut.last_input_accept_i.value = int(
            input_index == FRAME_PIXELS - 1
        )

        await settle()

        assert int(dut.input_allow_o.value) == 1

        if expected_live:
            output_index = (
                input_index - LIVE_START_INDEX
            )

            row, col = output_coord(output_index)

            assert int(dut.output_valid_o.value) == 1
            assert int(dut.output_row_o.value) == row
            assert int(dut.output_col_o.value) == col
            assert int(dut.output_border_o.value) == int(
                is_border(row, col)
            )

            live_positions.append(
                (output_index, row, col)
            )
        else:
            await assert_invalid_output(dut)

        await RisingEdge(dut.clk)

        dut.pixel_commit_i.value = 0
        dut.frame_start_i.value = 0
        dut.last_input_accept_i.value = 0

        await settle()

    assert len(live_positions) == LIVE_OUTPUT_COUNT

    drain_positions = []

    for output_index in range(
        LIVE_OUTPUT_COUNT,
        FRAME_PIXELS,
    ):
        row, col = output_coord(output_index)

        dut.output_ready_i.value = 1
        await settle()

        assert int(dut.output_valid_o.value) == 1
        assert int(dut.output_row_o.value) == row
        assert int(dut.output_col_o.value) == col
        assert int(dut.output_border_o.value) == int(
            is_border(row, col)
        )

        assert is_border(row, col)

        drain_positions.append(
            (output_index, row, col)
        )

        expected_done = (
            output_index == FRAME_PIXELS - 1
        )

        assert int(dut.frame_done_o.value) == int(
            expected_done
        )

        await RisingEdge(dut.clk)
        await settle()

    assert len(drain_positions) == DRAIN_OUTPUT_COUNT

    all_positions = (
        live_positions + drain_positions
    )

    assert len(all_positions) == FRAME_PIXELS

    assert [
        index
        for index, _, _ in all_positions
    ] == list(range(FRAME_PIXELS))

    border_count = sum(
        int(is_border(row, col))
        for _, row, col in all_positions
    )

    expected_border_count = (
        2 * IMG_WIDTH
        + 2 * (IMG_HEIGHT - 2)
    )

    assert border_count == expected_border_count

    assert int(dut.waiting_for_sof_o.value) == 1


@cocotb.test()
async def live_backpressure_blocks_input_after_fill(dut):
    await start_and_reset(dut)

    for input_index in range(IMG_WIDTH + 1):
        await commit_input(
            dut,
            input_index,
            ready=0,
        )

    # We are now exactly at the point where the next input would create
    # the first output position.
    for _ in range(4):
        dut.pixel_commit_i.value = 0
        dut.frame_start_i.value = 0
        dut.last_input_accept_i.value = 0
        dut.output_ready_i.value = 0

        await settle()

        assert int(dut.input_allow_o.value) == 0

        await assert_invalid_output(dut)

        await RisingEdge(dut.clk)
        await settle()

    dut.output_ready_i.value = 1
    await settle()

    assert int(dut.input_allow_o.value) == 1

    await commit_input(
        dut,
        IMG_WIDTH + 1,
        ready=1,
    )

    await commit_input(
        dut,
        IMG_WIDTH + 2,
        ready=1,
    )


@cocotb.test()
async def drain_is_exactly_w_plus_one_and_stalls_stably(dut):
    await start_and_reset(dut)

    live_count = await enter_drain(dut)

    assert live_count == LIVE_OUTPUT_COUNT

    first_drain_index = LIVE_OUTPUT_COUNT

    # Stall the first drain token for multiple clocks.
    row, col = output_coord(first_drain_index)

    for _ in range(4):
        await drain_position(
            dut,
            first_drain_index,
            ready=0,
        )

        assert int(dut.output_row_o.value) == row
        assert int(dut.output_col_o.value) == col

    drain_transfers = 0

    for output_index in range(
        first_drain_index,
        FRAME_PIXELS,
    ):
        # Add additional deterministic stalls.
        if output_index != FRAME_PIXELS - 1:
            await drain_position(
                dut,
                output_index,
                ready=0,
            )

        transferred = await drain_position(
            dut,
            output_index,
            ready=1,
        )

        drain_transfers += int(transferred)

    assert drain_transfers == IMG_WIDTH + 1

    assert int(dut.waiting_for_sof_o.value) == 1
    assert int(dut.input_allow_o.value) == 1


@cocotb.test()
async def no_new_frame_is_admitted_during_drain(dut):
    await start_and_reset(dut)

    await enter_drain(dut)

    # Present start-of-frame-like control while draining, but do not
    # violate the integration contract by asserting pixel_commit_i when
    # input_allow_o is low.
    dut.frame_start_i.value = 1
    dut.last_input_accept_i.value = 0
    dut.pixel_commit_i.value = 0
    dut.output_ready_i.value = 0

    for _ in range(3):
        await settle()

        assert int(dut.draining_o.value) == 1
        assert int(dut.input_allow_o.value) == 0

        await RisingEdge(dut.clk)

    dut.frame_start_i.value = 0

    for output_index in range(
        LIVE_OUTPUT_COUNT,
        FRAME_PIXELS,
    ):
        await drain_position(
            dut,
            output_index,
            ready=1,
        )

    assert int(dut.waiting_for_sof_o.value) == 1
    assert int(dut.input_allow_o.value) == 1

    # The first pixel of a new frame can now be committed.
    await commit_input(
        dut,
        0,
        ready=0,
    )

    assert int(dut.processing_o.value) == 1


@cocotb.test()
async def frame_abort_clears_partial_position_state(dut):
    await start_and_reset(dut)

    # Advance far enough to create at least one logical output.
    for input_index in range(IMG_WIDTH + 2):
        await commit_input(
            dut,
            input_index,
            ready=1,
        )

    assert int(dut.processing_o.value) == 1

    dut.pixel_commit_i.value = 0
    dut.frame_start_i.value = 0
    dut.last_input_accept_i.value = 0

    dut.frame_abort_i.value = 1
    dut.output_ready_i.value = 1

    await settle()

    assert int(dut.input_allow_o.value) == 0
    await assert_invalid_output(dut)

    await RisingEdge(dut.clk)

    dut.frame_abort_i.value = 0

    await settle()

    assert int(dut.waiting_for_sof_o.value) == 1
    assert int(dut.processing_o.value) == 0
    assert int(dut.draining_o.value) == 0
    assert int(dut.input_allow_o.value) == 1

    # Start another frame. Its first output must again be position zero
    # after exactly the frozen initial delay.
    for input_index in range(IMG_WIDTH + 1):
        await commit_input(
            dut,
            input_index,
            ready=0,
        )

    await commit_input(
        dut,
        IMG_WIDTH + 1,
        ready=1,
    )


@cocotb.test()
async def synchronous_reset_clears_drain_state(dut):
    await start_and_reset(dut)

    await enter_drain(dut)

    assert int(dut.draining_o.value) == 1
    assert int(dut.input_allow_o.value) == 0

    dut.output_ready_i.value = 0

    dut.rst.value = 1

    await settle()

    assert int(dut.output_valid_o.value) == 0
    assert int(dut.input_allow_o.value) == 0

    await RisingEdge(dut.clk)
    await settle()

    dut.rst.value = 0
    await settle()

    assert int(dut.waiting_for_sof_o.value) == 1
    assert int(dut.processing_o.value) == 0
    assert int(dut.draining_o.value) == 0

    assert int(dut.input_allow_o.value) == 1

    await assert_invalid_output(dut)
