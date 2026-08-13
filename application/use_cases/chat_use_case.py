from domain.ports.input_guardrail import InputGuardrail
import uuid
from typing import List, Optional
from application.dtos.chat_dto import ChatMessageDTO, ChatRequestDTO, ChatResponseDTO
from domain.entities.chat import ChatSession
from domain.ports.chat_repository_port import ChatRepositoryPort
from domain.ports.llm_service_port import LLMServicePort
from domain.ports.tool_port import ToolPort


class SendChatMessageUseCase:

    def __init__(
        self,
        chat_repository: ChatRepositoryPort,
        llm_service: LLMServicePort,
        input_guardrail: InputGuardrail,
        tools: Optional[List[ToolPort]] = None,
    ):
        self.chat_repository = chat_repository
        self.llm_service = llm_service
        self.input_guardrail = input_guardrail
        self.tools = tools or []

    async def execute(self, request: ChatRequestDTO) -> ChatResponseDTO:
        session_id = request.session_id or str(uuid.uuid4())

        # 1. Fetch existing session or create new one
        session = await self.chat_repository.get_session(session_id)
        if not session:
            session = ChatSession(session_id=session_id)

        # 2. Append user message
        session.add_message(role="user", content=request.message)

        # 2.1 Apply input guardrail
        guardrail_result = await self.input_guardrail.evaluate_prompt(request.message)
        if guardrail_result.blocked:
            session.add_message(role="assistant", content=guardrail_result.block_message)
            await self.chat_repository.save_session(session)
            return ChatResponseDTO(
                session_id=session_id,
                response=guardrail_result.block_message,
                history=[ChatMessageDTO(
                    role=msg.role,
                    content=msg.content,
                    timestamp=msg.timestamp,
                ) for msg in session.messages]
            )

        # 3. Generate response using LLM port
        assistant_reply = await self.llm_service.generate_response(
            prompt=request.message,
            history=session.messages[:-1],  # history prior to current message
            tools=self.tools,
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
