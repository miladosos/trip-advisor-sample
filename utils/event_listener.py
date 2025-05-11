from crewai.utilities.events import (LLMCallCompletedEvent, LLMCallFailedEvent, LLMCallStartedEvent)
from crewai.utilities.events.base_event_listener import BaseEventListener
from crewai.utilities.events.crewai_event_bus import CrewAIEventsBus

from .custom_logger import CustomLogger

class LLMEventListener(BaseEventListener):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.verbose = True

    def setup_listeners(self, crewai_event_bus: CrewAIEventsBus):
        @crewai_event_bus.on(LLMCallStartedEvent)
        def on_llm_call_started(self, event: LLMCallStartedEvent):
            CustomLogger.log_event(
                event_type="llm_call_started",
                data={
                    "messages": event.messages,
                },
            )

        @crewai_event_bus.on(LLMCallCompletedEvent)
        def on_llm_call_completed(self, event: LLMCallCompletedEvent):
            CustomLogger.log_event(
                event_type="llm_call_completed",
                data={
                    "response": event.response,
                    "call_type": event.call_type.value,
                },
            )

        @crewai_event_bus.on(LLMCallFailedEvent)
        def on_llm_call_failed(self, event: LLMCallFailedEvent):
            CustomLogger.log_event(
                event_type="llm_call_failed",
                data={
                    "error": event.error,
                },
            )
