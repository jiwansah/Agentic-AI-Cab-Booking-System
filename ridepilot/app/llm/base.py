from abc import ABC, abstractmethod
from typing import Any


class LLMAdapter(ABC):

    @abstractmethod
    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> Any:
        """Send messages to an LLM and return its response."""
        pass

