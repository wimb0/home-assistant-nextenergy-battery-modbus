"""Data coordinator for the NextEnergy Battery integration."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from modbus_connection import ModbusError, ModbusTimeoutError
from modbus_connection.tmodbus import ModbusConnection

from .const import (
    ALARM_1_MESSAGES,
    ALARM_2_MESSAGES,
    ALARM_3_MESSAGES,
    DOMAIN,
    MANUFACTURER,
    NETWORK_STATUS_MESSAGES,
    STATUS_1_MESSAGES,
    SYSTEM_POWER_STATE_MESSAGES,
    WORK_MODE_MESSAGES,
)
from .device import NextEnergyBattery, UpdateReport
from .util import parse_bitfield_messages

_LOGGER = logging.getLogger(__name__)

# Consecutive timeouts before the link is treated as stuck rather than slow.
_STUCK_AFTER_TIMEOUTS = 3


class NextEnergyDataCoordinator(DataUpdateCoordinator[None]):
    """Coordinator running one of the device's update methods on its interval."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        device: NextEnergyBattery,
        connection: ModbusConnection,
        prefix: str,
        polling_interval: int,
        poll: Callable[[], Awaitable[UpdateReport]],
        count_timeouts: bool = False,
    ) -> None:
        """Initialize.

        ``count_timeouts`` enables stuck-link detection; it must be set on one
        coordinator only (the fastest interval), so a second coordinator never
        drops the link under a poll already in flight.
        """
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN} {poll.__name__}",
            update_interval=timedelta(seconds=polling_interval),
        )
        self.device = device
        self._connection = connection
        self.prefix = prefix
        self._poll = poll
        self._count_timeouts = count_timeouts
        # Consecutive poll timeouts; reset by any poll that reaches the device.
        self._timeouts = 0
        # What the last poll managed to read; diagnostics reports it, and the
        # components it missed have their entities go unavailable.
        self._report = UpdateReport(set(), {})

    @property
    def serial_number(self) -> str | None:
        """The device serial number, once the identity registers were read."""
        return self.device.identity.serial_number or None

    @property
    def device_info(self) -> DeviceInfo:
        """Device registry entry for this battery system."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.config_entry.entry_id)},
            name=f"{MANUFACTURER} Battery",
            manufacturer=MANUFACTURER,
            model=self.device.identity.model_name,
            sw_version=self.device.inverter_static.master_version,
            serial_number=self.serial_number,
        )

    async def async_close(self) -> None:
        """Close the Modbus connection."""
        await self._connection.close()

    async def async_setup(self) -> None:
        """Read the static data and discover what this device serves.

        Raises ModbusError if the device cannot be reached.
        """
        await self.device.async_setup()

    async def _async_note_timeout(self) -> None:
        """Count a timeout, and drop the link once it looks stuck."""
        self._timeouts += 1
        if self._timeouts < _STUCK_AFTER_TIMEOUTS:
            return
        _LOGGER.debug("Dropping a stuck link after %d timeouts", self._timeouts)
        self._timeouts = 0
        await self._connection.disconnect()

    async def _async_update_data(self) -> None:
        """Refresh the device's components; entities read them directly.

        Each component is read on its own, so one that fails costs only its own
        entities. The update itself fails only when nothing answered at all.
        """
        try:
            report = await self._poll()
        except ModbusTimeoutError as ex:
            if self._count_timeouts:
                await self._async_note_timeout()
            raise UpdateFailed(f"Failed to fetch data: {ex}") from ex
        except ModbusError as ex:
            raise UpdateFailed(f"Failed to fetch data: {ex}") from ex

        self._timeouts = 0

        was_failing = self.failed_components
        self._report = report

        if not report.updated:
            errors = list(report.failed.values())
            raise UpdateFailed(
                f"Failed to fetch data: {errors[0]}"
            ) from errors[0]

        for name in sorted(report.failed.keys() - was_failing):
            _LOGGER.warning("Failed to fetch %s: %s", name, report.failed[name])

    @property
    def absent_components(self) -> frozenset[str]:
        """Components this device does not serve."""
        return self.device.absent

    @property
    def last_report(self) -> UpdateReport:
        """What the last poll refreshed and what it missed."""
        return self._report

    @property
    def failed_components(self) -> frozenset[str]:
        """Components the last poll could not read."""
        return frozenset(self._report.failed)

    # --- Derived values (previously computed over a raw data dict) ---

    @property
    def alarm_1(self) -> str:
        """Alarm block 1 as a readable string."""
        return parse_bitfield_messages(
            self.device.inverter_live.alarm_1, ALARM_1_MESSAGES
        )

    @property
    def alarm_2(self) -> str:
        """Alarm block 2 as a readable string."""
        return parse_bitfield_messages(
            self.device.inverter_live.alarm_2, ALARM_2_MESSAGES
        )

    @property
    def alarm_3(self) -> str:
        """Alarm block 3 as a readable string."""
        return parse_bitfield_messages(
            self.device.inverter_live.alarm_3, ALARM_3_MESSAGES
        )

    @property
    def inverter_status_1(self) -> str:
        """Inverter status as a readable string."""
        value = self.device.inverter_live.inverter_status_1
        if value is None:
            return "Unknown"
        return parse_bitfield_messages(value, STATUS_1_MESSAGES)

    @property
    def inverter_status_3(self) -> str:
        """Grid connection state as a readable string."""
        value = self.device.inverter_live.inverter_status_3
        if value is None:
            return "Unknown"
        return "Off-grid" if (value >> 0) & 1 else "On-grid"

    @property
    def work_mode(self) -> str:
        """Work mode as a readable string."""
        return WORK_MODE_MESSAGES.get(self.device.settings.work_mode, "Unknown")

    @property
    def system_power_state(self) -> str:
        """System power state as a readable string."""
        return SYSTEM_POWER_STATE_MESSAGES.get(
            self.device.settings.system_power_state, "Unknown"
        )

    @property
    def network_status(self) -> str:
        """Network status as a readable string."""
        return NETWORK_STATUS_MESSAGES.get(
            self.device.settings.network_status, "Unknown"
        )

    @property
    def battery_charging(self) -> float | None:
        """Charging power (positive part of battery power)."""
        power = self.device.powerflow.battery_power
        if power is None:
            return None
        return max(0, power)

    @property
    def battery_discharging(self) -> float | None:
        """Discharging power (absolute negative part of battery power)."""
        power = self.device.powerflow.battery_power
        if power is None:
            return None
        return abs(power) if power < 0 else 0

    @property
    def grid_import(self) -> float | None:
        """Import power (positive part of meter power)."""
        power = self.device.powerflow.grid_power_meter
        if power is None:
            return None
        return max(0, power)

    @property
    def grid_export(self) -> float | None:
        """Export power (absolute negative part of meter power)."""
        power = self.device.powerflow.grid_power_meter
        if power is None:
            return None
        return abs(power) if power < 0 else 0
