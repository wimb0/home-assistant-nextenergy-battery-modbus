"""Test NextEnergy Battery sensor entities."""
from datetime import timedelta

from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from modbus_connection import ModbusTimeoutError
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)

from custom_components.nextenergy_battery.const import DOMAIN

from .const import MOCK_DATA, MOCK_OPTIONS, seed_charge, seed_discharge


async def test_sensor_values(
    hass: HomeAssistant, mock_connection, mock_modbus_unit
) -> None:
    """Test sensor availability and values while discharging."""
    seed_discharge(mock_modbus_unit)
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_DATA, options=MOCK_OPTIONS)
    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    prefix = MOCK_OPTIONS["prefix"]
    assert hass.states.get(f"sensor.{prefix}_system_soc").state == "85"
    assert hass.states.get(f"sensor.{prefix}_battery_discharging").state == "550"
    assert (
        hass.states.get(f"sensor.{prefix}_alarm_2").state
        == "Low insulation resistance"
    )
    assert hass.states.get(f"sensor.{prefix}_work_mode").state == "Self-Use"
    assert hass.states.get(f"sensor.{prefix}_output_energy_total").state == "945.39"


async def test_charging_scenario(
    hass: HomeAssistant, mock_connection, mock_modbus_unit
) -> None:
    """Test sensor values for a charging scenario."""
    seed_charge(mock_modbus_unit)
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_DATA, options=MOCK_OPTIONS)
    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    prefix = MOCK_OPTIONS["prefix"]
    assert hass.states.get(f"sensor.{prefix}_battery_charging").state == "750"
    assert hass.states.get(f"sensor.{prefix}_grid_export").state == "1500"
    assert hass.states.get(f"sensor.{prefix}_work_mode").state == "Force Charge"


async def test_unavailable_scenario(
    hass: HomeAssistant, mock_connection, mock_modbus_unit
) -> None:
    """Test availability when polls stop reaching the battery."""
    seed_discharge(mock_modbus_unit)
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_DATA, options=MOCK_OPTIONS)
    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    prefix = MOCK_OPTIONS["prefix"]
    assert hass.states.get(f"sensor.{prefix}_system_soc").state == "85"

    mock_modbus_unit.fail_requests(ModbusTimeoutError())
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=35))
    await hass.async_block_till_done()

    # Live sensors go unavailable, but static info and energy totals hold.
    assert (
        hass.states.get(f"sensor.{prefix}_system_soc").state == STATE_UNAVAILABLE
    )
    assert hass.states.get(f"sensor.{prefix}_model_name").state == "MQ2200-M-A"
    assert (
        hass.states.get(f"sensor.{prefix}_battery_charge_total").state
        != STATE_UNAVAILABLE
    )

    mock_modbus_unit.fail_requests(None)
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=70))
    await hass.async_block_till_done()

    assert hass.states.get(f"sensor.{prefix}_system_soc").state == "85"


async def test_disabled_sensors(
    hass: HomeAssistant, mock_connection, mock_modbus_unit
) -> None:
    """Test that sensors are disabled by default as expected."""
    seed_discharge(mock_modbus_unit)
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_DATA, options=MOCK_OPTIONS)
    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entity_registry = er.async_get(hass)

    entry_reg = entity_registry.async_get(
        f"sensor.{MOCK_OPTIONS['prefix']}_serial_number"
    )
    assert entry_reg is not None
    assert entry_reg.disabled
    assert entry_reg.disabled_by == er.RegistryEntryDisabler.INTEGRATION
