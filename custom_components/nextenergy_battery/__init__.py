"""The NextEnergy Battery integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import DOMAIN, PLATFORMS
from .modbus import NextEnergyModbusClient
from .coordinator import NextEnergyDataCoordinator

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the NextEnergy Battery component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up NextEnergy Battery from a config entry."""
    _LOGGER.info("Setting up NextEnergy Battery integration.")

    host = entry.data["host"]
    port = entry.data["port"]
    slave_id = entry.data["slave_id"]
    polling_interval = entry.options.get("polling_interval", entry.data.get("polling_interval", 30))

    client = NextEnergyModbusClient(host, port, slave_id)
    coordinator = NextEnergyDataCoordinator(hass, client, polling_interval)

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    entry.async_on_unload(entry.add_update_listener(update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading NextEnergy Battery integration.")

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        entry.async_on_unload(None)
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    _LOGGER.info("Updating NextEnergy Battery integration.")
    await hass.config_entries.async_reload(entry.entry_id)
