"""Platform for sensor integration."""
from datetime import timedelta

from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass

from .const import DOMAIN, REGISTER_ADDRESSES, SCALING_FACTORS
from .modbus import NextEnergyModbusClient


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the sensor platform."""
    host = config_entry.data["host"]
    port = config_entry.data["port"]
    slave_id = config_entry.data["slave_id"]
    polling_interval = config_entry.options.get("polling_interval", 30)

    client = NextEnergyModbusClient(host, port, slave_id)
    client.connect()

    sensors = [
        NextEnergySensor(
            client,
            config_entry,
            "SoC",
            "soc",
            "%",
            SensorDeviceClass.BATTERY,
            SensorStateClass.MEASUREMENT,
        ),
        NextEnergySensor(
            client,
            config_entry,
            "Generation",
            "generation",
            "W",
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
        ),
        NextEnergySensor(
            client,
            config_entry,
            "Consumption",
            "consumption",
            "W",
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
        ),
        NextEnergySensor(
            client,
            config_entry,
            "Grid",
            "grid",
            "W",
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
        ),
        NextEnergySensor(
            client,
            config_entry,
            "Battery Charging",
            "battery_charging",
            "W",
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
        ),
        NextEnergySensor(
            client,
            config_entry,
            "Battery Discharging",
            "battery_discharging",
            "W",
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
        ),
        NextEnergySensor(
            client,
            config_entry,
            "Grid Export",
            "grid_export",
            "W",
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
        ),
        NextEnergySensor(
            client,
            config_entry,
            "Grid Import",
            "grid_import",
            "W",
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
        ),
        NextEnergySensor(
            client,
            config_entry,
            "Grid Frequency",
            "grid_frequency",
            "Hz",
            SensorDeviceClass.FREQUENCY,
            SensorStateClass.MEASUREMENT,
        ),
        NextEnergySensor(
            client,
            config_entry,
            "Battery Temp",
            "battery_temp",
            "°C",
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        NextEnergySensor(
            client,
            config_entry,
            "Inverter Temp",
            "inverter_temp",
            "°C",
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        NextEnergySensor(
            client,
            config_entry,
            "Today's Generation",
            "todays_generation",
            "kWh",
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL_INCREASING,
        ),
        NextEnergySensor(
            client,
            config_entry,
            "Cumulative Generation",
            "cumulative_generation",
            "kWh",
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL_INCREASING,
        ),
        NextEnergySensor(
            client,
            config_entry,
            "Today's Load Consumption",
            "todays_load_consumption",
            "kWh",
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL_INCREASING,
        ),
        NextEnergySensor(
            client,
            config_entry,
            "Total Load Consumption",
            "total_load_consumption",
            "kWh",
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL_INCREASING,
        ),
        NextEnergySensor(
            client,
            config_entry,
            "Today's Grid Export",
            "todays_grid_export",
            "kWh",
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL_INCREASING,
        ),
        NextEnergySensor(
            client,
            config_entry,
            "Total Grid Export",
            "total_grid_export",
            "kWh",
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL_INCREASING,
        ),
        NextEnergySensor(
            client,
            config_entry,
            "Today's Grid Import",
            "todays_grid_import",
            "kWh",
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL_INCREASING,
        ),
        NextEnergySensor(
            client,
            config_entry,
            "Total Grid Import",
            "total_grid_import",
            "kWh",
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL_INCREASING,
        ),
        NextEnergySensor(
            client,
            config_entry,
            "Today's Battery Charge",
            "todays_battery_charge",
            "kWh",
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL_INCREASING,
        ),
        NextEnergySensor(
            client,
            config_entry,
            "Total Battery Charge",
            "total_battery_charge",
            "kWh",
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL_INCREASING,
        ),
        NextEnergySensor(
            client,
            config_entry,
            "Today's Battery Discharge",
            "todays_battery_discharge",
            "kWh",
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL_INCREASING,
        ),
        NextEnergySensor(
            client,
            config_entry,
            "Total Battery Discharge",
            "total_battery_discharge",
            "kWh",
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL_INCREASING,
        ),
    ]

    async_add_entities(sensors, update_before_add=True)


class NextEnergySensor(Entity):
    """Representation of a NextEnergy Battery sensor."""

    def __init__(
        self,
        client,
        config_entry,
        name,
        register_name,
        unit_of_measurement,
        device_class,
        state_class,
    ):
        """Initialize the sensor."""
        self._client = client
        self._config_entry = config_entry
        self._name = name
        self._register_name = register_name
        self._unit_of_measurement = unit_of_measurement
        self._device_class = device_class
        self._state_class = state_class
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"NextEnergy {self._name}"

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self._config_entry.entry_id}_{self._register_name}"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self._device_class

    @property
    def state_class(self):
        """Return the state class of the sensor."""
        return self._state_class

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "name": "NextEnergy Battery",
            "manufacturer": "NextEnergy",
        }

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    def update(self):
        """Fetch new state data for the sensor."""
        if self._register_name in REGISTER_ADDRESSES:
            address = REGISTER_ADDRESSES[self._register_name]
            result = self._client.read_register(address)
            if result is not None and hasattr(result, 'registers'):
                value = result.registers[0] * SCALING_FACTORS[self._register_name]
                if self._register_name == "battery":
                    if value > 0:
                        self.hass.data[DOMAIN][self._config_entry.entry_id]["battery_charging"] = value
                        self.hass.data[DOMAIN][self._config_entry.entry_id]["battery_discharging"] = 0
                    else:
                        self.hass.data[DOMAIN][self._config_entry.entry_id]["battery_charging"] = 0
                        self.hass.data[DOMAIN][self._config_entry.entry_id]["battery_discharging"] = abs(value)
                elif self._register_name == "grid":
                    if value > 0:
                        self.hass.data[DOMAIN][self._config_entry.entry_id]["grid_import"] = value
                        self.hass.data[DOMAIN][self._config_entry.entry_id]["grid_export"] = 0
                    else:
                        self.hass.data[DOMAIN][self._config_entry.entry_id]["grid_import"] = 0
                        self.hass.data[DOMAIN][self._config_entry.entry_id]["grid_export"] = abs(value)
                else:
                    self._state = value
            else:
                self._state = None
        elif self._register_name == "battery_charging":
            self._state = self.hass.data[DOMAIN].get(self._config_entry.entry_id, {}).get("battery_charging")
        elif self._register_name == "battery_discharging":
            self._state = self.hass.data[DOMAIN].get(self._config_entry.entry_id, {}).get("battery_discharging")
        elif self._register_name == "grid_import":
            self._state = self.hass.data[DOMAIN].get(self._config_entry.entry_id, {}).get("grid_import")
        elif self._register_name == "grid_export":
            self._state = self.hass.data[DOMAIN].get(self._config_entry.entry_id, {}).get("grid_export")

    @property
    def scan_interval(self):
        """Return the scan interval."""
        return timedelta(seconds=self._config_entry.options.get("polling_interval", 30))