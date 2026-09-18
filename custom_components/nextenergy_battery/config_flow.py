"""Config flow for NextEnergy Battery."""
import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from modbus_connection import ModbusError

from .const import (
    CONF_POLLING_INTERVAL,
    CONF_PREFIX,
    CONF_SLAVE_ID,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_PREFIX,
    DOMAIN,
    MANUFACTURER,
)
from .device import NextEnergyBattery, create_connection

_LOGGER = logging.getLogger(__name__)


async def async_probe(host: str, port: int, slave_id: int) -> str:
    """Probe the battery over TCP, returning its serial; raises on failure."""
    connection = create_connection(host, port)
    try:
        return await NextEnergyBattery.async_probe(
            connection.for_unit(slave_id)
        )
    finally:
        await connection.close()


class NextEnergyBatteryConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for NextEnergy Battery."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return NextEnergyBatteryOptionsFlow()

    async def async_step_user(self, user_input=None):
        """Handle the initial setup step."""
        errors = {}

        if user_input is not None:
            try:
                serial = await async_probe(
                    user_input[CONF_HOST],
                    user_input[CONF_PORT],
                    user_input[CONF_SLAVE_ID],
                )
            except ModbusError:
                errors["base"] = "cannot_connect"
            else:
                # Key the entry on the serial where the battery reports one,
                # so the same device is recognised across addresses. Firmware
                # that does not serve the identity block falls back to host.
                await self.async_set_unique_id(serial or user_input[CONF_HOST])
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

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            try:
                await async_probe(
                    user_input[CONF_HOST],
                    user_input[CONF_PORT],
                    user_input[CONF_SLAVE_ID],
                )
            except ModbusError:
                errors["base"] = "cannot_connect"
            else:
                old_prefix = (
                    self.config_entry.options.get(CONF_PREFIX, DEFAULT_PREFIX)
                    or DEFAULT_PREFIX
                )
                new_prefix = user_input[CONF_PREFIX] or DEFAULT_PREFIX
                new_data = {
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_PORT: user_input[CONF_PORT],
                    CONF_SLAVE_ID: user_input[CONF_SLAVE_ID],
                }
                new_options = {
                    CONF_POLLING_INTERVAL: user_input[CONF_POLLING_INTERVAL],
                    CONF_PREFIX: new_prefix,
                }
                new_title = f"{MANUFACTURER} ({user_input[CONF_HOST]})"

                self.hass.config_entries.async_update_entry(
                    self.config_entry, title=new_title, data=new_data, options=new_options
                )
                if new_prefix != old_prefix:
                    _async_migrate_prefix(
                        self.hass, self.config_entry, old_prefix, new_prefix
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
            vol.Required(
                CONF_PREFIX,
                default=options.get(CONF_PREFIX, DEFAULT_PREFIX)
            ): str,
        })

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            errors=errors,
        )


def _async_migrate_prefix(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
    old_prefix: str,
    new_prefix: str,
) -> None:
    """Rewrite entity identities after a prefix change.

    Entity unique ids and ids embed the prefix, so without a rewrite every
    entity would be orphaned and recreated. Best-effort: a collision leaves
    the affected entity on its old identity rather than failing the save.
    """
    registry = er.async_get(hass)
    old_uid_prefix = f"{entry.entry_id}_{old_prefix}_"
    for registry_entry in er.async_entries_for_config_entry(registry, entry.entry_id):
        if not registry_entry.unique_id.startswith(old_uid_prefix):
            continue
        rest = registry_entry.unique_id.removeprefix(old_uid_prefix)
        new_unique_id = f"{entry.entry_id}_{new_prefix}_{rest}"
        new_entity_id = f"sensor.{new_prefix}_{rest}"
        if registry.async_get_entity_id(
            registry_entry.domain, DOMAIN, new_unique_id
        ):
            _LOGGER.warning(
                "Not migrating %s to unique id %s: already in use",
                registry_entry.entity_id,
                new_unique_id,
            )
            continue
        try:
            registry.async_update_entity(
                registry_entry.entity_id,
                new_unique_id=new_unique_id,
                new_entity_id=new_entity_id,
            )
        except ValueError as err:
            _LOGGER.warning("Not migrating %s: %s", registry_entry.entity_id, err)
