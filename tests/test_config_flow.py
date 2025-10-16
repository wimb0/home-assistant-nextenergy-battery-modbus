"""Test NextEnergy Battery config flow."""
from unittest.mock import patch

import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nextenergy_battery.const import DOMAIN
from .const import MOCK_CONFIG


@pytest.mark.parametrize("user_input", [MOCK_CONFIG])
async def test_form_success(hass: HomeAssistant, user_input, mock_modbus_client) -> None:
    """Test we get the form and it works."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM

    with patch("custom_components.nextenergy_battery.async_setup_entry", return_value=True):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input,
        )
        await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY


async def test_options_flow(hass: HomeAssistant, mock_modbus_client) -> None:
    """Test the options flow."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, options=MOCK_CONFIG)
    entry.add_to_hass(hass)
    
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM

    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"host": "4.3.2.1", "port": 502, "slave_id": 1, "polling_interval": 60}
    )
    assert result2["type"] == FlowResultType.ABORT
