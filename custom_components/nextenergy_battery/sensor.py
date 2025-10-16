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
from homeassistant.const import UnitOfPower

from .const import DOMAIN, SENSORS, DISABLED_BY_DEFAULT, MANUFACTURER
from .coordinator import NextEnergyDataCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    prefix = coordinator.prefix

    entity_descriptions = []
    for key, (name, _, _, unit, device_class, state_class, _, _, icon) in SENSORS.items():
        enabled_by_default = key not in DISABLED_BY_DEFAULT
        entity_descriptions.append(
            SensorEntityDescription(
                key=f"{prefix}_{key}",
                name=name,
                native_unit_of_measurement=unit,
                device_class=device_class,
                state_class=state_class,
                entity_registry_enabled_default=enabled_by_default,
                icon=icon,  # <-- Statisch icoon hier toegevoegd
            )
        )

    entity_descriptions.extend([
        SensorEntityDescription(
            key=f"{prefix}_battery_charging",
            name="Battery Charging",
            native_unit_of_measurement=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:battery-plus-outline",
        ),
        SensorEntityDescription(
            key=f"{prefix}_battery_discharging",
            name="Battery Discharging",
            native_unit_of_measurement=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:battery-minus-outline",
        ),
        SensorEntityDescription(
            key=f"{prefix}_grid_import",
            name="Grid Import",
            native_unit_of_measurement=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:transmission-tower-import",
        ),
        SensorEntityDescription(
            key=f"{prefix}_grid_export",
            name="Grid Export",
            native_unit_of_measurement=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:transmission-tower-export",
        ),
    ])

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
        self.entity_id = f"sensor.{entity_description.key}"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.config_entry.entry_id)},
            "name": f"{MANUFACTURER} Battery",
            "manufacturer": MANUFACTURER,
            "model": coordinator.data.get("model_name"),
            "sw_version": coordinator.data.get("master_version"),
            "serial_number": coordinator.data.get("serial_number"),
        }

    @property
    def native_value(self) -> float | int | str | None:
        """Return the state of the sensor."""
        unprefixed_key = self.entity_description.key.replace(f"{self.coordinator.prefix}_", "", 1)
        return self.coordinator.data.get(unprefixed_key)

    @property
    def icon(self) -> str | None:
        """Return the icon of the sensor."""
        unprefixed_key = self.entity_description.key.replace(f"{self.coordinator.prefix}_", "", 1)
        
        # --- VOORBEELD VAN DYNAMISCHE ICONEN ---
        if unprefixed_key in ["system_soc", "bms_soc"]:
            value = self.coordinator.data.get(unprefixed_key)
            if value is None:
                return "mdi:battery-unknown"
            
            # Rond de waarde af naar het dichtstbijzijnde tiental
            rounded_value = int(round(value / 10)) * 10
            
            if rounded_value == 100:
                # Als de batterij aan het opladen is, toon een oplaadicoon
                if self.coordinator.data.get("battery_power", 0) > 0:
                    return "mdi:battery-charging-100"
                return "mdi:battery"
            if rounded_value == 0:
                 return "mdi:battery-outline"

            return f"mdi:battery-{rounded_value}"
            
        # Voor alle andere sensoren, gebruik het statische icoon
        return self.entity_description.icon
