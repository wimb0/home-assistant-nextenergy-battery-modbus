"""Device model for the NextEnergy battery system, built on modbus-connection.

Backend-neutral: everything here talks to a ``ModbusUnit`` and works over
any modbus-connection backend (tmodbus, pymodbus, or the mock used in tests).
The integration owns the connection; this module only reads registers.
It has no Home Assistant dependency.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from modbus_connection import (
    IllegalDataAddressError,
    IllegalFunctionError,
    ModbusConnectionError,
    ModbusError,
    ModbusTcpParams,
    ModbusTimeoutError,
    ModbusUnit,
)
from modbus_connection.model import (
    Component,
    ComponentGroup,
    RegisterField,
    gauge,
    int32,
    integer,
    string,
    uint32,
)
from modbus_connection.tmodbus import ModbusConnection

_LOGGER = logging.getLogger(__name__)

MODBUS_TIMEOUT = 5

# The refusals that mean the registers are not in this device's map. Every
# other exception response says the registers are there and the read failed,
# so those propagate.
_NOT_SERVED = (IllegalFunctionError, IllegalDataAddressError)

# Components refreshed every poll, in read order. Static identity blocks are
# read once at setup and never polled. Settings change rarely, so they poll
# on their own slow interval.
_POLLED_READINGS = (
    "bms_live",
    "meter",
    "inverter_live",
    "powerflow",
    "energy",
)
_POLLED_SETTINGS = ("settings",)
_POLLED = (*_POLLED_READINGS, *_POLLED_SETTINGS)


@dataclass(frozen=True)
class UpdateReport:
    """What one poll refreshed, by the device's component attribute names."""

    updated: set[str]
    failed: dict[str, ModbusError]

    @property
    def complete(self) -> bool:
        """Whether every polled component refreshed."""
        return not self.failed


def create_connection(host: str, port: int) -> ModbusConnection:
    """Create a TCP device connection, shared by entry setup and the config flow."""
    return ModbusConnection(
        ModbusTcpParams(host=host, port=port), timeout=MODBUS_TIMEOUT
    )


class VersionField(RegisterField[str]):
    """A NextEnergy firmware version word: 0xABC -> "A.B.C" (one nibble each)."""

    def decode(
        self, words: list[int], scale_exponent: int | None = None
    ) -> str | None:
        """Decode the packed BCD version word."""
        value = words[0]
        return f"{(value >> 8) & 0xF}.{(value >> 4) & 0xF}.{value & 0xF}"

    def encode(self, value: Any, scale_exponent: int | None = None) -> list[int]:
        """Versions are read-only; encoding is unsupported."""
        raise ValueError("Version registers are read-only")


class DeviceIdentity(Component):
    """Static device identity, read once at setup."""

    # Proven by probe: the whole 30000-30031 block reads as one.
    register_ranges = ((30000, 30031),)

    model_name = string(30000, 16)
    serial_number = string(30016, 16)


class InverterStatic(Component):
    """Static inverter ratings, read once at setup."""

    # Proven by probe: 39053-39062 reads as one block.
    register_ranges = ((36001, 36001), (39053, 39062))

    master_version = VersionField(36001)
    rated_power = int32(39053, scale=0.001)
    max_active_power = int32(39055, scale=0.001)
    max_apparent_power = int32(39057, scale=0.001)
    max_reactive_power_fed = int32(39059, scale=0.001)
    max_reactive_power_absorbed = int32(39061, scale=0.001)


class BmsStatic(Component):
    """Static BMS identity, read once at setup."""

    # Probed: each range below reads as one block, but a read spanning the
    # gaps between them comes back short — so a block never crosses a range
    # boundary. The five slave serials (37097-37176) read as one 80-register
    # block.
    register_ranges = (
        (37003, 37020),
        (37032, 37037),
        (37097, 37176),
        (37635, 37636),
    )

    bms_master_version = VersionField(37003)
    bms_master_type = integer(37004, signed=False)
    bms_master_sn = string(37005, 16)
    bms_slave_number = integer(37032, signed=False)
    bms_slave_1_version = VersionField(37033)
    bms_slave_2_version = VersionField(37034)
    bms_slave_3_version = VersionField(37035)
    bms_slave_4_version = VersionField(37036)
    bms_slave_5_version = VersionField(37037)
    bms_slave_1_sn = string(37097, 16)
    bms_slave_2_sn = string(37113, 16)
    bms_slave_3_sn = string(37129, 16)
    bms_slave_4_sn = string(37145, 16)
    bms_slave_5_sn = string(37161, 16)
    bms_design_energy = gauge(37635, 0.01, signed=False)
    battery_flag = integer(37636, signed=False)


