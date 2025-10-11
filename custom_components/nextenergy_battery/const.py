"""Constants for the NextEnergy Battery integration."""

DOMAIN = "nextenergy_battery"
PLATFORMS = ["sensor"]

REGISTER_ADDRESSES = {
    "soc": 37612,
    "generation": 39118,
    "consumption": 39225,
    "grid": 39168,
    "battery": 39237,
    "feed_in": 39134,
    "grid_frequency": 39139,
    "battery_temp": 37611,
    "inverter_temp": 39141,
    "todays_generation": 39151,
    "cumulative_generation": 39149,
    "todays_load_consumption": 39631,
    "total_load_consumption": 39629,
    "todays_grid_export": 39615,
    "total_grid_export": 39613,
    "todays_grid_import": 39619,
    "total_grid_import": 39617,
    "todays_battery_charge": 39607,
    "total_battery_charge": 39605,
    "todays_battery_discharge": 39611,
    "total_battery_discharge": 39609,
}

SCALING_FACTORS = {
    "soc": 1,
    "generation": 1000,
    "consumption": 1,
    "grid": 1,
    "battery": 1,
    "feed_in": 1000,
    "grid_frequency": 0.01,
    "battery_temp": 0.1,
    "inverter_temp": 0.1,
    "todays_generation": 0.01,
    "cumulative_generation": 0.01,
    "todays_load_consumption": 0.01,
    "total_load_consumption": 0.01,
    "todays_grid_export": 0.01,
    "total_grid_export": 0.01,
    "todays_grid_import": 0.01,
    "total_grid_import": 0.01,
    "todays_battery_charge": 0.01,
    "total_battery_charge": 0.01,
    "todays_battery_discharge": 0.01,
    "total_battery_discharge": 0.01,
}
