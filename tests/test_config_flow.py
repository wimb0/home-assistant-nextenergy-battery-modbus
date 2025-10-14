"""Test NextEnergy Battery config flow."""
from unittest.mock import patch

import pytest
from homeassistant import config_entries, data_entry_flow
from homeassistant.core import HomeAssistant

from custom_components.nextenergy_battery.const import DOMAIN
from .const import MOCK_CONFIG


@pytest.mark.parametrize("user_input", [MOCK_CONFIG])
async def test_form_success(hass: HomeAssistant, user_input, bypass_get_data) -> None:
    """Test we get the form and it works."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM

    with patch(
        "custom_components.nextenergy_battery.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input,
        )
        await hass.async_block_till_done()

    assert result2["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result2["title"] == f"NextEnergy ({MOCK_CONFIG['host']})"
    assert result2["data"] == {
        "host": MOCK_CONFIG["host"],
        "port": MOCK_CONFIG["port"],
        "slave_id": MOCK_CONFIG["slave_id"],
    }
    assert result2["options"] == {
        "polling_interval": MOCK_CONFIG["polling_interval"],
        "prefix": MOCK_CONFIG["prefix"],
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_options_flow(hass: HomeAssistant) -> None:
    """Test the options flow."""
    entry = config_entries.ConfigEntry(
        version=1,
        domain=DOMAIN,
        title=f"NextEnergy ({MOCK_CONFIG['host']})",
        data={
            "host": MOCK_CONFIG["host"],
            "port": MOCK_CONFIG["port"],
            "slave_id": MOCK_CONFIG["slave_id"],
        },
        options={
            "polling_interval": 30,
            "prefix": "test_prefix",
        },
    )
    entry.add_to_hass(hass)
    
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "init"

    # Test updating options
    new_host = "4.3.2.1"
    new_polling_interval = 60
    
    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"host": new_host, "port": 502, "slave_id": 1, "polling_interval": new_polling_interval},
    )

    assert result2["type"] == data_entry_flow.RESULT_TYPE_ABORT
    assert result2["reason"] == "reconfigure_successful"
    
    assert entry.data["host"] == new_host
    assert entry.options["polling_interval"] == new_polling_interval
