import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


async def settle():
    await Timer(1, unit="ns")


async def start_and_reset(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst.value = 1
    dut.s_valid.value = 0
    dut.s_data.value = 0
    dut.m_ready.value = 0

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    await settle()

    dut.rst.value = 0
    await settle()

    assert int(dut.m_valid.value) == 0
    assert int(dut.s_ready.value) == 1


@cocotb.test()
async def pass_through_no_stall(dut):
    await start_and_reset(dut)

    dut.m_ready.value = 1
    dut.s_valid.value = 1
    dut.s_data.value = 0x5A
    await settle()

    assert int(dut.s_ready.value) == 1
    assert int(dut.m_valid.value) == 0

    await RisingEdge(dut.clk)
    await settle()

    assert int(dut.m_valid.value) == 1
    assert int(dut.m_data.value) == 0x5A

    dut.s_valid.value = 0

    await RisingEdge(dut.clk)
    await settle()

    assert int(dut.m_valid.value) == 0


@cocotb.test()
async def backpressure_holds_output_stable(dut):
    await start_and_reset(dut)

    dut.m_ready.value = 0
    dut.s_valid.value = 1
    dut.s_data.value = 0x12

    await RisingEdge(dut.clk)
    await settle()

    assert int(dut.m_valid.value) == 1
    assert int(dut.m_data.value) == 0x12

    dut.s_data.value = 0x34

    for _ in range(3):
        await settle()

        assert int(dut.s_ready.value) == 0
        assert int(dut.m_valid.value) == 1
        assert int(dut.m_data.value) == 0x12

        await RisingEdge(dut.clk)

    dut.m_ready.value = 1
    await settle()

    assert int(dut.s_ready.value) == 1

    await RisingEdge(dut.clk)
    await settle()

    assert int(dut.m_valid.value) == 1
    assert int(dut.m_data.value) == 0x34


@cocotb.test()
async def source_gaps_leave_stage_empty(dut):
    await start_and_reset(dut)

    dut.m_ready.value = 1
    dut.s_valid.value = 1
    dut.s_data.value = 0x21

    await RisingEdge(dut.clk)
    await settle()

    assert int(dut.m_valid.value) == 1
    assert int(dut.m_data.value) == 0x21

    dut.s_valid.value = 0

    await RisingEdge(dut.clk)
    await settle()

    assert int(dut.m_valid.value) == 0

    for _ in range(2):
        await RisingEdge(dut.clk)
        await settle()
        assert int(dut.m_valid.value) == 0

    dut.s_valid.value = 1
    dut.s_data.value = 0x43

    await RisingEdge(dut.clk)
    await settle()

    assert int(dut.m_valid.value) == 1
    assert int(dut.m_data.value) == 0x43


@cocotb.test()
async def replacement_on_consume(dut):
    await start_and_reset(dut)

    dut.m_ready.value = 0
    dut.s_valid.value = 1
    dut.s_data.value = 0xA1

    await RisingEdge(dut.clk)
    await settle()

    assert int(dut.m_valid.value) == 1
    assert int(dut.m_data.value) == 0xA1

    dut.m_ready.value = 1
    dut.s_valid.value = 1
    dut.s_data.value = 0xB2
    await settle()

    assert int(dut.s_ready.value) == 1

    await RisingEdge(dut.clk)
    await settle()

    assert int(dut.m_valid.value) == 1
    assert int(dut.m_data.value) == 0xB2


@cocotb.test()
async def synchronous_reset_discards_stored_token(dut):
    await start_and_reset(dut)

    dut.m_ready.value = 0
    dut.s_valid.value = 1
    dut.s_data.value = 0x77

    await RisingEdge(dut.clk)
    await settle()

    assert int(dut.m_valid.value) == 1

    dut.s_valid.value = 0
    dut.rst.value = 1

    await RisingEdge(dut.clk)
    await settle()

    assert int(dut.m_valid.value) == 0
    assert int(dut.s_ready.value) == 1

    dut.rst.value = 0
    dut.s_valid.value = 1
    dut.s_data.value = 0x88

    await RisingEdge(dut.clk)
    await settle()

    assert int(dut.m_valid.value) == 1
    assert int(dut.m_data.value) == 0x88


@cocotb.test()
async def randomized_no_loss_or_duplication(dut):
    await start_and_reset(dut)

    rng = random.Random(0xE1A57C)

    pending = None
    next_value = 0

    model_queue = []
    accepted = []
    observed = []

    for _ in range(200):
        if pending is None and rng.random() < 0.65:
            pending = next_value & 0xFF
            next_value += 1

        dut.s_valid.value = int(pending is not None)
        dut.s_data.value = 0 if pending is None else pending
        dut.m_ready.value = int(rng.random() < 0.60)

        await settle()

        input_fire = (
            int(dut.s_valid.value)
            and int(dut.s_ready.value)
        )
        output_fire = (
            int(dut.m_valid.value)
            and int(dut.m_ready.value)
        )

        if output_fire:
            assert model_queue
            expected = model_queue.pop(0)
            actual = int(dut.m_data.value)

            assert actual == expected
            observed.append(actual)

        if input_fire:
            assert pending is not None
            model_queue.append(pending)
            accepted.append(pending)
            pending = None

        await RisingEdge(dut.clk)

    for _ in range(20):
        dut.s_valid.value = int(pending is not None)
        dut.s_data.value = 0 if pending is None else pending
        dut.m_ready.value = 1

        await settle()

        input_fire = (
            int(dut.s_valid.value)
            and int(dut.s_ready.value)
        )
        output_fire = (
            int(dut.m_valid.value)
            and int(dut.m_ready.value)
        )

        if output_fire:
            assert model_queue
            expected = model_queue.pop(0)
            actual = int(dut.m_data.value)

            assert actual == expected
            observed.append(actual)

        if input_fire:
            assert pending is not None
            model_queue.append(pending)
            accepted.append(pending)
            pending = None

        await RisingEdge(dut.clk)

        if pending is None and not model_queue:
            await settle()
            if int(dut.m_valid.value) == 0:
                break

    await settle()

    assert pending is None
    assert model_queue == []
    assert accepted == observed
    assert int(dut.m_valid.value) == 0
