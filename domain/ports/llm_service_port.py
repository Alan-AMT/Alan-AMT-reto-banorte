from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.chat import ChatMessage
from domain.ports.tool_port import ToolPort


class LLMServicePort(ABC):

    @abstractmethod
    async def generate_response(
        self,
        prompt: str,
        history: List[ChatMessage],
        tools: Optional[List[ToolPort]] = None,
    ) -> str:
        """Generate LLM response given a user prompt, message history, and optional tools."""
        pass
