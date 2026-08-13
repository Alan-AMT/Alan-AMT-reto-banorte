from domain.ports.input_guardrail import InputGuardrail
from typing import List
from fastapi import Depends, Request

from application.use_cases.chat_use_case import SendChatMessageUseCase
from domain.ports.chat_repository_port import ChatRepositoryPort
from domain.ports.llm_service_port import LLMServicePort
from domain.ports.tool_port import ToolPort


def get_chat_repository(request: Request) -> ChatRepositoryPort:
    return request.app.state.chat_repository


def get_llm_service(request: Request) -> LLMServicePort:
    return request.app.state.llm_service


def get_tools(request: Request) -> List[ToolPort]:
    return getattr(request.app.state, "tools", [])

def get_input_guardrail(request: Request) -> InputGuardrail:
    return request.app.state.input_guardrail


def get_send_chat_message_use_case(
    repository: ChatRepositoryPort = Depends(get_chat_repository),
    llm_service: LLMServicePort = Depends(get_llm_service),
    input_guardrail: InputGuardrail = Depends(get_input_guardrail),
    tools: List[ToolPort] = Depends(get_tools),
) -> SendChatMessageUseCase:
    return SendChatMessageUseCase(
        chat_repository=repository,
        llm_service=llm_service,
        input_guardrail=input_guardrail,
        tools=tools,
    )

