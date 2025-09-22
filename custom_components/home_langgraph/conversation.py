from typing import Literal
from nabu_agent import execute_main_workflow

from homeassistant.components.conversation import (
    ConversationInput,
    ConversationResult,
    AbstractConversationAgent,
    ConversationEntity,
)
from homeassistant.components import conversation as conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import MATCH_ALL, CONF_LLM_HASS_API
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent, chat_session
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    DOMAIN,
)


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    hass.data[DOMAIN][entry.entry_id] = entry

    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> bool:
    """Set up Local LLM Conversation from a config entry."""

    # handle updates to the options
    entry.async_on_unload(entry.add_update_listener(update_listener))

    # register the agent entity
    async_add_entities([entry.runtime_data])

    return True


class LocalLLMAgent(ConversationEntity, AbstractConversationAgent):
    """Base Local LLM conversation agent."""

    hass: HomeAssistant
    entry_id: str

    _attr_has_entity_name = True
    _attr_supports_streaming = False  # TODO: add support for backends that can stream

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the agent."""
        self._attr_name = entry.title
        self._attr_unique_id = entry.entry_id

        self.hass = hass
        self.entry_id = entry.entry_id

        if self.entry.options.get(CONF_LLM_HASS_API):
            self._attr_supported_features = (
                conversation.ConversationEntityFeature.CONTROL
            )

    async def async_added_to_hass(self) -> None:
        """When entity is added to Home Assistant."""
        await super().async_added_to_hass()
        conversation.async_set_agent(self.hass, self.entry, self)

    async def async_will_remove_from_hass(self) -> None:
        """When entity will be removed from Home Assistant."""
        conversation.async_unset_agent(self.hass, self.entry)
        await super().async_will_remove_from_hass()

    @property
    def entry(self) -> ConfigEntry:
        try:
            return self.hass.data[DOMAIN][self.entry_id]
        except KeyError as ex:
            raise Exception("Attempted to use self.entry during startup.") from ex

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return a list of supported languages."""
        return MATCH_ALL

    async def async_process(self, user_input: ConversationInput) -> ConversationResult:
        """Process a sentence."""
        with (
            chat_session.async_get_chat_session(
                self.hass, user_input.conversation_id
            ) as session,
            conversation.async_get_chat_log(self.hass, session, user_input) as chat_log,
        ):
            return await self._async_handle_message(user_input, chat_log)

    async def _async_handle_message(
        self,
        user_input: conversation.ConversationInput,
        chat_log: conversation.ChatLog,
    ) -> conversation.ConversationResult:
        result = await execute_main_workflow(user_input.text)
        i = intent.IntentResponse(language="ca")
        i.async_set_speech(result)
        return ConversationResult(
            response=i, conversation_id=user_input.conversation_id
        )
