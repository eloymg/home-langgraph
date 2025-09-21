from typing import Any

from homeassistant import config_entries
from homeassistant.data_entry_flow import (
    FlowResult,
)

from .const import DOMAIN


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        return self.async_create_entry(
            title="Home LangGraph",
            description="Use LangGraph in HA",
        )
