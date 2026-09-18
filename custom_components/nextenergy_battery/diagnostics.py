# In custom_components/nextenergy_battery/diagnostics.py

"""Diagnostics support for NextEnergy Battery."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from modbus_connection import ModbusError

from .const import CONF_SLAVE_ID, DOMAIN
from .coordinator import NextEnergyDataCoordinator
from .device import NextEnergyBattery

TO_REDACT = {CONF_HOST, CONF_PORT, CONF_SLAVE_ID}

# Holding registers carrying serial numbers: device serial, BMS master
# serial, and the five BMS slave serials. Dropped from the raw dump so a
# diagnostics download carries no device-identifying strings.
_SERIAL_RANGES = ((30016, 30031), (37005, 37020), (37097, 37176))


def _register_layout(device: NextEnergyBattery) -> dict[str, dict[str, str]]:
    """Where every declared field sits on the device, per component."""
    return {
        name: {
            field: f"{resolved.space}:0x{resolved.address:04X}"
            + (
                f"-0x{resolved.address + resolved.count - 1:04X}"
                if resolved.count > 1
                else ""
            )
            for field, resolved in component.resolved_fields.items()
        }
        for name, component in device.components.items()
    }


def _scrub_serials(raw: dict[str, dict[int, int | bool]]) -> dict[str, Any]:
    """Format the raw map as hex addresses, dropping serial registers."""
    serial_addresses = {
        address
        for low, high in _SERIAL_RANGES
        for address in range(low, high + 1)
    }
    return {
        space: {
            f"0x{address:04X}": value
            for address, value in values.items()
            if not (space == "holding" and address in serial_addresses)
        }
        for space, values in raw.items()
    }


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    readings, settings = hass.data[DOMAIN][entry.entry_id]
    coordinator: NextEnergyDataCoordinator = readings

    try:
        raw_registers: dict[str, Any] = _scrub_serials(
            await coordinator.device.async_read_raw()
        )
    except ModbusError as ex:
        raw_registers = {"error": str(ex)}

    failed = dict(readings.last_report.failed)
    failed.update(settings.last_report.failed)

    return {
        "config_entry_data": async_redact_data(dict(entry.data), TO_REDACT),
        "config_entry_options": dict(entry.options),
        "unserved_components": sorted(
            readings.absent_components | settings.absent_components
        ),
        "updated": sorted(
            readings.last_report.updated | settings.last_report.updated
        ),
        "failed": {name: str(err) for name, err in sorted(failed.items())},
        "register_layout": _register_layout(coordinator.device),
        "raw_registers": raw_registers,
    }
