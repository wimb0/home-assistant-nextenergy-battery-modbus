"""Modbus communication for NextEnergy Battery."""
import logging
import time
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
        self._client = ModbusTcpClient(host=host, port=port, timeout=5, retries=3)

    def connect(self):
        """Connect to the Modbus device."""
        _LOGGER.info(f"Connecting to Modbus device at {self._host}:{self._port}")
        return self._client.connect()

    def close(self):
        """Close the connection to the Modbus device."""
        _LOGGER.info("Closing connection to Modbus device.")
        self._client.close()

    def read_sensor(self, sensor_key):
        """Read a sensor value from the Modbus device."""
        name, address, scale, unit, device_class, state_class, is_string, count = SENSORS[sensor_key]

        _LOGGER.debug(f"Reading sensor {name} from address {address} with count {count}")
        
        result = self._client.read_holding_registers(address=address, count=count, slave=self._slave_id)
        if result.isError():
            _LOGGER.debug(f"Error reading sensor {name}: {result}")
            return None

        registers = result.registers

        # Special handling for version sensors
        if sensor_key in [
            "master_version",
            "bms_master_version",
            "bms_slave_1_version",
            "bms_slave_2_version",
            "bms_slave_3_version",
            "bms_slave_4_version",
            "bms_slave_5_version",
        ]:
            value = registers[0]
            return f"{(value >> 8) & 0xF}.{(value >> 4) & 0xF}.{value & 0xF}"

        if is_string:
            # Manual string decoding
            return "".join(
                chr(registers[i] >> 8) + chr(registers[i] & 0xFF) for i in range(count)
            ).rstrip("\x00")
        
        raw_value = 0
        if count == 1:
            raw_value = registers[0]
            # Handle signed 16-bit integers
            if raw_value >= 0x8000:
                raw_value -= 0x10000
        elif count == 2:
            # Handle signed 32-bit integers
            raw_value = (registers[0] << 16) | registers[1]
            if raw_value >= 0x80000000:
                raw_value -= 0x100000000
        else:
            # For other counts, return raw list for now
            return registers

        return raw_value * scale

    def read_all_sensors(self):
        """Read all sensor values from the Modbus device with retry logic."""
        max_retries = 3
        retry_delay = 5  # seconds

        for attempt in range(max_retries):
            try:
                if not self._client.is_socket_open():
                    _LOGGER.debug("Socket is not open, attempting to connect.")
                    if not self.connect():
                        _LOGGER.warning("Failed to connect to Modbus device on attempt %s.", attempt + 1)
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                            continue
                        raise ConnectionException(f"Failed to connect to {self._host}:{self._port} after multiple retries")

                data = {}
                for sensor_key in SENSORS:
                    data[sensor_key] = self.read_sensor(sensor_key)
                return data  # Return data on success

            except (ConnectionException, ModbusIOException, BrokenPipeError) as e:
                _LOGGER.warning(
                    "Connection error on attempt %s/%s: %s. Retrying in %s seconds...",
                    attempt + 1,
                    max_retries,
                    e,
                    retry_delay,
                )
                self.close()  # Close the broken connection before retrying
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    _LOGGER.error("Failed to read sensors after %s retries.", max_retries)
                    raise  # Re-raise the exception if all retries fail
            except Exception as e:
                _LOGGER.error("An unexpected error occurred while reading sensors: %s", e)
                return {}  # Return empty data to prevent HA from crashing on unexpected errors

        return {}  # Return empty data if all retries fail
