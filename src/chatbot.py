from typing import Optional

from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger
from src.telemetry.metrics import tracker


class ChatbotBaseline:
    """
    Minimal chatbot baseline for Phase 1.
    It performs a single LLM call without tool use or ReAct reasoning.
    """

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def ask(self, user_input: str, system_prompt: Optional[str] = None) -> str:
        logger.log_event(
            "CHATBOT_START",
            {
                "input": user_input,
                "model": self.llm.model_name,
            },
        )

        result = self.llm.generate(user_input, system_prompt=system_prompt)

        tracker.track_request(
            provider=result.get("provider", "unknown"),
            model=self.llm.model_name,
            usage=result.get("usage", {}),
            latency_ms=result.get("latency_ms", 0),
        )

        logger.log_event(
            "CHATBOT_END",
            {
                "model": self.llm.model_name,
                "provider": result.get("provider", "unknown"),
                "response": result["content"],
            },
        )

        return result["content"]
