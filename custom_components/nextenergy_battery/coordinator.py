"""Data coordinator for the NextEnergy Battery integration."""
import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .modbus import NextEnergyModbusClient

_LOGGER = logging.getLogger(__name__)


class NextEnergyDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the inverter."""

    def __init__(self, hass, client: NextEnergyModbusClient, polling_interval: int):
        """Initialize."""
        self.client = client
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=polling_interval),
        )

    async def _async_update_data(self):
        """Fetch data from the inverter.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        data = await self.client.async_read_all_sensors()

        # Split battery power into charging and discharging
        if data and "battery_power" in data and data["battery_power"] is not None:
            battery_power = data["battery_power"]
            if battery_power > 0:
                data["battery_charging"] = battery_power
                data["battery_discharging"] = 0
            else:
                data["battery_charging"] = 0
                data["battery_discharging"] = abs(battery_power)
        else:
            data["battery_charging"] = None
            data["battery_discharging"] = None

        # Split grid power into import and export
        if data and "grid_power_meter" in data and data["grid_power_meter"] is not None:
            grid_power = data["grid_power_meter"]
            if grid_power > 0:
                data["grid_import"] = grid_power
                data["grid_export"] = 0
            else:
                data["grid_import"] = 0
                data["grid_export"] = abs(grid_power)
        else:
            data["grid_import"] = None
            data["grid_export"] = None

        return data