"""Modbus communication for NextEnergy Battery."""
import logging
import struct
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

from .const import SENSORS

_LOGGER = logging.getLogger(__name__)


class NextEnergyModbusClient:
    """A client for communicating with a NextEnergy Battery via Modbus."""

    def __init__(self, host, port, slave_id):
        """Initialize the client."""
        self._host = host
        self._port = port
        self._slave_id = slave_id
        self._client = ModbusTcpClient(host, port)

    async def async_connect(self):
        """Connect to the Modbus device."""
        _LOGGER.info(f"Connecting to Modbus device at {self._host}:{self._port}")
        return await self._client.connect()

    def close(self):
        """Close the connection to the Modbus device."""
        _LOGGER.info("Closing connection to Modbus device.")
        self._client.close()

    async def async_read_sensor(self, sensor_key):
        """Read a sensor value from the Modbus device."""
        if not self._client.is_connected():
            _LOGGER.warning("Modbus client is not connected. Reconnecting...")
            if not await self.async_connect():
                _LOGGER.error("Failed to reconnect to Modbus device.")
                return None

        name, address, scale, unit, device_class, state_class, is_string, count = SENSORS[sensor_key]

        _LOGGER.debug(f"Reading sensor {name} from address {address} with count {count}")
        try:
            result = await self._client.read_holding_registers(address, count, slave=self._slave_id)
            if result.isError():
                _LOGGER.error(f"Error reading sensor {name}: {result}")
                return None

            if is_string:
                decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.BIG)
                return decoder.decode_string(count * 2).rstrip(b'\x00').decode('utf-8')
            
            if count == 1:
                return result.registers[0] * scale
            elif count == 2:
                decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.BIG, wordorder=Endian.LITTLE)
                # Assuming 32-bit integer, check documentation for exact type (e.g., int32, uint32, float32)
                return decoder.decode_32bit_int() * scale
            # Add other multi-register handling here if needed

        except ConnectionException as e:
            _LOGGER.error(f"Error reading sensor {name}: {e}")
            return None
        return None

    async def async_read_all_sensors(self):
        """Read all sensor values from the Modbus device."""
        data = {}
        for sensor_key in SENSORS:
            data[sensor_key] = await self.async_read_sensor(sensor_key)
        return data