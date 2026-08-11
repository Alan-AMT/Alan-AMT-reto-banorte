from fastapi import Depends, Request

from application.use_cases.chat_use_case import SendChatMessageUseCase
from domain.ports.chat_repository_port import ChatRepositoryPort
from domain.ports.llm_service_port import LLMServicePort


def get_chat_repository(request: Request) -> ChatRepositoryPort:
    return request.app.state.chat_repository


def get_llm_service(request: Request) -> LLMServicePort:
    return request.app.state.llm_service


def get_send_chat_message_use_case(
    repository: ChatRepositoryPort = Depends(get_chat_repository),
    llm_service: LLMServicePort = Depends(get_llm_service),
) -> SendChatMessageUseCase:
    return SendChatMessageUseCase(
        chat_repository=repository,
        llm_service=llm_service,
    )

