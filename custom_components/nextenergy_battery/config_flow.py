
"""Config flow for NextEnergy Battery."""
import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN


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
            await self.async_set_unique_id(user_input["host"])
            self._abort_if_unique_id_configured()

            # Here you would validate the user input, e.g., check if you can connect to the Modbus device
            # For now, we'll just assume the input is valid
            return self.async_create_entry(title=user_input["host"], data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required("host"): str,
                vol.Required("port", default=502): int,
                vol.Required("slave_id", default=1): int,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
