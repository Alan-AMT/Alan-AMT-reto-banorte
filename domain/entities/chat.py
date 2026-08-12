from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, List, Optional, Union


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class TextPart:
    text: str


@dataclass
class ToolCallPart:
    name: str
    args: dict


@dataclass
class ToolResultPart:
    name: str
    result: Any


ChatPart = Union[TextPart, ToolCallPart, ToolResultPart]


@dataclass
class ChatMessage:
    role: Union[Role, str]
    parts: List[ChatPart] = field(default_factory=list)
    timestamp: datetime = field(default_factory=utc_now)

    def __init__(
        self,
        role: Union[Role, str],
        content: Optional[str] = None,
        parts: Optional[List[ChatPart]] = None,
        timestamp: Optional[datetime] = None,
    ):
        self.role = Role(role) if isinstance(role, str) and role in [r.value for r in Role] else role
        if parts is not None:
            self.parts = parts
        elif content is not None:
            self.parts = [TextPart(text=content)]
        else:
            self.parts = []
        self.timestamp = timestamp or utc_now()

    @property
    def content(self) -> str:
        return "".join(part.text for part in self.parts if isinstance(part, TextPart))


@dataclass
class ChatSession:
    session_id: str
    messages: List[ChatMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def add_message(
        self,
        role: Union[Role, str],
        content: Optional[str] = None,
        parts: Optional[List[ChatPart]] = None,
    ) -> ChatMessage:
        msg = ChatMessage(role=role, content=content, parts=parts)
        self.messages.append(msg)
        self.updated_at = utc_now()
        return msg
