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

from .const import DOMAIN, SENSORS, DISABLED_BY_DEFAULT, MANUFACTURER
from .coordinator import NextEnergyDataCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: NextEnergyDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[NextEnergySensor] = []

    for key, (register, scale, unit, device_class, state_class, is_string, register_count, entity_category) in SENSORS.items():
        enabled_by_default = key not in DISABLED_BY_DEFAULT
        description = SensorEntityDescription(
            key=key,
            translation_key=key,
            native_unit_of_measurement=unit,
            device_class=device_class,
            state_class=state_class,
            entity_registry_enabled_default=enabled_by_default,
            entity_category=entity_category,
        )
        entities.append(NextEnergySensor(coordinator, description))

    # Add derived sensors
    derived_sensors = [
        SensorEntityDescription(
            key="battery_charging",
            translation_key="battery_charging",
            native_unit_of_measurement=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        SensorEntityDescription(
            key="battery_discharging",
            translation_key="battery_discharging",
            native_unit_of_measurement=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        SensorEntityDescription(
            key="grid_import",
            translation_key="grid_import",
            native_unit_of_measurement=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        SensorEntityDescription(
            key="grid_export",
            translation_key="grid_export",
            native_unit_of_measurement=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
        ),
    ]

    for description in derived_sensors:
        entities.append(NextEnergySensor(coordinator, description))

    async_add_entities(entities)


class NextEnergySensor(CoordinatorEntity[NextEnergyDataCoordinator], SensorEntity):
    """Representation of a NextEnergy Battery sensor."""

    entity_description: SensorEntityDescription

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
            "name": coordinator.prefix,
            "manufacturer": MANUFACTURER,
            "model": coordinator.data.get("model_name"),
            "sw_version": coordinator.data.get("master_version"),
            "serial_number": coordinator.data.get("serial_number"),
        }

    @property
    def native_value(self) -> float | int | str | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get(self.entity_description.key)