import uuid
from application.dtos.chat_dto import ChatMessageDTO, ChatRequestDTO, ChatResponseDTO
from domain.entities.chat import ChatSession
from domain.ports.chat_repository_port import ChatRepositoryPort
from domain.ports.llm_service_port import LLMServicePort


class SendChatMessageUseCase:

    def __init__(
        self,
        chat_repository: ChatRepositoryPort,
        llm_service: LLMServicePort,
    ):
        self.chat_repository = chat_repository
        self.llm_service = llm_service

    async def execute(self, request: ChatRequestDTO) -> ChatResponseDTO:
        session_id = request.session_id or str(uuid.uuid4())

        # 1. Fetch existing session or create new one
        session = await self.chat_repository.get_session(session_id)
        if not session:
            session = ChatSession(session_id=session_id)
        
        print("\n==================================")
        print("SESSION", session)
        print("==================================\n")

        # 2. Append user message
        session.add_message(role="user", content=request.message)

        # 3. Generate response using LLM port
        assistant_reply = await self.llm_service.generate_response(
            prompt=request.message,
            history=session.messages[:-1],  # history prior to current message
        )
        # assistant_reply = "hola"

        # 4. Append assistant response
        session.add_message(role="assistant", content=assistant_reply)

        # 5. Save updated session state
        await self.chat_repository.save_session(session)

        # 6. Build and return output DTO
        history_dtos = [
            ChatMessageDTO(
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp,
            )
            for msg in session.messages
        ]

        return ChatResponseDTO(
            session_id=session.session_id,
            response=assistant_reply,
            history=history_dtos,
        )
