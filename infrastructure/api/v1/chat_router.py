from fastapi import APIRouter, Depends, HTTPException, status

from application.dtos.chat_dto import ChatRequestDTO, ChatResponseDTO
from application.use_cases.chat_use_case import SendChatMessageUseCase
from domain.exceptions import DomainException
from infrastructure.api.dependencies import get_send_chat_message_use_case

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "",
    response_model=ChatResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Send a chat message",
    description="Processes a user message and generates a response using hexagonal use cases and adapters.",
)
async def chat_endpoint(
    request: ChatRequestDTO,
    use_case: SendChatMessageUseCase = Depends(get_send_chat_message_use_case),
) -> ChatResponseDTO:
    try:
        return await use_case.execute(request)
    except DomainException as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred processing your request.",
        )
