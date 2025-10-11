"""Options flow for NextEnergy Battery."""
import voluptuous as vol
from homeassistant import config_entries


class NextEnergyBatteryOptionsFlow(config_entries.OptionsFlow):
    """Handle an options flow for NextEnergy Battery."""

    def __init__(self, config_entry):
        """Initialize the options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema(
            {
                vol.Optional(
                    "polling_interval",
                    default=self.config_entry.options.get("polling_interval", 30),
                ): int,
            }
        )

        return self.async_show_form(step_id="init", data_schema=options_schema)
