""Test NextEnergy Battery sensor entities."""
from datetime import timedelta
from unittest.mock import patch

from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)

from custom_components.nextenergy_battery.const import DOMAIN
from .const import MOCK_CONFIG, MOCK_DYNAMIC_DATA_CHARGE, MOCK_STATIC_DATA


async def test_sensor_values(hass: HomeAssistant, bypass_get_data):
    """Test sensor availability and values."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, options=MOCK_CONFIG)
    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert hass.states.get(f"sensor.{MOCK_CONFIG['prefix']}_system_soc").state == "85"
    assert hass.states.get(f"sensor.{MOCK_CONFIG['prefix']}_battery_discharging").state == "550"
    assert hass.states.get(f"sensor.{MOCK_CONFIG['prefix']}_alarm_2").state == "Low insulation resistance"


async def test_charging_scenario(hass: HomeAssistant, bypass_get_data):
    """Test sensor values for a charging scenario."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, options=MOCK_CONFIG)
    entry.add_to_hass(hass)

    # Override the mock data for this specific test
    with patch(
        "custom_components.nextenergy_battery.modbus.NextEnergyModbusClient.read_sensors"
    ) as mock_read_sensors:
        mock_read_sensors.side_effect = lambda keys: MOCK_STATIC_DATA if "model_name" in keys else MOCK_DYNAMIC_DATA_CHARGE

        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        assert hass.states.get(f"sensor.{MOCK_CONFIG['prefix']}_battery_charging").state == "750"
        assert hass.states.get(f"sensor.{MOCK_CONFIG['prefix']}_grid_export").state == "1500"
        assert hass.states.get(f"sensor.{MOCK_CONFIG['prefix']}_work_mode").state == "Force Charge"


async def test_unavailable_scenario(hass: HomeAssistant, bypass_get_data):
    """Test sensor availability when the coordinator fails to update."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, options=MOCK_CONFIG)
    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    # First update is successful
    assert hass.states.get(f"sensor.{MOCK_CONFIG['prefix']}_system_soc").state == "85"

    # Now, simulate a failed update
    with patch(
        "custom_components.nextenergy_battery.modbus.NextEnergyModbusClient.read_sensors",
        side_effect=Exception("API is down"),
    ):
        future_time = dt_util.utcnow() + timedelta(seconds=30)
        async_fire_time_changed(hass, future_time)
        await hass.async_block_till_done()

        # ALL sensors should now be unavailable because the coordinator failed
        assert hass.states.get(f"sensor.{MOCK_CONFIG['prefix']}_system_soc").state == STATE_UNAVAILABLE
        assert hass.states.get(f"sensor.{MOCK_CONFIG['prefix']}_model_name").state == STATE_UNAVAILABLE


async def test_disabled_sensors(hass: HomeAssistant, bypass_get_data):
    """Test that sensors are disabled by default as expected."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, options=MOCK_CONFIG)
    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entity_registry = er.async_get(hass)

    entry_reg = entity_registry.async_get(f"sensor.{MOCK_CONFIG['prefix']}_serial_number")
    assert entry_reg is not None
    assert entry_reg.disabled
    assert entry_reg.disabled_by == er.RegistryEntryDisabler.INTEGRATION
