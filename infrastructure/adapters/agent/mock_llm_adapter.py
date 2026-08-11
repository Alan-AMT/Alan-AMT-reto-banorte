from typing import List
from domain.entities.chat import ChatMessage
from domain.ports.llm_service_port import LLMServicePort


class MockLLMAdapter(LLMServicePort):

    def __init__(self, bot_name: str = "Assistant"):
        self.bot_name = bot_name

    async def generate_response(
        self, prompt: str, history: List[ChatMessage]
    ) -> str:
        history_len = len(history)
        return (
            f"[{self.bot_name}] Recibí tu mensaje: '{prompt}'. "
            f"Tienes {history_len} mensajes previos en tu historial de conversación."
        )
