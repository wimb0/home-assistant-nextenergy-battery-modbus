"""Platform for binary sensor integration."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, BINARY_SENSORS, MANUFACTURER
from .coordinator import NextEnergyDataCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor platform."""
    coordinator: NextEnergyDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[NextEnergyBinarySensor] = []

    for key, (register, device_class, entity_category) in BINARY_SENSORS.items():
        description = BinarySensorEntityDescription(
            key=key,
            translation_key=key,
            device_class=device_class,
            entity_category=entity_category,
        )
        entities.append(NextEnergyBinarySensor(coordinator, description))

    async_add_entities(entities)


class NextEnergyBinarySensor(CoordinatorEntity[NextEnergyDataCoordinator], BinarySensorEntity):
    """Representation of a NextEnergy Battery binary sensor."""

    entity_description: BinarySensorEntityDescription

    def __init__(
        self,
        coordinator: NextEnergyDataCoordinator,
        entity_description: BinarySensorEntityDescription,
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
    def is_on(self) -> bool | None:
        """Return the state of the sensor."""
        value = self.coordinator.data.get(self.entity_description.key)
        if value is None:
            return None
        return value == 1