class BmsLive(Component):
    """Live BMS readings, polled every update cycle."""

    # Probed: 37609-37633 reads as one 25-register block.
    register_ranges = ((37002, 37002), (37609, 37633))

    bms_connection_status = integer(37002, signed=False)
    bms_voltage = gauge(37609, 0.1, signed=False)
    bms_current = gauge(37610, 0.1)
    bms_ambient_temp = gauge(37611, 0.1)
    bms_soc = integer(37612, signed=False)
    bms_max_temp = gauge(37617, 0.1)
    bms_min_temp = gauge(37618, 0.1)
    bms_max_cell_voltage = integer(37619, signed=False)
    bms_min_cell_voltage = integer(37620, signed=False)
    bms_soh = integer(37624, signed=False)
    bms_fault_1 = integer(37626, signed=False)
    bms_fault_2 = integer(37627, signed=False)
    bms_fault_3 = integer(37628, signed=False)
    bms_fault_4 = integer(37629, signed=False)
    bms_fault_5 = integer(37630, signed=False)
    bms_fault_6 = integer(37631, signed=False)
    bms_remain_energy = gauge(37632, 0.01, signed=False)
    bms_fcc_capacity = gauge(37633, 0.1, signed=False)


class Meter(Component):
    """External meter readings, polled every update cycle."""

    # Probed: 38801-38815 reads as one 15-register block.
    register_ranges = ((38801, 38815),)

    meter_connection_status = integer(38801, signed=False)
    r_phase_voltage = int32(38802, scale=0.1)
    s_phase_voltage = int32(38804, scale=0.1)
    t_phase_voltage = int32(38806, scale=0.1)
    r_phase_current = int32(38808, scale=0.001)
    s_phase_current = int32(38810, scale=0.001)
    t_phase_current = int32(38812, scale=0.001)
    combined_active_power = int32(38814, scale=0.1)


class InverterLive(Component):
    """Live inverter state, polled every update cycle."""

    # Probed: each range below reads as one block (39134-39141 spans the
    # unmapped 39140 and still answers in full).
    register_ranges = ((39063, 39069), (39123, 39125), (39134, 39141))

    inverter_status_1 = integer(39063, signed=False)
    inverter_status_3 = uint32(39065)
    alarm_1 = integer(39067, signed=False)
    alarm_2 = integer(39068, signed=False)
    alarm_3 = integer(39069, signed=False)
    grid_r_voltage = gauge(39123, 0.1)
    grid_s_voltage = gauge(39124, 0.1)
    grid_t_voltage = gauge(39125, 0.1)
    active_power = int32(39134, scale=0.001)
    reactive_power = int32(39136, scale=0.001)
    power_factor = gauge(39138, 0.001)
    grid_frequency = gauge(39139, 0.01)
    inverter_temp = gauge(39141, 0.1)


class PowerFlow(Component):
    """Instantaneous power flow, polled every update cycle."""

    # Probed: 39225-39238 reads as one block, covering load and battery power
    # across the gap between them.
    register_ranges = (
        (39168, 39169),
        (39216, 39217),
        (39225, 39238),
        (39423, 39423),
    )

    grid_power_meter = int32(39168)
    eps_power = int32(39216)
    load_power = int32(39225)
    battery_power = int32(39237)
    system_soc = integer(39423, signed=False)


class Energy(Component):
    """Cumulative energy counters, polled every update cycle."""

    # Probed: 39605-39632 reads as one 28-register block (the last counter
    # spans 39631-39632).
    register_ranges = ((39605, 39632),)

    battery_charge_total = uint32(39605, scale=0.01)
    battery_charge_today = uint32(39607, scale=0.01)
    battery_discharge_total = uint32(39609, scale=0.01)
    battery_discharge_today = uint32(39611, scale=0.01)
    grid_export_total = uint32(39613, scale=0.01)
    grid_export_today = uint32(39615, scale=0.01)
    grid_import_total = uint32(39617, scale=0.01)
    grid_import_today = uint32(39619, scale=0.01)
    output_energy_total = uint32(39621, scale=0.01)
    output_energy_today = uint32(39623, scale=0.01)
    input_energy_total = uint32(39625, scale=0.01)
    input_energy_today = uint32(39627, scale=0.01)
    total_load_power = uint32(39629, scale=0.01)
    total_load_power_today = uint32(39631, scale=0.01)


class Settings(Component):
    """Configuration registers, polled on the slow interval."""

    # Probed: 49203 answers 49203-49212 only, so each of the 49xxx registers
    # reads on its own — except network status, which lives at 49240 (49242
    # is the trigger-signal bitfield). 46609-46611 reads as one block.
    register_ranges = (
        (46609, 46611),
        (49203, 49203),
        (49228, 49228),
        (49240, 49240),
    )

    min_soc = integer(46609, signed=False)
    max_soc = integer(46610, signed=False)
    min_soc_ongrid = integer(46611, signed=False)
    work_mode = integer(49203, signed=False)
    system_power_state = integer(49228, signed=False)
    network_status = integer(49240, signed=False)


