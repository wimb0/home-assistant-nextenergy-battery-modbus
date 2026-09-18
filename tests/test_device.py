"""Test the NextEnergy battery device model without hardware."""
import pytest

from modbus_connection import IllegalDataAddressError, ModbusTimeoutError

from custom_components.nextenergy_battery.device import (
    BmsLive,
    DeviceIdentity,
    InverterStatic,
    NextEnergyBattery,
    PowerFlow,
)

from .const import MOCK_SERIAL, seed_discharge


async def test_static_decoding(mock_modbus_unit) -> None:
    """Test identity strings and the BCD version field."""
    seed_discharge(mock_modbus_unit)

    identity = DeviceIdentity(mock_modbus_unit)
    await identity.async_update()
    assert identity.model_name == "MQ2200-M-A"
    assert identity.serial_number == MOCK_SERIAL

    inverter = InverterStatic(mock_modbus_unit)
    await inverter.async_update()
    assert inverter.master_version == "1.2.3"
    assert inverter.rated_power == 2.2


async def test_signed_power_decoding(mock_modbus_unit) -> None:
    """Test a negative 32-bit power value decodes with its sign."""
    seed_discharge(mock_modbus_unit)

    powerflow = PowerFlow(mock_modbus_unit)
    await powerflow.async_update()
    assert powerflow.battery_power == -550
    assert powerflow.grid_power_meter == 200


async def test_bms_gauge_scaling(mock_modbus_unit) -> None:
    """Test a 0.1-scaled gauge and an unscaled SoC register."""
    seed_discharge(mock_modbus_unit)
    mock_modbus_unit.holding[37609] = 360

    bms = BmsLive(mock_modbus_unit)
    await bms.async_update()
    assert bms.bms_voltage == 36.0
    assert bms.bms_soc == 85


async def test_readings_block_count(mock_modbus_unit) -> None:
    """Test one poll reads the live map in eleven block reads."""
    seed_discharge(mock_modbus_unit)
    device = NextEnergyBattery(mock_modbus_unit)
    await device.async_setup()

    before = len(mock_modbus_unit.read_events)
    report = await device.async_update_readings()

    assert report.complete
    assert len(mock_modbus_unit.read_events) - before == 11


async def test_partial_failure_keeps_other_components(
    mock_modbus_unit,
) -> None:
    """Test one refusing block fails only its own component."""
    seed_discharge(mock_modbus_unit)
    device = NextEnergyBattery(mock_modbus_unit)
    await device.async_setup()

    mock_modbus_unit.fail_read(39605, IllegalDataAddressError())
    report = await device.async_update_readings()

    assert not report.complete
    assert set(report.failed) == {"energy"}
    assert {"bms_live", "meter", "inverter_live", "powerflow"} <= report.updated


async def test_absent_static_component(mock_modbus_unit) -> None:
    """Test a refused static block is marked absent at setup."""
    seed_discharge(mock_modbus_unit)
    device = NextEnergyBattery(mock_modbus_unit)

    mock_modbus_unit.fail_read(39053, IllegalDataAddressError())
    await device.async_setup()

    assert "inverter_static" in device.absent


async def test_probe_returns_serial(mock_modbus_unit) -> None:
    """Test probing reads the serial number."""
    seed_discharge(mock_modbus_unit)

    assert await NextEnergyBattery.async_probe(mock_modbus_unit) == MOCK_SERIAL


async def test_total_silence_raises(mock_modbus_unit) -> None:
    """Test a poll that reaches nothing raises instead of reporting."""
    seed_discharge(mock_modbus_unit)
    device = NextEnergyBattery(mock_modbus_unit)
    await device.async_setup()

    mock_modbus_unit.fail_requests(ModbusTimeoutError())
    with pytest.raises(ModbusTimeoutError):
        await device.async_update_readings()
