"""Test NextEnergy Battery setup process."""
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nextenergy_battery.const import DOMAIN

from .const import MOCK_DATA, MOCK_OPTIONS, MOCK_SERIAL


async def test_setup_unload_and_reload_entry(
    hass: HomeAssistant, mock_device
) -> None:
    """Test entry setup, serial migration, unload, and reload."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_DATA, options=MOCK_OPTIONS)
    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state == ConfigEntryState.LOADED
    assert entry.unique_id == MOCK_SERIAL

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state == ConfigEntryState.NOT_LOADED

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state == ConfigEntryState.LOADED
