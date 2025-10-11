"""Modbus communication for NextEnergy Battery."""
import logging
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

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
        
        result = self._client.read_holding_registers(address=address, count=count, device_id=self._slave_id)
        if result.isError():
            _LOGGER.debug(f"Error reading sensor {name}: {result}")
            return None

        registers = result.registers
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
            # Handle unsigned 32-bit integers (adjust if signed is needed)
            raw_value = (registers[0] << 16) | registers[1]
        else:
            # For other counts, return raw list for now
            return registers

        return raw_value * scale

    def read_all_sensors(self):
        """Read all sensor values from the Modbus device."""
        if not self._client.is_socket_open():
            self.connect()

        data = {}
        for sensor_key in SENSORS:
            try:
                data[sensor_key] = self.read_sensor(sensor_key)
            except Exception as e:
                _LOGGER.error(f"Error reading sensor {sensor_key}: {e}")
                data[sensor_key] = None
        return data