"""Diagnostics support for NextEnergy Battery."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import NextEnergyDataCoordinator


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: NextEnergyDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    return {
        "entry": entry.as_dict(),
        "coordinator_data": coordinator.data,
    }
