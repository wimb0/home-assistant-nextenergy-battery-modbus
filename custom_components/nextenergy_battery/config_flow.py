"""Config flow for NextEnergy Battery."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback

from .const import (
    DOMAIN,
    DEFAULT_POLLING_INTERVAL,
    CONF_POLLING_INTERVAL,
    CONF_PREFIX,
    DEFAULT_PREFIX,
    CONF_SLAVE_ID,
    MANUFACTURER,
)

class NextEnergyBatteryConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for NextEnergy Battery."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return NextEnergyBatteryOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial setup step."""
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_HOST])
            self._abort_if_unique_id_configured()

            data = {
                CONF_HOST: user_input[CONF_HOST],
                CONF_PORT: user_input[CONF_PORT],
                CONF_SLAVE_ID: user_input[CONF_SLAVE_ID],
            }
            options = {
                CONF_POLLING_INTERVAL: user_input[CONF_POLLING_INTERVAL],
                CONF_PREFIX: user_input[CONF_PREFIX],
            }

            title = f"{MANUFACTURER} ({user_input[CONF_HOST]})"
            return self.async_create_entry(
                title=title, data=data, options=options
            )

        data_schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_PORT, default=502): int,
            vol.Required(CONF_SLAVE_ID, default=1): int,
            vol.Required(CONF_POLLING_INTERVAL, default=DEFAULT_POLLING_INTERVAL): int,
            vol.Required(CONF_PREFIX, default=DEFAULT_PREFIX): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

class NextEnergyBatteryOptionsFlow(config_entries.OptionsFlow):
    """Handle an options flow for changing settings."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize the options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            new_data = {
                CONF_HOST: user_input[CONF_HOST],
                CONF_PORT: user_input[CONF_PORT],
                CONF_SLAVE_ID: user_input[CONF_SLAVE_ID],
            }
            
            new_options = {
                CONF_POLLING_INTERVAL: user_input[CONF_POLLING_INTERVAL],
                CONF_PREFIX: self.config_entry.options.get(CONF_PREFIX),
            }
            
            new_title = f"{MANUFACTURER} ({user_input[CONF_HOST]})"
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                title=new_title,
                data=new_data,
                options=new_options
            )
            return self.async_abort(reason="reconfigure_successful")

        data = self.config_entry.data
        options = self.config_entry.options
        
        options_schema = vol.Schema({
            vol.Required(CONF_HOST, default=data.get(CONF_HOST)): str,
            vol.Required(CONF_PORT, default=data.get(CONF_PORT, 502)): int,
            vol.Required(CONF_SLAVE_ID, default=data.get(CONF_SLAVE_ID, 1)): int,
            vol.Required(
                CONF_POLLING_INTERVAL, 
                default=options.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)
            ): int,
        })
        
        return self.async_show_form(
            step_id="init",
            data_schema=options_schema
        )
