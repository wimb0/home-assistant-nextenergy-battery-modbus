"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import (
    UnitOfPower,
)

from .const import DOMAIN, SENSORS
from .coordinator import NextEnergyDataCoordinator


DISABLED_BY_DEFAULT = [
    "serial_number",
    "master_version",
    "slave_version",
    "manager_version",
    "bms_master_version",
    "bms_master_sn",
    "bms_slave_1_version",
    "bms_slave_1_sn",
    "bms_slave_2_version",
    "bms_slave_2_sn",
    "bms_slave_3_version",
    "bms_slave_3_sn",
    "bms_slave_4_version",
    "bms_slave_4_sn",
    "bms_slave_5_version",
    "bms_slave_5_sn",
    "bms_connection_status",
    "meter_connection_status",
    "r_phase_voltage",
    "s_phase_voltage",
    "t_phase_voltage",
    "r_phase_current",
    "s_phase_current",
    "t_phase_current",
    "grid_r_voltage",
    "grid_s_voltage",
    "grid_t_voltage",
    "rated_power",
    "max_active_power",
    "status",
    "eps_power",
    "reactive_power",
]


ENTITY_DESCRIPTIONS = []
for key, (name, _, _, unit, device_class, state_class, _, _) in SENSORS.items():
    enabled_by_default = key not in DISABLED_BY_DEFAULT
    ENTITY_DESCRIPTIONS.append(
        SensorEntityDescription(
            key=key,
            name=name,
            native_unit_of_measurement=unit,
            device_class=device_class,
            state_class=state_class,
            entity_registry_enabled_default=enabled_by_default,
        )
    )

ENTITY_DESCRIPTIONS.extend([
    SensorEntityDescription(
        key="battery_charging",
        name="Battery Charging",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="battery_discharging",
        name="Battery Discharging",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="grid_import",
        name="Grid Import",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="grid_export",
        name="Grid Export",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
])


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        NextEnergySensor(coordinator=coordinator, entity_description=entity_description)
        for entity_description in entity_descriptions
    )


class NextEnergySensor(CoordinatorEntity[NextEnergyDataCoordinator], SensorEntity):
    """Representation of a NextEnergy Battery sensor."""

    def __init__(
        self,
        coordinator: NextEnergyDataCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.config_entry.entry_id)},
            "name": "NextEnergy Battery",
            "manufacturer": "NextEnergy",
            "model": coordinator.data.get("model_name"),
            "sw_version": coordinator.data.get("master_version"),
            "serial_number": coordinator.data.get("serial_number"),
        }

    @property
    def native_value(self) -> float | int | str | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get(self.entity_description.key)
