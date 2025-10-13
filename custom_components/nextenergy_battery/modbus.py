# In custom_components/nextenergy_battery/modbus.py

"""Modbus communication for NextEnergy Battery."""
import logging
import time
from typing import Dict
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException, ModbusIOException

from .const import SENSORS

_LOGGER = logging.getLogger(__name__)


class NextEnergyModbusClient:
    """A client for communicating with a NextEnergy Battery via Modbus."""

    def __init__(self, host, port, slave_id):
        """Initialize the client."""
        self._host = host
        self._port = port
        self._slave_id = slave_id
        self._client = ModbusTcpClient(host=host, port=port, timeout=5)

    def connect(self):
        """Connect to the Modbus device."""
        _LOGGER.debug(f"Connecting to Modbus device at {self._host}:{self._port}")
        return self._client.connect()

    def close(self):
        """Close the connection to the Modbus device."""
        _LOGGER.debug("Closing connection to Modbus device.")
        self._client.close()

    def _read_sensor_value(self, sensor_key):
        """Read a single sensor value from the Modbus device."""
        name, address, scale, unit, device_class, state_class, is_string, count = SENSORS[sensor_key]

        _LOGGER.debug(f"Reading sensor {name} from address {address} with count {count}")
        
        result = self._client.read_holding_registers(address=address, count=count, device_id=self._slave_id)
        if result.isError():
            _LOGGER.debug(f"Error reading sensor {name}: {result}")
            return None

        registers = result.registers

        # Special handling for version sensors
        if sensor_key in [
            "master_version", "bms_master_version", "bms_slave_1_version",
            "bms_slave_2_version", "bms_slave_3_version", "bms_slave_4_version",
            "bms_slave_5_version",
        ]:
            value = registers[0]
            return f"{(value >> 8) & 0xF}.{(value >> 4) & 0xF}.{value & 0xF}"

        if is_string:
            return "".join(
                chr(registers[i] >> 8) + chr(registers[i] & 0xFF) for i in range(count)
            ).rstrip("\x00")
        
        raw_value = 0
        if count == 1:
            raw_value = registers[0]
            if raw_value >= 0x8000: raw_value -= 0x10000
        elif count == 2:
            raw_value = (registers[0] << 16) | registers[1]
            if raw_value >= 0x80000000: raw_value -= 0x100000000
        else:
            return registers

        return raw_value * scale

    def read_sensors(self, sensor_keys: list) -> Dict:
        """Read a specific list of sensor values from the Modbus device with retry logic."""
        max_retries = 3
        retry_delay = 1  # seconds

        for attempt in range(max_retries):
            try:
                self.connect()
                if not self._client.is_socket_open():
                    _LOGGER.warning("Failed to connect to Modbus device on attempt %s.", attempt + 1)
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    raise ConnectionException(f"Failed to connect to {self._host}:{self._port} after retries")

                data = {}
                for sensor_key in sensor_keys:
                    data[sensor_key] = self._read_sensor_value(sensor_key)
                
                return data

            except (ConnectionException, ModbusIOException, BrokenPipeError) as e:
                _LOGGER.warning(
                    "Connection error on attempt %s/%s: %s. Retrying...",
                    attempt + 1, max_retries, e
                )
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    _LOGGER.error("Failed to read sensors after %s retries.", max_retries)
                    raise

            except Exception as e:
                _LOGGER.error("An unexpected error occurred while reading sensors: %s", e)
                return {}

            finally:
                if self._client.is_socket_open():
                    self.close()
        return {}
