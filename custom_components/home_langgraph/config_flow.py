"""Config flow for Fallback Conversation integration."""
from __future__ import annotations

import logging
# from types import MappingProxyType
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    ConversationAgentSelector,
    ConversationAgentSelectorConfig,
    SelectSelector,
    SelectSelectorConfig,
    SelectOptionDict,
    SelectSelectorMode,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_NAME, default="Langgraph conversation agent"): str,
    }
)

class ConfigFlow(config_entries.ConfigFlow, domain="home_langgraph"):
    """Fallback Agent config flow."""

    VERSION = 2

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        _LOGGER.debug("ConfigFlow::user_input %s", user_input)
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
            )

        return self.async_create_entry(
            title=user_input.get(CONF_NAME,"Langgraph conversation agent"),
            data=user_input,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlow(config_entry)

class OptionsFlow(config_entries.OptionsFlow):
    """Fallback config flow options handler."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self._options = dict(config_entry.data)
        self._options.update(dict(config_entry.options))

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            self._options.update(user_input)
            return self.async_create_entry(
                title=user_input.get(CONF_NAME, "Langgraph conversation agent"),
                data=self._options,
            )

        schema = await self.fallback_config_option_schema(self._options)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema),
        )