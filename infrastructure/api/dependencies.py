from infrastructure.adapters.agent.gemini_llm_adapter import GeminiLLMAdapter
from functools import lru_cache
from fastapi import Depends

from application.use_cases.chat_use_case import SendChatMessageUseCase
from domain.ports.chat_repository_port import ChatRepositoryPort
from domain.ports.llm_service_port import LLMServicePort
from infrastructure.adapters.in_memory_chat_repository import InMemoryChatRepository
from infrastructure.adapters.agent.mock_llm_adapter import MockLLMAdapter
from infrastructure.config.settings import settings

# Global singletons for in-memory adapters (for demo/development)
_chat_repository_instance = InMemoryChatRepository()


def get_chat_repository() -> ChatRepositoryPort:
    return _chat_repository_instance


@lru_cache()
def get_llm_service() -> LLMServicePort:
    return GeminiLLMAdapter()


def get_send_chat_message_use_case(
    repository: ChatRepositoryPort = Depends(get_chat_repository),
    llm_service: LLMServicePort = Depends(get_llm_service),
) -> SendChatMessageUseCase:
    return SendChatMessageUseCase(
        chat_repository=repository,
        llm_service=llm_service,
    )
