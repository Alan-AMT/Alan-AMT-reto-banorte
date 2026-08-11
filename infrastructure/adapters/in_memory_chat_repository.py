from typing import Dict, Optional
from domain.entities.chat import ChatSession
from domain.ports.chat_repository_port import ChatRepositoryPort


class InMemoryChatRepository(ChatRepositoryPort):

    def __init__(self):
        self._storage: Dict[str, ChatSession] = {}

    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        return self._storage.get(session_id)

    async def save_session(self, session: ChatSession) -> None:
        self._storage[session.session_id] = session
