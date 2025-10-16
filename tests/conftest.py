"""Global fixtures for NextEnergy Battery tests."""
import pytest
from unittest.mock import patch

from .const import MOCK_STATIC_DATA, MOCK_DYNAMIC_DATA_DISCHARGE

@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Auto enable custom integrations."""
    yield

@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture():
    """Skip notification calls."""
    yield

@pytest.fixture(name="bypass_get_data")
def bypass_get_data_fixture():
    """Skip calls to the API and return mock data."""
    def mock_read_sensors(sensor_keys):
        if "model_name" in sensor_keys:
            return MOCK_STATIC_DATA
        return MOCK_DYNAMIC_DATA_DISCHARGE

    with patch(
        "custom_components.nextenergy_battery.modbus.NextEnergyModbusClient.read_sensors",
        side_effect=mock_read_sensors,
    ) as mock_api:
        yield mock_api

@pytest.fixture(name="bypass_get_data_empty")
def bypass_get_data_empty_fixture():
    """Simulate a successful static data read, followed by failed dynamic data reads."""
    def mock_read_sensors(sensor_keys):
        if "model_name" in sensor_keys:
            return MOCK_STATIC_DATA
        return {}

    with patch(
        "custom_components.nextenergy_battery.modbus.NextEnergyModbusClient.read_sensors",
        side_effect=mock_read_sensors,
    ) as mock_api:
        yield mock_api
