"""Global fixtures for NextEnergy Battery tests."""
import pytest
from unittest.mock import patch

from .const import MOCK_STATIC_DATA, MOCK_DYNAMIC_DATA

@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Auto enable custom integrations."""
    yield

@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture():
    """Skip notification calls."""
    yield

# This fixture mocks the Modbus client's read_sensors method
@pytest.fixture(name="bypass_get_data")
def bypass_get_data_fixture():
    """Skip calls to the API."""
    with patch(
        "custom_components.nextenergy_battery.modbus.NextEnergyModbusClient.read_sensors"
    ) as mock_read_sensors:
        # Separate mocks for the one-time static read and the polled dynamic reads
        mock_read_sensors.side_effect = [
            MOCK_STATIC_DATA,
            MOCK_DYNAMIC_DATA,
            MOCK_DYNAMIC_DATA,
        ]
        yield mock_read_sensors
