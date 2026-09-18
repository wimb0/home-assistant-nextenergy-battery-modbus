"""Platform for sensor integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import UnitOfPower

from .const import DOMAIN, SENSORS, DISABLED_BY_DEFAULT
from .coordinator import NextEnergyDataCoordinator


@dataclass(frozen=True, kw_only=True)
class NextEnergySensorEntityDescription(SensorEntityDescription):
    """A sensor reading one value off the battery system."""

    value_fn: Callable[[NextEnergyDataCoordinator], object]
    # The device component this entity reads. An entity naming a component the
    # device does not serve is never created, and one naming a component a
    # poll failed to read goes unavailable until it reads again.
    component: str = "bms_live"


# Key -> (value_fn, component). Metadata (name/unit/class/icon) comes from
# const.SENSORS so the register map stays in one place.
SENSOR_VALUES: dict[str, tuple[Callable, str]] = {
    "model_name": (lambda c: c.device.identity.model_name, "identity"),
    "serial_number": (lambda c: c.device.identity.serial_number, "identity"),
    "master_version": (
        lambda c: c.device.inverter_static.master_version,
        "inverter_static",
    ),
    "bms_master_version": (
        lambda c: c.device.bms_static.bms_master_version,
        "bms_static",
    ),
    "bms_master_sn": (lambda c: c.device.bms_static.bms_master_sn, "bms_static"),
    "bms_slave_number": (
        lambda c: c.device.bms_static.bms_slave_number,
        "bms_static",
    ),
    "bms_slave_1_version": (
        lambda c: c.device.bms_static.bms_slave_1_version,
        "bms_static",
    ),
    "bms_slave_2_version": (
        lambda c: c.device.bms_static.bms_slave_2_version,
        "bms_static",
    ),
    "bms_slave_3_version": (
        lambda c: c.device.bms_static.bms_slave_3_version,
        "bms_static",
    ),
    "bms_slave_4_version": (
        lambda c: c.device.bms_static.bms_slave_4_version,
        "bms_static",
    ),
    "bms_slave_5_version": (
        lambda c: c.device.bms_static.bms_slave_5_version,
        "bms_static",
    ),
    "bms_slave_1_sn": (lambda c: c.device.bms_static.bms_slave_1_sn, "bms_static"),
    "bms_slave_2_sn": (lambda c: c.device.bms_static.bms_slave_2_sn, "bms_static"),
    "bms_slave_3_sn": (lambda c: c.device.bms_static.bms_slave_3_sn, "bms_static"),
    "bms_slave_4_sn": (lambda c: c.device.bms_static.bms_slave_4_sn, "bms_static"),
    "bms_slave_5_sn": (lambda c: c.device.bms_static.bms_slave_5_sn, "bms_static"),
    "bms_design_energy": (
        lambda c: c.device.bms_static.bms_design_energy,
        "bms_static",
    ),
    "battery_flag": (
        lambda c: c.device.bms_static.battery_flag,
        "bms_static",
    ),
    "bms_master_type": (
        lambda c: c.device.bms_static.bms_master_type,
        "bms_static",
    ),
    "rated_power": (
        lambda c: c.device.inverter_static.rated_power,
        "inverter_static",
    ),
    "max_active_power": (
        lambda c: c.device.inverter_static.max_active_power,
        "inverter_static",
    ),
    "max_apparent_power": (
        lambda c: c.device.inverter_static.max_apparent_power,
        "inverter_static",
    ),
    "max_reactive_power_fed": (
        lambda c: c.device.inverter_static.max_reactive_power_fed,
        "inverter_static",
    ),
    "max_reactive_power_absorbed": (
        lambda c: c.device.inverter_static.max_reactive_power_absorbed,
        "inverter_static",
    ),
    "bms_connection_status": (
        lambda c: c.device.bms_live.bms_connection_status,
        "bms_live",
    ),
    "bms_voltage": (lambda c: c.device.bms_live.bms_voltage, "bms_live"),
    "bms_current": (lambda c: c.device.bms_live.bms_current, "bms_live"),
    "bms_ambient_temp": (lambda c: c.device.bms_live.bms_ambient_temp, "bms_live"),
    "bms_soc": (lambda c: c.device.bms_live.bms_soc, "bms_live"),
    "bms_max_temp": (lambda c: c.device.bms_live.bms_max_temp, "bms_live"),
    "bms_min_temp": (lambda c: c.device.bms_live.bms_min_temp, "bms_live"),
    "bms_max_cell_voltage": (
        lambda c: c.device.bms_live.bms_max_cell_voltage,
        "bms_live",
    ),
    "bms_min_cell_voltage": (
        lambda c: c.device.bms_live.bms_min_cell_voltage,
        "bms_live",
    ),
    "bms_soh": (lambda c: c.device.bms_live.bms_soh, "bms_live"),
    "bms_fault_1": (lambda c: c.device.bms_live.bms_fault_1, "bms_live"),
    "bms_fault_2": (lambda c: c.device.bms_live.bms_fault_2, "bms_live"),
    "bms_fault_3": (lambda c: c.device.bms_live.bms_fault_3, "bms_live"),
    "bms_fault_4": (lambda c: c.device.bms_live.bms_fault_4, "bms_live"),
    "bms_fault_5": (lambda c: c.device.bms_live.bms_fault_5, "bms_live"),
    "bms_fault_6": (lambda c: c.device.bms_live.bms_fault_6, "bms_live"),
    "bms_remain_energy": (
        lambda c: c.device.bms_live.bms_remain_energy,
        "bms_live",
    ),
    "bms_fcc_capacity": (
        lambda c: c.device.bms_live.bms_fcc_capacity,
        "bms_live",
    ),
    "meter_connection_status": (
        lambda c: c.device.meter.meter_connection_status,
        "meter",
    ),
    "r_phase_voltage": (lambda c: c.device.meter.r_phase_voltage, "meter"),
    "s_phase_voltage": (lambda c: c.device.meter.s_phase_voltage, "meter"),
    "t_phase_voltage": (lambda c: c.device.meter.t_phase_voltage, "meter"),
    "r_phase_current": (lambda c: c.device.meter.r_phase_current, "meter"),
    "s_phase_current": (lambda c: c.device.meter.s_phase_current, "meter"),
    "t_phase_current": (lambda c: c.device.meter.t_phase_current, "meter"),
    "combined_active_power": (
        lambda c: c.device.meter.combined_active_power,
        "meter",
    ),
    "inverter_status_1": (lambda c: c.inverter_status_1, "inverter_live"),
    "inverter_status_3": (lambda c: c.inverter_status_3, "inverter_live"),
    "alarm_1": (lambda c: c.alarm_1, "inverter_live"),
    "alarm_2": (lambda c: c.alarm_2, "inverter_live"),
    "alarm_3": (lambda c: c.alarm_3, "inverter_live"),
    "grid_r_voltage": (
        lambda c: c.device.inverter_live.grid_r_voltage,
        "inverter_live",
    ),
    "grid_s_voltage": (
        lambda c: c.device.inverter_live.grid_s_voltage,
        "inverter_live",
    ),
    "grid_t_voltage": (
        lambda c: c.device.inverter_live.grid_t_voltage,
        "inverter_live",
    ),
    "active_power": (lambda c: c.device.inverter_live.active_power, "inverter_live"),
    "reactive_power": (
        lambda c: c.device.inverter_live.reactive_power,
        "inverter_live",
    ),
    "power_factor": (lambda c: c.device.inverter_live.power_factor, "inverter_live"),
    "grid_frequency": (
        lambda c: c.device.inverter_live.grid_frequency,
        "inverter_live",
    ),
    "inverter_temp": (
        lambda c: c.device.inverter_live.inverter_temp,
        "inverter_live",
    ),
    "grid_power_meter": (
        lambda c: c.device.powerflow.grid_power_meter,
        "powerflow",
    ),
    "eps_power": (lambda c: c.device.powerflow.eps_power, "powerflow"),
    "load_power": (lambda c: c.device.powerflow.load_power, "powerflow"),
    "battery_power": (lambda c: c.device.powerflow.battery_power, "powerflow"),
    "system_soc": (lambda c: c.device.powerflow.system_soc, "powerflow"),
    "battery_charge_total": (
        lambda c: c.device.energy.battery_charge_total,
        "energy",
    ),
    "battery_charge_today": (
        lambda c: c.device.energy.battery_charge_today,
        "energy",
    ),
    "battery_discharge_total": (
        lambda c: c.device.energy.battery_discharge_total,
        "energy",
    ),
    "battery_discharge_today": (
        lambda c: c.device.energy.battery_discharge_today,
        "energy",
    ),
    "grid_export_total": (lambda c: c.device.energy.grid_export_total, "energy"),
    "grid_export_today": (lambda c: c.device.energy.grid_export_today, "energy"),
    "grid_import_total": (lambda c: c.device.energy.grid_import_total, "energy"),
    "grid_import_today": (lambda c: c.device.energy.grid_import_today, "energy"),
    "output_energy_total": (
        lambda c: c.device.energy.output_energy_total,
        "energy",
    ),
    "output_energy_today": (
        lambda c: c.device.energy.output_energy_today,
        "energy",
    ),
    "input_energy_total": (
        lambda c: c.device.energy.input_energy_total,
        "energy",
    ),
    "input_energy_today": (
        lambda c: c.device.energy.input_energy_today,
        "energy",
    ),
    "total_load_power": (lambda c: c.device.energy.total_load_power, "energy"),
    "total_load_power_today": (
        lambda c: c.device.energy.total_load_power_today,
        "energy",
    ),
    "min_soc": (lambda c: c.device.settings.min_soc, "settings"),
    "max_soc": (lambda c: c.device.settings.max_soc, "settings"),
    "min_soc_ongrid": (lambda c: c.device.settings.min_soc_ongrid, "settings"),
    "work_mode": (lambda c: c.work_mode, "settings"),
    "system_power_state": (lambda c: c.system_power_state, "settings"),
    "network_status": (lambda c: c.network_status, "settings"),
    # Derived power splits.
    "battery_charging": (lambda c: c.battery_charging, "powerflow"),
    "battery_discharging": (lambda c: c.battery_discharging, "powerflow"),
    "grid_import": (lambda c: c.grid_import, "powerflow"),
    "grid_export": (lambda c: c.grid_export, "powerflow"),
}

DERIVED_META = {
    "battery_charging": (
        "Battery Charging",
        UnitOfPower.WATT,
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
        "mdi:battery-plus-outline",
    ),
    "battery_discharging": (
        "Battery Discharging",
        UnitOfPower.WATT,
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
        "mdi:battery-minus-outline",
    ),
    "grid_import": (
        "Grid Import",
        UnitOfPower.WATT,
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
        "mdi:transmission-tower-import",
    ),
    "grid_export": (
        "Grid Export",
        UnitOfPower.WATT,
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
        "mdi:transmission-tower-export",
    ),
}

# Long-term statistics stay available when the device is offline.
STATISTICS_STATE_CLASSES = (
    SensorStateClass.TOTAL,
    SensorStateClass.TOTAL_INCREASING,
)


# Components polled on the slow settings interval; everything else reads the
# fast readings coordinator. Value functions only touch the shared device, so
# either coordinator serves them — availability is what differs.
SETTINGS_COMPONENTS = frozenset({"settings"})


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    readings, settings = hass.data[DOMAIN][entry.entry_id]
    prefix = readings.prefix
    absent = readings.absent_components | settings.absent_components

    pending: list[
        tuple[NextEnergyDataCoordinator, NextEnergySensorEntityDescription]
    ] = []
    for key, (name, _, _, unit, device_class, state_class, _, _, icon) in SENSORS.items():
        if key not in SENSOR_VALUES:
            continue
        _, component = SENSOR_VALUES[key]
        if component in absent:
            continue
        pending.append((
            settings if component in SETTINGS_COMPONENTS else readings,
            NextEnergySensorEntityDescription(
                key=f"{prefix}_{key}",
                name=name,
                native_unit_of_measurement=unit,
                device_class=device_class,
                state_class=state_class,
                entity_registry_enabled_default=key not in DISABLED_BY_DEFAULT,
                icon=icon,
                value_fn=SENSOR_VALUES[key][0],
                component=component,
            ),
        ))

    for key, (name, unit, device_class, state_class, icon) in DERIVED_META.items():
        value_fn, component = SENSOR_VALUES[key]
        if component in absent:
            continue
        pending.append((
            settings if component in SETTINGS_COMPONENTS else readings,
            NextEnergySensorEntityDescription(
                key=f"{prefix}_{key}",
                name=name,
                native_unit_of_measurement=unit,
                device_class=device_class,
                state_class=state_class,
                icon=icon,
                value_fn=value_fn,
                component=component,
            ),
        ))

    async_add_entities(
        (
            NextEnergyTotalSensor
            if description.state_class in STATISTICS_STATE_CLASSES
            else NextEnergySensor
        )(coordinator=coordinator, entity_description=description)
        for coordinator, description in pending
    )


class NextEnergySensor(
    CoordinatorEntity[NextEnergyDataCoordinator], SensorEntity
):
    """Representation of a NextEnergy Battery sensor."""

    entity_description: NextEnergySensorEntityDescription

    def __init__(
        self,
        coordinator: NextEnergyDataCoordinator,
        entity_description: NextEnergySensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self.entity_id = f"sensor.{entity_description.key}"
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        )
        self._attr_device_info = coordinator.device_info

    @property
    def available(self) -> bool:
        """Whether the last poll refreshed the value behind this entity."""
        return (
            super().available
            and self.entity_description.component
            not in self.coordinator.failed_components
        )

    @property
    def native_value(self) -> float | int | str | None:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator)

    @property
    def icon(self) -> str | None:
        """Return the icon of the sensor."""
        unprefixed_key = self.entity_description.key.replace(
            f"{self.coordinator.prefix}_", "", 1
        )

        if unprefixed_key in ["system_soc", "bms_soc"]:
            value = self.entity_description.value_fn(self.coordinator)
            if value is None:
                return "mdi:battery-unknown"

            rounded_value = int(round(value / 10)) * 10

            if rounded_value == 100:
                if (self.coordinator.device.powerflow.battery_power or 0) > 0:
                    return "mdi:battery-charging-100"
                return "mdi:battery"
            if rounded_value == 0:
                return "mdi:battery-outline"

            return f"mdi:battery-{rounded_value}"

        return self.entity_description.icon


class NextEnergyTotalSensor(NextEnergySensor, RestoreSensor):
    """A long-term statistic: it holds its last value while offline."""

    @property
    def available(self) -> bool:
        """A total stays available even when nothing answered the poll."""
        return True

    async def async_added_to_hass(self) -> None:
        """Seed the total from the state it had before the restart."""
        await super().async_added_to_hass()
        if (last_data := await self.async_get_last_sensor_data()) is not None:
            self._attr_native_value = last_data.native_value
        self._process_data()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Take this poll's value before publishing the state."""
        self._process_data()
        super()._handle_coordinator_update()

    def _process_data(self) -> None:
        """Store what the device now reads, keeping the last value if empty."""
        value = self.entity_description.value_fn(self.coordinator)
        if value is None:
            return
        last = self._attr_native_value
        if (
            self.entity_description.state_class is SensorStateClass.TOTAL_INCREASING
            and isinstance(last, (int, float))
            and isinstance(value, (int, float))
            and last * 0.99 <= value < last
        ):
            return  # ignore firmware issue causing minor decrease
        self._attr_native_value = value
