import time
import uuid
from typing import cast
from fastapi import APIRouter, Depends, HTTPException, status, Request

from application.dtos.chat_dto import ChatRequestDTO
from application.dtos.openresponses_dto import (
    OpenResponsesRequest,
    OpenResponsesResponse,
    Message,
    OutputTextContent,
    Usage,
    UsageDetails,
    OutputUsageDetails,
    TextFormat,
    Reasoning
)
from application.use_cases.chat_use_case import SendChatMessageUseCase
from domain.exceptions import DomainException
from infrastructure.api.dependencies import get_send_chat_message_use_case, verify_api_key

router = APIRouter(prefix="/v1/responses", tags=["OpenResponses"])


@router.post(
    "",
    response_model=OpenResponsesResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a response using OpenResponses format",
    dependencies=[Depends(verify_api_key)],
)
async def generate_response(
    request: OpenResponsesRequest,
    use_case: SendChatMessageUseCase = Depends(get_send_chat_message_use_case),
) -> OpenResponsesResponse:
    if request.stream:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Streaming is not implemented in this version",
        )

    # 1. Map input to ChatRequestDTO
    # input can be string or list. We only support string in this iteration.
    input_text = request.input if isinstance(request.input, str) else str(request.input)
    
    # If instructions are provided, we prepend them to the message or handle them appropriately.
    # The existing use case just takes a user message. For now we will append instructions if provided
    # so they form part of the prompt context, or just pass the input. The spec says treat instructions
    # as an override/addition to system instructions. Since our ChatRequestDTO only takes a message,
    # we can inject it there if needed.
    message_content = input_text
    if request.instructions:
        message_content = f"Instructions: {request.instructions}\n\n{input_text}"

    chat_req = ChatRequestDTO(
        message=message_content,
        session_id=request.previous_response_id
    )

    created_at = int(time.time())

    # 2. Invoke existing Use Case
    try:
        chat_resp = await use_case.execute(chat_req)
    except DomainException as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        print(exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred processing your request.",
        )

    completed_at = int(time.time())

    # 3. Map Response to OpenResponsesResponse
    output_message = Message(
        id=f"msg_{uuid.uuid4().hex}",
        status="completed",
        role="assistant",
        content=[OutputTextContent(text=chat_resp.response, type="output_text")]
    )

    # Calculate tokens if available
    input_tokens = 0
    output_tokens = 0
    total_tokens = 0
    if chat_resp.telemetry:
        input_tokens = chat_resp.telemetry.prompt_tokens
        output_tokens = chat_resp.telemetry.completion_tokens
        total_tokens = chat_resp.telemetry.total_tokens

    usage = Usage(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        input_tokens_details=UsageDetails(cached_tokens=0),
        output_tokens_details=OutputUsageDetails(reasoning_tokens=0),
    )

    return OpenResponsesResponse(
        id=f"resp_{uuid.uuid4().hex}",
        object="response",
        created_at=created_at,
        completed_at=completed_at,
        status="completed",
        model=request.model or "default",
        previous_response_id=chat_resp.session_id,
        instructions=request.instructions or "",
        output=[output_message],
        usage=usage,
        max_output_tokens=request.max_output_tokens,
        temperature=request.temperature if request.temperature is not None else 1.0,
        top_p=request.top_p if request.top_p is not None else 1.0
    )
