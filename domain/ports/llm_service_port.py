from abc import ABC, abstractmethod
from typing import List
from domain.entities.chat import ChatMessage


class LLMServicePort(ABC):

    @abstractmethod
    async def generate_response(
        self, prompt: str, history: List[ChatMessage]
    ) -> str:
        """Generate LLM response given a user prompt and previous message history."""
        pass
