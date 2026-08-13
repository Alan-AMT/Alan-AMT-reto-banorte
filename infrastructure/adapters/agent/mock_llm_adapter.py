from typing import List, Optional
from domain.entities.chat import ChatMessage
from domain.ports.llm_service_port import LLMServicePort
from domain.ports.tool_port import ToolPort


class MockLLMAdapter(LLMServicePort):

    def __init__(self, bot_name: str = "Assistant"):
        self.bot_name = bot_name

    async def generate_response(
        self,
        prompt: str,
        history: List[ChatMessage],
        tools: Optional[List[ToolPort]] = None,
        trace_id: Optional[str] = None,
        telemetry_service: Optional[Any] = None,
    ) -> str:
        history_len = len(history)
        tools_count = len(tools) if tools else 0

        if trace_id and telemetry_service:
            from domain.entities.telemetry import TokenUsage
            telemetry_service.record_llm_execution(
                trace_id=trace_id,
                tokens=TokenUsage(prompt_tokens=15, completion_tokens=25, total_tokens=40),
                latency_ms=10.0,
            )

        return (
            f"[{self.bot_name}] Recibí tu mensaje: '{prompt}'. "
            f"Tienes {history_len} mensajes previos y {tools_count} herramientas disponibles."
        )

