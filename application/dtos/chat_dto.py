from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ChatMessageDTO(BaseModel):
    role: str = Field(..., description="Role of the speaker: user or assistant")
    content: str = Field(..., description="Content of the message")
    timestamp: datetime = Field(default_factory=utc_now)


class ChatRequestDTO(BaseModel):
    message: str = Field(..., min_length=1, description="The user input message")
    session_id: Optional[str] = Field(
        None, description="Optional session ID for maintaining chat history"
    )


class TelemetryDTO(BaseModel):
    trace_id: str = Field(..., description="Unique ID for the execution trace")
    total_tokens: int = Field(0, description="Total tokens consumed across all model calls")
    prompt_tokens: int = Field(0, description="Prompt/Input tokens consumed")
    completion_tokens: int = Field(0, description="Completion/Output tokens generated")
    latency_ms: float = Field(0.0, description="End-to-end execution latency in milliseconds")
    tools_called_count: int = Field(0, description="Number of tool calls executed")
    guardrail_blocked: bool = Field(False, description="Whether the prompt was blocked by guardrail")
    guardrail_category: Optional[str] = Field(None, description="Guardrail category if blocked")


class ChatResponseDTO(BaseModel):
    session_id: str = Field(..., description="Unique ID for the chat session")
    response: str = Field(..., description="Generated answer from the assistant")
    history: List[ChatMessageDTO] = Field(
        default_factory=list, description="Recent conversation history"
    )
    telemetry: Optional[TelemetryDTO] = Field(
        None, description="Execution telemetry metrics (tokens, latency, tool calls)"
    )
    timestamp: datetime = Field(default_factory=utc_now)


