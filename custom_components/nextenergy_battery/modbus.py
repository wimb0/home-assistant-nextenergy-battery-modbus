
"""Modbus communication for NextEnergy Battery."""
import logging

from pymodbus.client.sync import ModbusTcpClient

from pymodbus.exceptions import ConnectionException

_LOGGER = logging.getLogger(__name__)


class NextEnergyModbusClient:
    """A client for communicating with a NextEnergy Battery via Modbus."""

    def __init__(self, host, port, slave_id):
        """Initialize the client."""
        self._host = host
        self._port = port
        self._slave_id = slave_id
        self._client = ModbusTcpClient(host, port)

    def connect(self):
        """Connect to the Modbus device."""
        _LOGGER.info(f"Connecting to Modbus device at {self._host}:{self._port}")
        return self._client.connect()

    def close(self):
        """Close the connection to the Modbus device."""
        _LOGGER.info("Closing connection to Modbus device.")
        self._client.close()

    def read_register(self, address, count=1):
        """Read a register from the Modbus device."""
        if not self._client.is_socket_open():
            _LOGGER.warning("Modbus client is not connected. Reconnecting...")
            if not self.connect():
                _LOGGER.error("Failed to reconnect to Modbus device.")
                return None

        _LOGGER.debug(f"Reading {count} registers from address {address}")
        try:
            return self._client.read_holding_registers(address, count, unit=self._slave_id)
        except ConnectionException as e:
            _LOGGER.error(f"Error reading register {address}: {e}")
            return None
