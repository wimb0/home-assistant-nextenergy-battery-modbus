"""Test NextEnergy Battery setup process."""
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nextenergy_battery.const import DOMAIN
from .const import MOCK_CONFIG


async def test_setup_unload_and_reload_entry(hass: HomeAssistant, mock_modbus_client):
    """Test entry setup and unload."""
    # Create a mock config entry
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, options=MOCK_CONFIG)
    entry.add_to_hass(hass)

    # Set up the entry and assert that it's loaded
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state == ConfigEntryState.LOADED
    assert DOMAIN in hass.data

    # Unload the entry and assert that it's been removed
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state == ConfigEntryState.NOT_LOADED
