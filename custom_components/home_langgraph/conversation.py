from homeassistant.components.conversation import ConversationInput, ConversationResult, AbstractConversationAgent, ConversationEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components import assist_pipeline, conversation as conversation
from homeassistant.helpers import config_validation as cv, intent, template, entity_registry as er, llm, \
    area_registry as ar, device_registry as dr, chat_session

from homeassistant.const import ATTR_ENTITY_ID, CONF_HOST, CONF_PORT, CONF_SSL, MATCH_ALL, CONF_LLM_HASS_API

class LocalLLMAgent(ConversationEntity, AbstractConversationAgent):
    """Base Local LLM conversation agent."""

    hass: HomeAssistant
    entry_id: str
    in_context_examples: list[dict]

    _attr_has_entity_name = True
    _attr_supports_streaming = False # TODO: add support for backends that can stream

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the agent."""
        self._attr_name = entry.title
        self._attr_unique_id = entry.entry_id

        self.hass = hass
        self.entry_id = entry.entry_id

        self.backend_type = "asd"
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
            return self.hass.data["home_langgraph"][self.entry_id]
        except KeyError as ex:
            raise Exception("Attempted to use self.entry during startup.") from ex

    async def async_process(
        self, user_input: ConversationInput
    ) -> ConversationResult:
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

            return ConversationResult(
                    response="asd", conversation_id=user_input.conversation_id
                )