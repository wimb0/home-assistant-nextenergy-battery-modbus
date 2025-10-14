"""Constants for NextEnergy Battery tests."""

MOCK_CONFIG = {
    "host": "1.2.3.4",
    "port": 502,
    "slave_id": 1,
    "polling_interval": 30,
    "prefix": "test_prefix",
}

# Mock data representing the raw values from the battery
MOCK_STATIC_DATA = {
    "model_name": "MQ2200-M-A",
    "serial_number": "TEST_SN_12345",
    "master_version": "1.2.3",
}

MOCK_DYNAMIC_DATA = {
    "system_soc": 85,
    "battery_power": -550,  # Discharging
    "grid_power_meter": 200,  # Importing
    "inverter_status_1": 2,  # Operation
    "inverter_status_3": 0,  # On-grid
    "alarm_1": 0,
    "alarm_2": 2, # Low insulation resistance
    "alarm_3": 0,
}