class NextEnergyBattery:
    """A NextEnergy battery system on a Modbus unit.

    Reading it has two phases. ``async_setup`` runs once: it reads the static
    identity and finds out which optional blocks this firmware serves.
    ``async_update`` then runs every interval over the live components setup
    settled on.
    """

    def __init__(self, unit: ModbusUnit) -> None:
        """Initialize the device's components on ``unit``."""
        self._unit = unit
        self.identity = DeviceIdentity(unit)
        self.inverter_static = InverterStatic(unit)
        self.bms_static = BmsStatic(unit)
        self.bms_live = BmsLive(unit)
        self.meter = Meter(unit)
        self.inverter_live = InverterLive(unit)
        self.powerflow = PowerFlow(unit)
        self.energy = Energy(unit)
        self.settings = Settings(unit)
        self.absent: frozenset[str] = frozenset()
        # None until async_setup has run, so a failed setup is retried.
        self._polled: list[str] | None = None
        self._readable = ComponentGroup(
            unit,
            [
                self.identity,
                self.inverter_static,
                self.bms_static,
                self.bms_live,
                self.meter,
                self.inverter_live,
                self.powerflow,
                self.energy,
                self.settings,
            ],
        )

    @property
    def components(self) -> dict[str, Component]:
        """Every component of this device, by the name diagnostics reports."""
        return {
            "identity": self.identity,
            "inverter_static": self.inverter_static,
            "bms_static": self.bms_static,
            "bms_live": self.bms_live,
            "meter": self.meter,
            "inverter_live": self.inverter_live,
            "powerflow": self.powerflow,
            "energy": self.energy,
            "settings": self.settings,
        }

    @classmethod
    async def async_probe(cls, unit: ModbusUnit) -> str:
        """Read the device's serial number, proving it is reachable."""
        info = DeviceIdentity(unit)
        await info.async_update()
        return info.serial_number or ""

    @classmethod
    async def async_probe_connection(cls, connection: ModbusConnection) -> str:
        """Probe over an already-built connection, closing it afterwards."""
        try:
            return await cls.async_probe(connection.for_unit(1))
        finally:
            await connection.close()

    async def async_setup(self) -> None:
        """Read the static data and learn which optional blocks exist.

        The identity block is required: a failure here propagates and the
        config entry retries later. The remaining static blocks are optional;
        a refusal means that firmware does not serve them.
        """
        await self.identity.async_update()

        absent = set()
        for name, component in (
            ("inverter_static", self.inverter_static),
            ("bms_static", self.bms_static),
        ):
            try:
                await component.async_update()
            except _NOT_SERVED as ex:
                absent.add(name)
                _LOGGER.info(
                    "This device does not serve the %s registers at %s, so "
                    "they stay unavailable and are not read again",
                    name,
                    ex.block,
                )
        self.absent = frozenset(absent)
        self._polled = [name for name in _POLLED if name not in absent]

    async def _async_poll_names(self, names: tuple[str, ...]) -> UpdateReport:
        """Read the named components, one at a time.

        A component whose read fails keeps its previous values while the rest
        still refresh, so one slow block cannot blank the whole device.
        Listeners fire only once every component has been tried, and only for
        the ones that refreshed. A failure of the link itself raises
        ``ModbusConnectionError`` rather than reporting partial silence, and so
        does a first component that times out: nothing has answered yet, so
        reading on would only pay the same timeout again.
        """
        updated: set[str] = set()
        failed: dict[str, ModbusError] = {}
        for name in names:
            component: Component = getattr(self, name)
            try:
                await component.async_update(notify=False)
            except ModbusConnectionError:
                raise
            except ModbusTimeoutError as err:
                if not updated and not failed:
                    raise  # nothing answered; the rest would only time out too
                failed[name] = err
            except ModbusError as err:
                failed[name] = err
            else:
                updated.add(name)
        for name in updated:
            fresh: Component = getattr(self, name)
            fresh.notify()
        return UpdateReport(updated, failed)

    async def async_update_readings(self) -> UpdateReport:
        """Refresh the fast-changing measurements (30s interval)."""
        if self._polled is None:
            await self.async_setup()
        return await self._async_poll_names(_POLLED_READINGS)

    async def async_update_settings(self) -> UpdateReport:
        """Refresh the rarely-changing configuration (slow interval)."""
        if self._polled is None:
            await self.async_setup()
        return await self._async_poll_names(_POLLED_SETTINGS)

    async def async_update(self) -> UpdateReport:
        """Refresh every polled component, one at a time."""
        if self._polled is None:
            await self.async_setup()
        readings = await self._async_poll_names(_POLLED_READINGS)
        settings = await self._async_poll_names(_POLLED_SETTINGS)
        return UpdateReport(
            readings.updated | settings.updated,
            {**readings.failed, **settings.failed},
        )

    async def async_read_raw(self) -> dict[str, dict[int, int | bool]]:
        """Read the raw registers backing every readable component.

        The fields refresh but no listener fires: a diagnostics download is not
        a poll, and should not write a state for every entity off the cycle.
        """
        return await self._readable.async_read_raw(notify=False)
