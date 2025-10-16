"""Constants for NextEnergy Battery tests."""

MOCK_CONFIG = {
    "host": "1.2.3.4",
    "port": 502,
    "slave_id": 1,
    "polling_interval": 30,
    "prefix": "test_prefix",
}

MOCK_STATIC_DATA = {
    "model_name": "MQ2200-M-A",
    "serial_number": "TEST_SN_12345",
    "master_version": "1.2.3",
}

MOCK_DYNAMIC_DATA_DISCHARGE = {
    "system_soc": 85,
    "battery_power": -550, "grid_power_meter": 200,
    "inverter_status_1": 4, "inverter_status_3": 0,
    "alarm_1": 0, "alarm_2": 4, "alarm_3": 0,
    "work_mode": 1,
}

MOCK_DYNAMIC_DATA_CHARGE = {
    "system_soc": 50,
    "battery_power": 750, "grid_power_meter": -1500,
    "inverter_status_1": 4, "inverter_status_3": 0,
    "alarm_1": 0, "alarm_2": 0, "alarm_3": 0,
    "work_mode": 6,
}

