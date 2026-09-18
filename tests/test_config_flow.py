"""Test NextEnergy Battery config flow."""
from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import entity_registry as er
from modbus_connection import ModbusError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nextenergy_battery.const import DOMAIN

from .const import MOCK_DATA, MOCK_OPTIONS, MOCK_SERIAL, USER_INPUT


async def test_form_success(
    hass: HomeAssistant, mock_probe, mock_device
) -> None:
    """Test we get the form, probe the battery, and create a serial-keyed entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["data"] == MOCK_DATA
    assert result2["options"] == MOCK_OPTIONS

    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1
    assert entries[0].unique_id == MOCK_SERIAL


async def test_form_cannot_connect(hass: HomeAssistant) -> None:
    """Test the form reports an unreachable battery."""
    with patch(
        "custom_components.nextenergy_battery.config_flow.async_probe",
        side_effect=ModbusError("no connection"),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"], USER_INPUT
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}


async def test_options_flow(hass: HomeAssistant, mock_probe, mock_device) -> None:
    """Test the options flow validates and saves connection settings."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=MOCK_DATA,
        options=MOCK_OPTIONS,
        unique_id=MOCK_SERIAL,
    )
    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM

    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "host": "4.3.2.1",
            "port": 502,
            "slave_id": 1,
            "polling_interval": 60,
            "prefix": "test_prefix",
        },
    )
    assert result2["type"] == FlowResultType.ABORT
    assert result2["reason"] == "reconfigure_successful"
    assert entry.data == {"host": "4.3.2.1", "port": 502, "slave_id": 1}
    assert entry.options == {"polling_interval": 60, "prefix": "test_prefix"}


async def test_options_prefix_migrates_entities(
    hass: HomeAssistant, mock_probe, mock_device
) -> None:
    """Test a prefix change rewrites entity identities instead of orphaning them."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=MOCK_DATA,
        options=MOCK_OPTIONS,
        unique_id=MOCK_SERIAL,
    )
    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    old_unique_id = f"{entry.entry_id}_test_prefix_system_soc"
    assert (
        registry.async_get_entity_id("sensor", DOMAIN, old_unique_id)
        == "sensor.test_prefix_system_soc"
    )

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={**MOCK_DATA, "polling_interval": 30, "prefix": "renamed"},
    )
    assert result2["type"] == FlowResultType.ABORT
    await hass.async_block_till_done()

    new_unique_id = f"{entry.entry_id}_renamed_system_soc"
    assert registry.async_get_entity_id("sensor", DOMAIN, old_unique_id) is None
    assert (
        registry.async_get_entity_id("sensor", DOMAIN, new_unique_id)
        == "sensor.renamed_system_soc"
    )
