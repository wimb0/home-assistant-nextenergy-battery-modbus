"""Global fixtures for NextEnergy Battery tests."""
from unittest.mock import patch

import pytest

from .const import MOCK_SERIAL, seed_discharge


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Auto enable custom integrations."""
    yield


@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture():
    """Skip notification calls."""
    yield


@pytest.fixture(name="mock_connection")
def mock_connection_fixture(mock_modbus_connection):
    """Patch the TCP connection factory onto the in-memory mock backend."""
    with patch(
        "custom_components.nextenergy_battery.create_connection",
        return_value=mock_modbus_connection,
    ):
        yield mock_modbus_connection


@pytest.fixture(name="mock_device")
def mock_device_fixture(mock_connection, mock_modbus_unit):
    """Patch the connection and seed a discharging battery."""
    seed_discharge(mock_modbus_unit)
    yield mock_connection


@pytest.fixture(name="mock_probe")
def mock_probe_fixture():
    """Patch the config-flow probe to report a fixed serial."""
    with patch(
        "custom_components.nextenergy_battery.config_flow.async_probe",
        return_value=MOCK_SERIAL,
    ) as probe:
        yield probe
