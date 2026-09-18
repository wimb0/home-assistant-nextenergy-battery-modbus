# In custom_components/nextenergy_battery/__init__.py

"""The NextEnergy Battery integration."""
import logging

import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from modbus_connection import ModbusError

from .const import (
    CONF_POLLING_INTERVAL,
    CONF_PREFIX,
    CONF_SLAVE_ID,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_PREFIX,
    DOMAIN,
    PLATFORMS,
    SETTINGS_POLLING_INTERVAL,
)
from .coordinator import NextEnergyDataCoordinator
from .device import NextEnergyBattery, create_connection

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
    slave_id = entry.data[CONF_SLAVE_ID]
    prefix = entry.options.get(CONF_PREFIX, DEFAULT_PREFIX) or DEFAULT_PREFIX
    polling_interval = entry.options.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)

    connection = create_connection(host, port)
    device = NextEnergyBattery(connection.for_unit(slave_id))
    # Live measurements poll fast; the rarely-changing settings poll slow.
    # Both share one connection, which serializes their requests.
    readings = NextEnergyDataCoordinator(
        hass,
        entry,
        device,
        connection,
        prefix,
        polling_interval,
        poll=device.async_update_readings,
        count_timeouts=True,
    )
    settings = NextEnergyDataCoordinator(
        hass,
        entry,
        device,
        connection,
        prefix,
        SETTINGS_POLLING_INTERVAL,
        poll=device.async_update_settings,
    )
    entry.async_on_unload(readings.async_close)

    try:
        await readings.async_setup()
    except ModbusError as err:
        raise ConfigEntryNotReady(f"Could not reach the battery: {err}") from err

    await readings.async_config_entry_first_refresh()
    await settings.async_config_entry_first_refresh()

    _async_migrate_to_serial_identity(hass, entry, device)

    hass.data[DOMAIN][entry.entry_id] = (readings, settings)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


def _async_migrate_to_serial_identity(
    hass: HomeAssistant, entry: ConfigEntry, device: NextEnergyBattery
) -> None:
    """Key this entry on the battery's serial number instead of its host.

    Entries created before serial probing used the host as unique id, so
    moving the battery to a new address looked like a new device. Entity
    unique ids and the device identifiers are entry-id based and therefore
    unaffected; only the entry's own unique id moves.
    """
    serial = device.identity.serial_number or None
    if serial is not None and entry.unique_id != serial:
        _LOGGER.info(
            "Migrating NextEnergy Battery entry from host identity %s to serial %s",
            entry.unique_id,
            serial,
        )
        hass.config_entries.async_update_entry(entry, unique_id=serial)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading NextEnergy Battery integration.")

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    _LOGGER.info("Updating NextEnergy Battery integration options.")
    await hass.config_entries.async_reload(entry.entry_id)
