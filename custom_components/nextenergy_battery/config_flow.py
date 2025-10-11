"""Config flow for NextEnergy Battery."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT

from .const import DOMAIN
# from .modbus import NextEnergyModbusClient  <- Temporarily removed
from .options import NextEnergyBatteryOptionsFlow


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
            # Temporarily bypass connection test
            await self.async_set_unique_id(user_input[CONF_HOST])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=user_input[CONF_HOST], data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=502): int,
                vol.Required("slave_id", default=1): int,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
