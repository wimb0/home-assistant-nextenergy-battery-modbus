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
    UnitOfReactivePower,
)

DOMAIN = "nextenergy_battery"
MANUFACTURER = "NextEnergy"
PLATFORMS = ["sensor"]
DEFAULT_POLLING_INTERVAL = 30
CONF_POLLING_INTERVAL = "polling_interval"
CONF_PREFIX = "prefix"
DEFAULT_PREFIX = "nextenergy"
CONF_SLAVE_ID = "slave_id"

ALARM_1_MESSAGES = {
    0: "Input string voltage is high", 1: "DC arc fault", 2: "String reverse connection",
    7: "Grid power outage", 8: "Abnormal power grid voltage", 11: "Abnormal power grid frequency",
    14: "Output overcurrent", 15: "DC component of output current too large",
}
ALARM_2_MESSAGES = {
    0: "Abnormal residual current", 1: "System grounding abnormality", 2: "Low insulation resistance",
    3: "Temperature is too high", 9: "Energy storage equipment abnormality", 10: "Isolated island",
    14: "Off-grid output overload",
}
ALARM_3_MESSAGES = {
    3: "External fan abnormality", 4: "Energy storage reverse connection", 9: "Meter Lost", 10: "BMS Lost",
}
STATUS_1_MESSAGES = {
    0: "Standby",
    2: "Operation",
    6: "Fault",
}
WORK_MODE_MESSAGES = {
    1: "Self-Use", 2: "Feed-in Priority", 3: "Back-Up",
    4: "Peak Shaving", 6: "Force Charge", 7: "Force Discharge",
}
SYSTEM_POWER_STATE_MESSAGES = {0: "Turn OFF", 1: "Turn ON"}
NETWORK_STATUS_MESSAGES = {0: "Not Connected", 1: "Disconnection", 2: "Connection"}

# Defines the structure of a sensor
# (name, register, scale, unit, device_class, state_class, is_string, register_count, icon)
STATIC_SENSORS = {
    "model_name": ("Model Name", 30000, 1, None, None, None, True, 8, None),
    "serial_number": ("Serial Number", 30016, 1, None, None, None, True, 16, "mdi:numeric"),
    "master_version": ("Master Version", 36001, 1, None, None, None, False, 1, "mdi:chip"),
    "bms_master_version": ("BMS Master Version", 37003, 1, None, None, None, False, 1, "mdi:chip"),
    "bms_master_sn": ("BMS Master Serial Number", 37005, 1, None, None, None, True, 16, "mdi:numeric"),
    "bms_slave_number": ("BMS Slave Number", 37032, 1, None, None, None, False, 1, "mdi:counter"),
    "bms_slave_1_version": ("BMS Slave 1 Version", 37033, 1, None, None, None, False, 1, "mdi:chip"),
    "bms_slave_2_version": ("BMS Slave 2 Version", 37034, 1, None, None, None, False, 1, "mdi:chip"),
    "bms_slave_3_version": ("BMS Slave 3 Version", 37035, 1, None, None, None, False, 1, "mdi:chip"),
    "bms_slave_4_version": ("BMS Slave 4 Version", 37036, 1, None, None, None, False, 1, "mdi:chip"),
    "bms_slave_5_version": ("BMS Slave 5 Version", 37037, 1, None, None, None, False, 1, "mdi:chip"),
    "bms_slave_1_sn": ("BMS Slave 1 SN", 37097, 1, None, None, None, True, 16, "mdi:numeric"),
    "bms_slave_2_sn": ("BMS Slave 2 SN", 37113, 1, None, None, None, True, 16, "mdi:numeric"),
    "bms_slave_3_sn": ("BMS Slave 3 SN", 37129, 1, None, None, None, True, 16, "mdi:numeric"),
    "bms_slave_4_sn": ("BMS Slave 4 SN", 37145, 1, None, None, None, True, 16, "mdi:numeric"),
    "bms_slave_5_sn": ("BMS Slave 5 SN", 37161, 1, None, None, None, True, 16, "mdi:numeric"),
    "bms_design_energy": ("BMS Design Energy", 37635, 0.01, UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, None, False, 1, None),
    "rated_power": ("Rated Power (Pn)", 39053, 0.001, UnitOfPower.KILO_WATT, SensorDeviceClass.POWER, None, False, 2, None),
    "max_active_power": ("Max Active Power (Pmax)", 39055, 0.001, UnitOfPower.KILO_WATT, SensorDeviceClass.POWER, None, False, 2, None),
}

