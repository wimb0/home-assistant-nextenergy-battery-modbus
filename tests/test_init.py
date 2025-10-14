"""Test NextEnergy Battery setup process."""
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import STATE_UNAVAILABLE

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nextenergy_battery import (
    async_setup_entry,
    async_unload_entry,
)
from custom_components.nextenergy_battery.const import DOMAIN

from .const import MOCK_CONFIG


async def test_setup_unload_and_reload_entry(hass: HomeAssistant, bypass_get_data):
    """Test entry setup and unload."""
    # Create a mock config entry
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG)
    entry.add_to_hass(hass)

    # Set up the entry and assert that it's loaded
    assert await async_setup_entry(hass, entry)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids("sensor")) > 0
    assert entry.state == ConfigEntryState.LOADED

    # Unload the entry and assert that it's been removed
    assert await async_unload_entry(hass, entry)
    await hass.async_block_till_done()

    assert entry.state == ConfigEntryState.NOT_LOADED
