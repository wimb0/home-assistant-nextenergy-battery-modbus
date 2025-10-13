"""Data coordinator for the NextEnergy Battery integration."""
import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN, 
    DYNAMIC_SENSORS, 
    ALARM_1_MESSAGES, 
    ALARM_2_MESSAGES, 
    ALARM_3_MESSAGES,
    STATUS_1_MESSAGES,
)
from .modbus import NextEnergyModbusClient
from .util import parse_bitfield_messages

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
        self.static_data = {}
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

        data = {**self.static_data, **dynamic_data}

        if data:
            # Process alarms
            data["alarm_1"] = parse_bitfield_messages(data.get("alarm_1"), ALARM_1_MESSAGES)
            data["alarm_2"] = parse_bitfield_messages(data.get("alarm_2"), ALARM_2_MESSAGES)
            data["alarm_3"] = parse_bitfield_messages(data.get("alarm_3"), ALARM_3_MESSAGES)
            
            # Process statuses
            status1_val = data.get("inverter_status_1")
            data["inverter_status_1"] = parse_bitfield_messages(status1_val, STATUS_1_MESSAGES) if status1_val is not None else "Unknown"

            status3_val = data.get("inverter_status_3")
            if status3_val is not None:
                # Bit 0: 1 = Off-grid, 0 = Not off-grid (On-grid)
                if (status3_val >> 0) & 1:
                    data["inverter_status_3"] = "Off-grid"
                else:
                    data["inverter_status_3"] = "On-grid"
            else:
                data["inverter_status_3"] = "Unknown"

        # Process combined data
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
