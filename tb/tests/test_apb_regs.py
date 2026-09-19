import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


CONTROL = 0x00
THRESHOLD = 0x04
STATUS = 0x08
FRAME_COUNT = 0x0C


async def settle():
    await Timer(1, unit="ns")


def get_bit(value: int, bit: int) -> int:
    return (value >> bit) & 1


async def start_and_reset(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst.value = 1

    dut.psel.value = 0
    dut.penable.value = 0
    dut.pwrite.value = 0
    dut.paddr.value = 0
    dut.pwdata.value = 0

    dut.processing_i.value = 0
    dut.draining_i.value = 0
    dut.sof_accept_i.value = 0
    dut.frame_error_set_i.value = 0
    dut.frame_done_i.value = 0

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    await settle()

    dut.rst.value = 0
    await settle()


async def apb_read(dut, addr: int, expect_error: bool = False) -> int:
    dut.psel.value = 1
    dut.penable.value = 0
    dut.pwrite.value = 0
    dut.paddr.value = addr
    dut.pwdata.value = 0

    await RisingEdge(dut.clk)

    dut.penable.value = 1
    await settle()

    assert int(dut.pready.value) == 1
    assert int(dut.pslverr.value) == int(expect_error)

    data = int(dut.prdata.value)

    await RisingEdge(dut.clk)
    await settle()

    dut.psel.value = 0
    dut.penable.value = 0
    dut.paddr.value = 0

    await settle()

    return data


async def apb_write(
    dut,
    addr: int,
    data: int,
    expect_error: bool = False,
    sof_accept: bool = False,
    frame_error_set: bool = False,
):
    dut.psel.value = 1
    dut.penable.value = 0
    dut.pwrite.value = 1
    dut.paddr.value = addr
    dut.pwdata.value = data

    await RisingEdge(dut.clk)

    dut.penable.value = 1
    dut.sof_accept_i.value = int(sof_accept)
    dut.frame_error_set_i.value = int(frame_error_set)

    await settle()

    assert int(dut.pready.value) == 1
    assert int(dut.pslverr.value) == int(expect_error)

    await RisingEdge(dut.clk)
    await settle()

    dut.psel.value = 0
    dut.penable.value = 0
    dut.pwrite.value = 0
    dut.paddr.value = 0
    dut.pwdata.value = 0
    dut.sof_accept_i.value = 0
    dut.frame_error_set_i.value = 0

    await settle()


async def pulse(dut, signal_name: str):
    signal = getattr(dut, signal_name)

    signal.value = 1
    await RisingEdge(dut.clk)
    await settle()

    signal.value = 0
    await settle()


@cocotb.test()
async def reset_defaults_and_valid_reads(dut):
    await start_and_reset(dut)

    assert int(dut.pready.value) == 1
    assert int(dut.pslverr.value) == 0

    assert int(dut.run_enable_o.value) == 0
    assert int(dut.threshold_active_o.value) == 128
    assert int(dut.bypass_threshold_active_o.value) == 0

    control = await apb_read(dut, CONTROL)
    threshold = await apb_read(dut, THRESHOLD)
    status = await apb_read(dut, STATUS)
    frame_count = await apb_read(dut, FRAME_COUNT)

    assert control == 0
    assert threshold == 128
    assert status == 0
    assert frame_count == 0


@cocotb.test()
async def valid_writes_shadow_then_sof_updates_active(dut):
    await start_and_reset(dut)

    await apb_write(dut, CONTROL, 0x0000_0003)
    await apb_write(dut, THRESHOLD, 0x0000_002A)

    assert int(dut.run_enable_o.value) == 1

    control = await apb_read(dut, CONTROL)
    threshold = await apb_read(dut, THRESHOLD)
    status = await apb_read(dut, STATUS)

    assert (control & 0x3) == 0x3
    assert threshold == 0x2A

    assert int(dut.threshold_active_o.value) == 128
    assert int(dut.bypass_threshold_active_o.value) == 0
    assert get_bit(status, 2) == 1

    await pulse(dut, "sof_accept_i")

    assert int(dut.threshold_active_o.value) == 0x2A
    assert int(dut.bypass_threshold_active_o.value) == 1

    status = await apb_read(dut, STATUS)
    assert get_bit(status, 2) == 0


@cocotb.test()
async def simultaneous_config_write_and_sof_uses_preedge_shadow(dut):
    await start_and_reset(dut)

    await apb_write(dut, THRESHOLD, 0x22)
    await pulse(dut, "sof_accept_i")

    assert int(dut.threshold_active_o.value) == 0x22

    await apb_write(
        dut,
        THRESHOLD,
        0x33,
        sof_accept=True,
    )

    assert int(dut.threshold_active_o.value) == 0x22
    assert await apb_read(dut, THRESHOLD) == 0x33

    status = await apb_read(dut, STATUS)
    assert get_bit(status, 2) == 1

    await pulse(dut, "sof_accept_i")

    assert int(dut.threshold_active_o.value) == 0x33

    assert int(dut.bypass_threshold_active_o.value) == 0

    await apb_write(
        dut,
        CONTROL,
        0x0000_0003,
        sof_accept=True,
    )

    assert int(dut.run_enable_o.value) == 1
    assert int(dut.bypass_threshold_active_o.value) == 0

    control = await apb_read(dut, CONTROL)
    assert get_bit(control, 1) == 1

    status = await apb_read(dut, STATUS)
    assert get_bit(status, 2) == 1

    await pulse(dut, "sof_accept_i")

    assert int(dut.bypass_threshold_active_o.value) == 1

    status = await apb_read(dut, STATUS)
    assert get_bit(status, 2) == 0


@cocotb.test()
async def busy_draining_and_run_enable_storage(dut):
    await start_and_reset(dut)

    dut.processing_i.value = 1
    await settle()

    status = await apb_read(dut, STATUS)
    assert get_bit(status, 0) == 1
    assert get_bit(status, 1) == 0

    await apb_write(dut, CONTROL, 0x1)
    assert int(dut.run_enable_o.value) == 1

    await apb_write(dut, CONTROL, 0x0)

    assert int(dut.run_enable_o.value) == 0

    status = await apb_read(dut, STATUS)
    assert get_bit(status, 0) == 1

    dut.processing_i.value = 0
    dut.draining_i.value = 1
    await settle()

    status = await apb_read(dut, STATUS)
    assert get_bit(status, 0) == 1
    assert get_bit(status, 1) == 1

    dut.draining_i.value = 0
    await settle()

    status = await apb_read(dut, STATUS)
    assert get_bit(status, 0) == 0
    assert get_bit(status, 1) == 0


@cocotb.test()
async def invalid_and_misaligned_accesses_error_without_side_effect(dut):
    await start_and_reset(dut)

    await apb_write(dut, THRESHOLD, 0x55)
    assert await apb_read(dut, THRESHOLD) == 0x55

    await apb_write(
        dut,
        0x05,
        0xAA,
        expect_error=True,
    )

    assert await apb_read(dut, THRESHOLD) == 0x55

    misaligned = await apb_read(
        dut,
        0x01,
        expect_error=True,
    )
    assert misaligned == 0

    unmapped = await apb_read(
        dut,
        0x10,
        expect_error=True,
    )
    assert unmapped == 0

    assert await apb_read(dut, FRAME_COUNT) == 0

    await apb_write(
        dut,
        FRAME_COUNT,
        0xDEAD_BEEF,
        expect_error=False,
    )

    assert await apb_read(dut, FRAME_COUNT) == 0


@cocotb.test()
async def frame_error_is_sticky_w1c_and_set_wins(dut):
    await start_and_reset(dut)

    await pulse(dut, "frame_error_set_i")

    status = await apb_read(dut, STATUS)
    assert get_bit(status, 3) == 1

    await apb_write(dut, STATUS, 0x0000_0004)

    status = await apb_read(dut, STATUS)
    assert get_bit(status, 3) == 1

    await apb_write(dut, STATUS, 0x0000_0008)

    status = await apb_read(dut, STATUS)
    assert get_bit(status, 3) == 0

    await apb_write(
        dut,
        STATUS,
        0x0000_0008,
        frame_error_set=True,
    )

    status = await apb_read(dut, STATUS)
    assert get_bit(status, 3) == 1

    await apb_write(dut, STATUS, 0x0000_0008)

    status = await apb_read(dut, STATUS)
    assert get_bit(status, 3) == 0


@cocotb.test()
async def frame_count_increments_and_wraps(dut):
    await start_and_reset(dut)

    assert await apb_read(dut, FRAME_COUNT) == 0

    await pulse(dut, "frame_done_i")
    assert await apb_read(dut, FRAME_COUNT) == 1

    await pulse(dut, "frame_done_i")
    assert await apb_read(dut, FRAME_COUNT) == 2

    # Test-only state seeding to reach the rollover boundary without
    # simulating 2^32 frame completions. The actual increment path and APB
    # readback remain the DUT mechanisms under test.
    dut.frame_count_q.value = 0xFFFF_FFFF
    await settle()

    assert await apb_read(dut, FRAME_COUNT) == 0xFFFF_FFFF

    await pulse(dut, "frame_done_i")

    assert await apb_read(dut, FRAME_COUNT) == 0
