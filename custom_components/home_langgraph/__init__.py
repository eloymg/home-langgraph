"""The Local LLM Conversation integration."""
from __future__ import annotations

import logging
from typing import Final

import homeassistant.components.conversation as ha_conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, llm
from homeassistant.util.json import JsonObjectType

import voluptuous as vol

DOMAIN ="home_langgraph"
from .conversation import  LanggraphAgent

type LocalLLMConfigEntry = ConfigEntry[LanggraphAgent]

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

PLATFORMS = (Platform.CONVERSATION,)


async def async_setup_entry(hass: HomeAssistant, entry: LocalLLMConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry
    # forward setup to platform to register the entity
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True
