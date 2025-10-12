"""Config flow for NextEnergy Battery."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT

from .const import (
    DOMAIN,
    DEFAULT_POLLING_INTERVAL,
    CONF_POLLING_INTERVAL,
    CONF_PREFIX,
    DEFAULT_PREFIX,
    CONF_SLAVE_ID,
)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=502): int,
        vol.Required(CONF_SLAVE_ID, default=1): int,
        vol.Required(
            CONF_POLLING_INTERVAL, default=DEFAULT_POLLING_INTERVAL
        ): int,
        vol.Required(CONF_PREFIX, default=DEFAULT_PREFIX): str,
    }
)


def options_schema(options: dict) -> vol.Schema:
    """Return a schema for the options flow."""
    return vol.Schema(
        {
            vol.Optional(
                CONF_POLLING_INTERVAL,
                default=options.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL),
            ): int,
        }
    )


class NextEnergyBatteryOptionsFlow(config_entries.OptionsFlow):
    """Handle an options flow for NextEnergy Battery."""

    def __init__(self, config_entry):
        """Initialize the options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init", data_schema=options_schema(self.config_entry.options)
        )


class NextEnergyBatteryConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for NextEnergy Battery."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return NextEnergyBatteryOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
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

            return self.async_create_entry(
                title=user_input[CONF_HOST], data=data, options=options
            )

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )