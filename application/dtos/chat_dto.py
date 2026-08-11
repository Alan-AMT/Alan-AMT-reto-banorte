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


class ChatResponseDTO(BaseModel):
    session_id: str = Field(..., description="Unique ID for the chat session")
    response: str = Field(..., description="Generated answer from the assistant")
    history: List[ChatMessageDTO] = Field(
        default_factory=list, description="Recent conversation history"
    )
    timestamp: datetime = Field(default_factory=utc_now)

