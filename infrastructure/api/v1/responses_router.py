import json
import time
import uuid
import asyncio
from typing import cast, AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse

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

async def generate_sse_events(
    full_response: OpenResponsesResponse, 
    chat_resp_text: str, 
    msg_id: str
) -> AsyncGenerator[str, None]:
    seq = 0
    
    def format_event(event_type: str, data: dict) -> str:
        # Use model_dump for Pydantic v2 or dict() if data has pydantic models inside
        return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"

    # 1. response.created
    resp_created = full_response.model_dump(mode="json")
    resp_created["status"] = "in_progress"
    resp_created["output"] = []
    
    yield format_event(
        "response.created",
        {
            "type": "response.created",
            "sequence_number": seq,
            "response": resp_created
        }
    )
    seq += 1

    # 2. response.output_item.added
    yield format_event(
        "response.output_item.added",
        {
            "type": "response.output_item.added",
            "sequence_number": seq,
            "output_index": 0,
            "item": {
                "type": "message",
                "id": msg_id,
                "status": "in_progress",
                "role": "assistant",
                "content": []
            }
        }
    )
    seq += 1

    # 3. response.content_part.added
    yield format_event(
        "response.content_part.added",
        {
            "type": "response.content_part.added",
            "sequence_number": seq,
            "item_id": msg_id,
            "output_index": 0,
            "content_index": 0,
            "part": {
                "type": "output_text",
                "text": "",
                "annotations": []
            }
        }
    )
    seq += 1

    # 4. response.output_text.delta (loop)
    words = chat_resp_text.split(" ")
    for i, word in enumerate(words):
        chunk = word if i == 0 else " " + word
        yield format_event(
            "response.output_text.delta",
            {
                "type": "response.output_text.delta",
                "sequence_number": seq,
                "item_id": msg_id,
                "output_index": 0,
                "content_index": 0,
                "delta": chunk,
                "logprobs": []
            }
        )
        seq += 1
        await asyncio.sleep(0.01)

    # 5. response.output_text.done
    yield format_event(
        "response.output_text.done",
        {
            "type": "response.output_text.done",
            "sequence_number": seq,
            "item_id": msg_id,
            "output_index": 0,
            "content_index": 0,
            "text": chat_resp_text
        }
    )
    seq += 1

    # 6. response.content_part.done
    yield format_event(
        "response.content_part.done",
        {
            "type": "response.content_part.done",
            "sequence_number": seq,
            "item_id": msg_id,
            "output_index": 0,
            "content_index": 0,
            "part": {
                "type": "output_text",
                "text": chat_resp_text,
                "annotations": []
            }
        }
    )
    seq += 1

    # 7. response.output_item.done
    yield format_event(
        "response.output_item.done",
        {
            "type": "response.output_item.done",
            "sequence_number": seq,
            "output_index": 0,
            "item": {
                "type": "message",
                "id": msg_id,
                "status": "completed",
                "role": "assistant",
                "content": [
                    {
                        "type": "output_text",
                        "text": chat_resp_text,
                        "annotations": []
                    }
                ]
            }
        }
    )
    seq += 1

    # 8. response.completed
    yield format_event(
        "response.completed",
        {
            "type": "response.completed",
            "sequence_number": seq,
            "response": full_response.model_dump(mode="json")
        }
    )
    seq += 1

    # 9. [DONE]
    yield "data: [DONE]\n\n"


@router.post(
    "",
    response_model=None, # Changed to None because it can return StreamingResponse or OpenResponsesResponse
    status_code=status.HTTP_200_OK,
    summary="Generate a response using OpenResponses format",
    dependencies=[Depends(verify_api_key)],
)
async def generate_response(
    request: OpenResponsesRequest,
    use_case: SendChatMessageUseCase = Depends(get_send_chat_message_use_case),
):
    # 1. Map input to ChatRequestDTO
    input_text = request.input if isinstance(request.input, str) else str(request.input)
    
    message_content = input_text
    if request.instructions:
        message_content = f"Instructions: {request.instructions}\n\n{input_text}"

    print(request)

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
    msg_id = f"msg_{uuid.uuid4().hex}"

    # 3. Map Response to OpenResponsesResponse
    output_message = Message(
        id=msg_id,
        status="completed",
        role="assistant",
        content=[OutputTextContent(text=chat_resp.response, type="output_text")]
    )

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

    full_response = OpenResponsesResponse(
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

    if request.stream:
        return StreamingResponse(
            generate_sse_events(full_response, chat_resp.response, msg_id),
            media_type="text/event-stream"
        )
    
    return full_response
