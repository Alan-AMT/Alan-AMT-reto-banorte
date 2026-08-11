from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.chat import ChatSession


class ChatRepositoryPort(ABC):

    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Retrieve a chat session by ID."""
        pass

    @abstractmethod
    async def save_session(self, session: ChatSession) -> None:
        """Save or update a chat session."""
        pass
