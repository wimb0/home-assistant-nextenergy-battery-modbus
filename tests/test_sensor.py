"""Test NextEnergy Battery sensor entities."""
from homeassistant.core import HomeAssistant
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.helpers import entity_registry as er

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nextenergy_battery.const import DOMAIN, DYNAMIC_SENSORS, STATIC_SENSORS
from .const import MOCK_CONFIG

async def test_sensor_availability_and_values(hass: HomeAssistant, bypass_get_data):
    """Test sensor availability and values."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG)
    entry.add_to_hass(hass)
    
    # Initialize the integration
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entity_registry = er.async_get(hass)
    
    # Check a static sensor
    state = hass.states.get(f"sensor.{MOCK_CONFIG['prefix']}_model_name")
    assert state
    assert state.state == "MQ2200-M-A"

    # Check a dynamic sensor
    state = hass.states.get(f"sensor.{MOCK_CONFIG['prefix']}_system_soc")
    assert state
    assert state.state == "85"
    assert state.attributes.get("unit_of_measurement") == "%"

    # Check a derived sensor (discharging)
    state = hass.states.get(f"sensor.{MOCK_CONFIG['prefix']}_battery_discharging")
    assert state
    assert state.state == "550"

    state = hass.states.get(f"sensor.{MOCK_CONFIG['prefix']}_battery_charging")
    assert state
    assert state.state == "0"

    # Check a derived sensor (grid import)
    state = hass.states.get(f"sensor.{MOCK_CONFIG['prefix']}_grid_import")
    assert state
    assert state.state == "200"

    state = hass.states.get(f"sensor.{MOCK_CONFIG['prefix']}_grid_export")
    assert state
    assert state.state == "0"
    
    # Check a processed status sensor
    state = hass.states.get(f"sensor.{MOCK_CONFIG['prefix']}_inverter_status_1")
    assert state
    assert state.state == "Operation"
    
    # Check a processed alarm sensor
    state = hass.states.get(f"sensor.{MOCK_CONFIG['prefix']}_alarm_2")
    assert state
    assert state.state == "Low insulation resistance"

async def test_disabled_sensors(hass: HomeAssistant, bypass_get_data):
    """Test that sensors are disabled by default as expected."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG)
    entry.add_to_hass(hass)
    
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entity_registry = er.async_get(hass)

    # Check a sensor that should be disabled by default
    entry = entity_registry.async_get(f"sensor.{MOCK_CONFIG['prefix']}_serial_number")
    assert entry
    assert entry.disabled
    assert entry.disabled_by == er.RegistryEntryDisabler.INTEGRATION