DYNAMIC_SENSORS = {
    "bms_connection_status": ("BMS Connection Status", 37002, 1, None, None, None, False, 1, "mdi:lan-connect"),
    "bms_voltage": ("BMS Voltage", 37609, 0.1, UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, False, 1, None),
    "bms_current": ("BMS Current", 37610, 0.1, UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT, False, 1, None),
    "bms_ambient_temp": ("BMS Ambient Temp", 37611, 0.1, UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, False, 1, None),
    "bms_soc": ("BMS SoC", 37612, 1, "%", SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT, False, 1, None),
    "bms_max_temp": ("BMS Max Temp", 37617, 0.1, UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, False, 1, "mdi:thermometer-chevron-up"),
    "bms_min_temp": ("BMS Min Temp", 37618, 0.1, UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, False, 1, "mdi:thermometer-chevron-down"),
    "bms_max_cell_voltage": ("BMS Max Cell Voltage", 37619, 1, UnitOfElectricPotential.MILLIVOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, False, 1, "mdi:battery-plus-variant"),
    "bms_min_cell_voltage": ("BMS Min Cell Voltage", 37620, 1, UnitOfElectricPotential.MILLIVOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, False, 1, "mdi:battery-minus-variant"),
    "bms_soh": ("BMS SOH", 37624, 1, "%", None, SensorStateClass.MEASUREMENT, False, 1, "mdi:battery-heart-variant"),
    "bms_remain_energy": ("BMS Remain Energy", 37632, 0.01, UnitOfEnergy.KILO_WATT_HOUR, None, SensorStateClass.MEASUREMENT, False, 1, None),
    "bms_fcc_capacity": ("BMS FCC Capacity", 37633, 0.1, f"{UnitOfElectricCurrent.AMPERE}h", None, SensorStateClass.MEASUREMENT, False, 1, "mdi:battery-plus-variant"),
    "meter_connection_status": ("Meter Connection Status", 38801, 1, None, None, None, False, 1, "mdi:lan-connect"),
    "r_phase_voltage": ("R Phase Voltage", 38802, 0.1, UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, False, 2, None),
    "s_phase_voltage": ("S Phase Voltage", 38804, 0.1, UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, False, 2, None),
    "t_phase_voltage": ("T Phase Voltage", 38806, 0.1, UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, False, 2, None),
    "r_phase_current": ("R Phase Current", 38808, 0.001, UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT, False, 2, None),
    "s_phase_current": ("S Phase Current", 38810, 0.001, UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT, False, 2, None),
    "t_phase_current": ("T Phase Current", 38812, 0.001, UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT, False, 2, None),
    "combined_active_power": ("Combined Active Power", 38814, 0.1, UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, False, 2, None),
    "inverter_status_1": ("Inverter Status 1", 39063, 1, None, None, None, False, 1, "mdi:information-outline"),
    "inverter_status_3": ("Inverter Grid Status", 39065, 1, None, None, None, False, 2, "mdi:grid"),
    "alarm_1": ("Alarm Status 1", 39067, 1, None, None, None, False, 1, "mdi:alert-outline"),
    "alarm_2": ("Alarm Status 2", 39068, 1, None, None, None, False, 1, "mdi:alert-outline"),
    "alarm_3": ("Alarm Status 3", 39069, 1, None, None, None, False, 1, "mdi:alert-outline"),
    "grid_r_voltage": ("Grid R Voltage", 39123, 0.1, UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, False, 1, None),
    "grid_s_voltage": ("Grid S Voltage", 39124, 0.1, UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, False, 1, None),
    "grid_t_voltage": ("Grid T Voltage", 39125, 0.1, UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, False, 1, None),
    "active_power": ("Active Power", 39134, 0.001, UnitOfPower.KILO_WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, False, 2, None),
    "reactive_power": ("Reactive Power", 39136, 0.001, UnitOfReactivePower.KILO_VOLT_AMPERE_REACTIVE, SensorDeviceClass.REACTIVE_POWER, SensorStateClass.MEASUREMENT, False, 2, None),
    "power_factor": ("Power Factor", 39138, 0.001, None, SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, False, 1, None),
    "grid_frequency": ("Grid Frequency", 39139, 0.01, UnitOfFrequency.HERTZ, SensorDeviceClass.FREQUENCY, SensorStateClass.MEASUREMENT, False, 1, None),
    "inverter_temp": ("Inverter Temp", 39141, 0.1, UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, False, 1, None),
    "grid_power_meter": ("Grid Power (Meter)", 39168, 1, UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, False, 2, None),
    "eps_power": ("EPS Power", 39216, 1, UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, False, 2, None),
    "load_power": ("Load Power", 39225, 1, UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, False, 2, None),
    "battery_power": ("Battery Power", 39237, 1, UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, False, 2, None),
    "system_soc": ("System SoC", 39423, 1, "%", SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT, False, 1, None),
    "battery_charge_total": ("Battery Charge Total", 39605, 0.01, UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, False, 2, None),
    "battery_charge_today": ("Battery Charge Today", 39607, 0.01, UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, False, 2, None),
    "battery_discharge_total": ("Battery Discharge Total", 39609, 0.01, UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, False, 2, None),
    "battery_discharge_today": ("Battery Discharge Today", 39611, 0.01, UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, False, 2, None),
    "grid_export_total": ("Grid Export Total", 39613, 0.01, UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, False, 2, None),
    "grid_export_today": ("Grid Export Today", 39615, 0.01, UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, False, 2, None),
    "grid_import_total": ("Grid Import Total", 39617, 0.01, UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, False, 2, None),
    "grid_import_today": ("Grid Import Today", 39619, 0.01, UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, False, 2, None),
    "total_load_power": ("Total Load Power", 39629, 0.01, UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, False, 2, None),
    "total_load_power_today": ("Total Load Power Today", 39631, 0.01, UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, False, 2, None),
    "min_soc": ("Minimum SoC", 46609, 1, "%", SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT, False, 1, "mdi:battery-arrow-down-outline"),
    "max_soc": ("Maximum SoC", 46610, 1, "%", SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT, False, 1, "mdi:battery-arrow-up-outline"),
    "min_soc_ongrid": ("Minimum SoC On-Grid", 46611, 1, "%", SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT, False, 1, "mdi:battery-arrow-down-outline"),
    "work_mode": ("Work Mode", 49203, 1, None, None, None, False, 1, "mdi:state-machine"),
    "system_power_state": ("System Power State", 49228, 1, None, None, None, False, 1, "mdi:power"),
    "network_status": ("Network Status", 49242, 1, None, None, None, False, 1, "mdi:lan"),
}

SENSORS = {**STATIC_SENSORS, **DYNAMIC_SENSORS}

DISABLED_BY_DEFAULT = [
    "serial_number", "master_version", "bms_master_version", "bms_master_sn",
    "bms_slave_1_version", "bms_slave_1_sn", "bms_slave_2_version", "bms_slave_2_sn",
    "bms_slave_3_version", "bms_slave_3_sn", "bms_slave_4_version", "bms_slave_4_sn",
    "bms_slave_5_version", "bms_slave_5_sn", "bms_connection_status",
    "meter_connection_status", "r_phase_voltage", "s_phase_voltage",
    "t_phase_voltage", "r_phase_current", "s_phase_current", "t_phase_current",
    "grid_r_voltage", "grid_s_voltage", "grid_t_voltage", "rated_power",
    "max_active_power", "eps_power", "reactive_power", "bms_design_energy",
    "bms_max_temp", "bms_min_temp", "bms_max_cell_voltage", "bms_min_cell_voltage",
    "total_load_power", "bms_fcc_capacity", "system_power_state", "network_status",
    "total_load_power_today", "min_soc", "max_soc", "min_soc_ongrid",
]
