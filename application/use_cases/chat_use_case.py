import uuid
from typing import List, Optional

from application.dtos.chat_dto import ChatMessageDTO, ChatRequestDTO, ChatResponseDTO, TelemetryDTO
from domain.entities.chat import ChatSession
from domain.entities.telemetry import GuardrailSpan, TokenUsage
from domain.ports.chat_repository_port import ChatRepositoryPort
from domain.ports.input_guardrail import InputGuardrail
from domain.ports.llm_service_port import LLMServicePort
from domain.ports.telemetry_port import TelemetryPort
from domain.ports.tool_port import ToolPort


class SendChatMessageUseCase:

    def __init__(
        self,
        chat_repository: ChatRepositoryPort,
        llm_service: LLMServicePort,
        input_guardrail: InputGuardrail,
        tools: Optional[List[ToolPort]] = None,
        telemetry_service: Optional[TelemetryPort] = None,
    ):
        self.chat_repository = chat_repository
        self.llm_service = llm_service
        self.input_guardrail = input_guardrail
        self.tools = tools or []
        self.telemetry_service = telemetry_service

    async def execute(self, request: ChatRequestDTO) -> ChatResponseDTO:
        session_id = request.session_id or str(uuid.uuid4())

        # Start telemetry trace if telemetry service is present
        trace = (
            self.telemetry_service.start_trace(session_id=session_id)
            if self.telemetry_service
            else None
        )
        trace_id = trace.trace_id if trace else None

        try:
            # 1. Fetch existing session or create new one
            session = await self.chat_repository.get_session(session_id)
            if not session:
                session = ChatSession(session_id=session_id)

            # 2. Append user message
            session.add_message(role="user", content=request.message)

            # 2.1 Apply input guardrail
            guardrail_result = await self.input_guardrail.evaluate_prompt(request.message)

            if trace_id and self.telemetry_service:
                g_category = guardrail_result.category.value if hasattr(guardrail_result.category, "value") else (str(guardrail_result.category) if guardrail_result.category else None)
                self.telemetry_service.record_guardrail_eval(
                    trace_id=trace_id,
                    guardrail_data=GuardrailSpan(
                        evaluated=True,
                        blocked=guardrail_result.blocked,
                        category=g_category,
                        block_message=guardrail_result.block_message,
                        latency_ms=getattr(guardrail_result, "latency_ms", 0.0),
                        tokens=TokenUsage(
                            prompt_tokens=getattr(guardrail_result, "prompt_tokens", 0),
                            completion_tokens=getattr(guardrail_result, "completion_tokens", 0),
                            total_tokens=getattr(guardrail_result, "total_tokens", 0),
                        ),
                    ),
                )

            if guardrail_result.blocked:
                session.add_message(role="assistant", content=guardrail_result.block_message)
                await self.chat_repository.save_session(session)

                final_trace = (
                    self.telemetry_service.finalize_trace(trace_id=trace_id, status="blocked")
                    if trace_id and self.telemetry_service
                    else None
                )

                telemetry_dto = (
                    TelemetryDTO(
                        trace_id=final_trace.trace_id,
                        total_tokens=final_trace.total_tokens.total_tokens,
                        prompt_tokens=final_trace.total_tokens.prompt_tokens,
                        completion_tokens=final_trace.total_tokens.completion_tokens,
                        latency_ms=final_trace.total_latency_ms,
                        tools_called_count=len(final_trace.tool_calls),
                        guardrail_blocked=True,
                        guardrail_category=final_trace.guardrail.category if final_trace.guardrail else None,
                    )
                    if final_trace
                    else None
                )

                return ChatResponseDTO(
                    session_id=session_id,
                    response=guardrail_result.block_message,
                    history=[
                        ChatMessageDTO(
                            role=msg.role,
                            content=msg.content,
                            timestamp=msg.timestamp,
                        )
                        for msg in session.messages
                    ],
                    telemetry=telemetry_dto,
                )

            # 3. Generate response using LLM port
            assistant_reply = await self.llm_service.generate_response(
                prompt=request.message,
                history=session.messages[:-1],  # history prior to current message
                tools=self.tools,
                trace_id=trace_id,
                telemetry_service=self.telemetry_service,
            )

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

            final_trace = (
                self.telemetry_service.finalize_trace(trace_id=trace_id, status="success")
                if trace_id and self.telemetry_service
                else None
            )

            telemetry_dto = (
                TelemetryDTO(
                    trace_id=final_trace.trace_id,
                    total_tokens=final_trace.total_tokens.total_tokens,
                    prompt_tokens=final_trace.total_tokens.prompt_tokens,
                    completion_tokens=final_trace.total_tokens.completion_tokens,
                    latency_ms=final_trace.total_latency_ms,
                    tools_called_count=len(final_trace.tool_calls),
                    guardrail_blocked=False,
                    guardrail_category=None,
                )
                if final_trace
                else None
            )

            return ChatResponseDTO(
                session_id=session.session_id,
                response=assistant_reply,
                history=history_dtos,
                telemetry=telemetry_dto,
            )

        except Exception as exc:
            if trace_id and self.telemetry_service:
                self.telemetry_service.finalize_trace(
                    trace_id=trace_id, status="error", error=str(exc)
                )
            raise exc

