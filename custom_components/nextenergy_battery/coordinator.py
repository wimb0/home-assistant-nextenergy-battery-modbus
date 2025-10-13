# In custom_components/nextenergy_battery/coordinator.py

"""Data coordinator for the NextEnergy Battery integration."""
import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, DYNAMIC_SENSORS
from .modbus import NextEnergyModbusClient

_LOGGER = logging.getLogger(__name__)


class NextEnergyDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the inverter."""

    def __init__(
        self,
        hass,
        client: NextEnergyModbusClient,
        polling_interval: int,
        prefix: str,
    ):
        """Initialize."""
        self.client = client
        self.prefix = prefix
        self.static_data = {}  # Opslag voor statische data
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=polling_interval),
        )

    async def _async_update_data(self):
        """Fetch dynamic data from the inverter."""
        dynamic_data = await self.hass.async_add_executor_job(
            self.client.read_sensors, DYNAMIC_SENSORS.keys()
        )

        # Combineer statische en dynamische data
        data = {**self.static_data, **dynamic_data}

        # Verwerk de gecombineerde data
        if "battery_power" in data and data["battery_power"] is not None:
            battery_power = data["battery_power"]
            data["battery_charging"] = battery_power if battery_power > 0 else 0
            data["battery_discharging"] = abs(battery_power) if battery_power < 0 else 0
        else:
            data["battery_charging"] = None
            data["battery_discharging"] = None

        if "grid_power_meter" in data and data["grid_power_meter"] is not None:
            grid_power = data["grid_power_meter"]
            data["grid_import"] = grid_power if grid_power > 0 else 0
            data["grid_export"] = abs(grid_power) if grid_power < 0 else 0
        else:
            data["grid_import"] = None
            data["grid_export"] = None

        return data
