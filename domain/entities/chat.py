from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class ChatMessage:
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = field(default_factory=utc_now)


@dataclass
class ChatSession:
    session_id: str
    messages: List[ChatMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def add_message(self, role: str, content: str) -> ChatMessage:
        msg = ChatMessage(role=role, content=content)
        self.messages.append(msg)
        self.updated_at = utc_now()
        return msg

