"""Constants for the NextEnergy Battery integration."""
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfFrequency,
)

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.helpers.entity import EntityCategory

DOMAIN = "nextenergy_battery"
MANUFACTURER = "NextEnergy"
PLATFORMS = ["sensor", "binary_sensor"]
DEFAULT_POLLING_INTERVAL = 30
CONF_POLLING_INTERVAL = "polling_interval"
CONF_PREFIX = "prefix"
DEFAULT_PREFIX = "nextenergy"
CONF_SLAVE_ID = "slave_id"

# Defines the structure of a sensor, including its register, scale, unit, device class, state class,
# whether it's a string, the number of registers it occupies, and an optional entity category.
# (register, scale, unit, device_class, state_class, is_string, register_count, entity_category)
SENSORS = {
    "model_name": (30000, 1, None, None, None, True, 8, EntityCategory.DIAGNOSTIC),
    "serial_number": (30016, 1, None, None, None, True, 16, EntityCategory.DIAGNOSTIC),
    "master_version": (36001, 1, None, None, None, False, 1, EntityCategory.DIAGNOSTIC),
    "bms_master_version": (37003, 1, None, None, None, False, 1, EntityCategory.DIAGNOSTIC),
    "bms_master_sn": (37005, 1, None, None, None, True, 16, EntityCategory.DIAGNOSTIC),
    "bms_slave_number": (37032, 1, None, None, None, False, 1, EntityCategory.DIAGNOSTIC),
    "bms_slave_1_version": (37033, 1, None, None, None, False, 1, EntityCategory.DIAGNOSTIC),
    "bms_slave_2_version": (37034, 1, None, None, None, False, 1, EntityCategory.DIAGNOSTIC),
    "bms_slave_3_version": (37035, 1, None, None, None, False, 1, EntityCategory.DIAGNOSTIC),
    "bms_slave_4_version": (37036, 1, None, None, None, False, 1, EntityCategory.DIAGNOSTIC),
    "bms_slave_5_version": (37037, 1, None, None, None, False, 1, EntityCategory.DIAGNOSTIC),
    "bms_slave_1_sn": (37097, 1, None, None, None, True, 16, EntityCategory.DIAGNOSTIC),
    "bms_slave_2_sn": (37113, 1, None, None, None, True, 16, EntityCategory.DIAGNOSTIC),
    "bms_slave_3_sn": (37129, 1, None, None, None, True, 16, EntityCategory.DIAGNOSTIC),
    "bms_slave_4_sn": (37145, 1, None, None, None, True, 16, EntityCategory.DIAGNOSTIC),
    "bms_slave_5_sn": (37161, 1, None, None, None, True, 16, EntityCategory.DIAGNOSTIC),
    "bms_voltage": (37609, 0.1, UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, False, 1, None),
    "bms_current": (37610, 0.1, UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT, False, 1, None),
    "bms_ambient_temp": (37611, 0.1, UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, False, 1, None),
    "bms_soc": (37612, 1, "%", SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT, False, 1, None),
    "bms_soh": (37624, 1, "%", None, SensorStateClass.MEASUREMENT, False, 1, None),
    "bms_remain_energy": (37632, 0.1, UnitOfEnergy.WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL, False, 1, None),
    "r_phase_voltage": (38802, 0.1, UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, False, 2, None),
    "s_phase_voltage": (38804, 0.1, UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, False, 2, None),
    "t_phase_voltage": (38806, 0.1, UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, False, 2, None),
    "r_phase_current": (38808, 0.001, UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT, False, 2, None),
    "s_phase_current": (38810, 0.001, UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT, False, 2, None),
    "t_phase_current": (38812, 0.001, UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT, False, 2, None),
    "combined_active_power": (38814, 0.1, UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, False, 2, None),
    "rated_power": (39053, 0.001, UnitOfPower.KILO_WATT, SensorDeviceClass.POWER, None, False, 2, EntityCategory.DIAGNOSTIC),
    "max_active_power": (39055, 0.001, UnitOfPower.KILO_WATT, SensorDeviceClass.POWER, None, False, 2, EntityCategory.DIAGNOSTIC),
    "status": (39063, 1, None, None, None, False, 1, EntityCategory.DIAGNOSTIC),
    "grid_r_voltage": (39123, 0.1, UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, False, 1, None),
    "grid_s_voltage": (39124, 0.1, UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, False, 1, None),
    "grid_t_voltage": (39125, 0.1, UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, False, 1, None),
    "active_power": (39134, 0.001, UnitOfPower.KILO_WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, False, 2, None),
    "reactive_power": (39136, 0.001, "kVar", SensorDeviceClass.REACTIVE_POWER, SensorStateClass.MEASUREMENT, False, 2, None),
    "grid_frequency": (39139, 0.01, UnitOfFrequency.HERTZ, SensorDeviceClass.FREQUENCY, SensorStateClass.MEASUREMENT, False, 1, None),
    "inverter_temp": (39141, 0.1, UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, False, 1, None),
    "grid_power_meter": (39168, 1, UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, False, 2, None),
    "eps_power": (39216, 1, UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, False, 2, None),
    "load_power": (39225, 1, UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, False, 2, None),
    "battery_power": (39237, 1, UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, False, 2, None),
    "system_soc": (39423, 1, "%", SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT, False, 1, None),
    "battery_charge_total": (39605, 0.01, UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, False, 2, None),
    "battery_charge_today": (39607, 0.01, UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, False, 2, None),
    "battery_discharge_total": (39609, 0.01, UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, False, 2, None),
    "battery_discharge_today": (39611, 0.01, UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, False, 2, None),
    "grid_export_total": (39613, 0.01, UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, False, 2, None),
    "grid_export_today": (39615, 0.01, UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, False, 2, None),
    "grid_import_total": (39617, 0.01, UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, False, 2, None),
    "grid_import_today": (39619, 0.01, UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, False, 2, None),
}

BINARY_SENSORS = {
    "bms_connection_status": (37002, BinarySensorDeviceClass.CONNECTIVITY, EntityCategory.DIAGNOSTIC),
    "meter_connection_status": (38801, BinarySensorDeviceClass.CONNECTIVITY, EntityCategory.DIAGNOSTIC),
}

DISABLED_BY_DEFAULT = [
    "serial_number",
    "master_version",
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
    "eps_power",
    "reactive_power",
]