from domain.ports.input_guardrail import InputGuardrail
from typing import List
# pyrefly: ignore [missing-import]
import os
from fastapi import Depends, Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


from application.use_cases.chat_use_case import SendChatMessageUseCase
from domain.ports.chat_repository_port import ChatRepositoryPort
from domain.ports.llm_service_port import LLMServicePort
from domain.ports.tool_port import ToolPort


from domain.ports.telemetry_port import TelemetryPort


def get_chat_repository(request: Request) -> ChatRepositoryPort:
    return request.app.state.chat_repository


def get_llm_service(request: Request) -> LLMServicePort:
    return request.app.state.llm_service


def get_tools(request: Request) -> List[ToolPort]:
    return getattr(request.app.state, "tools", [])


def get_input_guardrail(request: Request) -> InputGuardrail:
    return request.app.state.input_guardrail


def get_telemetry_service(request: Request) -> TelemetryPort:
    return request.app.state.telemetry_service


def get_send_chat_message_use_case(
    repository: ChatRepositoryPort = Depends(get_chat_repository),
    llm_service: LLMServicePort = Depends(get_llm_service),
    input_guardrail: InputGuardrail = Depends(get_input_guardrail),
    tools: List[ToolPort] = Depends(get_tools),
    telemetry_service: TelemetryPort = Depends(get_telemetry_service),
) -> SendChatMessageUseCase:
    return SendChatMessageUseCase(
        chat_repository=repository,
        llm_service=llm_service,
        input_guardrail=input_guardrail,
        tools=tools,
        telemetry_service=telemetry_service,
    )


security = HTTPBearer()

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    expected_api_key = os.getenv("API_KEY")
    if not expected_api_key or credentials.credentials != expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials
