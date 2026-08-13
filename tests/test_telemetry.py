import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

from domain.entities.telemetry import GuardrailSpan, TokenUsage, ToolCallRecord
from domain.entities.guardrail import GuardrailResult, BlockedCategory
from infrastructure.adapters.in_memory_telemetry_adapter import InMemoryTelemetryAdapter
from application.use_cases.chat_use_case import SendChatMessageUseCase
from application.dtos.chat_dto import ChatRequestDTO
from main import app


def test_in_memory_telemetry_adapter_lifecycle():
    adapter = InMemoryTelemetryAdapter(enable_console_logging=False)
    trace = adapter.start_trace(session_id="test-session-123")
    assert trace.trace_id is not None
    assert trace.session_id == "test-session-123"

    # Record Guardrail
    adapter.record_guardrail_eval(
        trace.trace_id,
        GuardrailSpan(
            evaluated=True,
            blocked=False,
            category=None,
            latency_ms=15.5,
            tokens=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
        ),
    )

    # Record Tool Execution
    adapter.record_tool_execution(
        trace.trace_id,
        ToolCallRecord(
            tool_name="search_cv",
            args={"query": "python"},
            result_summary="Found 2 chunks",
            latency_ms=120.0,
            success=True,
        ),
    )

    # Record LLM Execution
    adapter.record_llm_execution(
        trace.trace_id,
        tokens=TokenUsage(prompt_tokens=50, completion_tokens=30, total_tokens=80),
        latency_ms=450.0,
    )

    # Finalize Trace
    final_trace = adapter.finalize_trace(trace.trace_id, status="success")
    assert final_trace is not None
    assert final_trace.status == "success"
    assert final_trace.total_tokens.prompt_tokens == 60  # 10 + 50
    assert final_trace.total_tokens.completion_tokens == 35  # 5 + 30
    assert final_trace.total_tokens.total_tokens == 95  # 15 + 80
    assert len(final_trace.tool_calls) == 1
    assert final_trace.tool_calls[0].tool_name == "search_cv"

    # To Dict (JSON representation check)
    t_dict = final_trace.to_dict()
    assert t_dict["trace_id"] == trace.trace_id
    assert t_dict["tokens"]["total_tokens"] == 95
    assert t_dict["guardrail"]["blocked"] is False
    assert len(t_dict["tool_calls"]) == 1


@pytest.mark.anyio
async def test_send_chat_message_use_case_telemetry_integration():

    telemetry_service = InMemoryTelemetryAdapter(enable_console_logging=False)
    
    mock_repo = AsyncMock()
    mock_repo.get_session.return_value = None
    mock_repo.save_session.return_value = None

    mock_guardrail = AsyncMock()
    mock_guardrail.evaluate_prompt.return_value = GuardrailResult(
        blocked=False,
        category=None,
        block_message="",
        latency_ms=20.0,
        prompt_tokens=12,
        completion_tokens=4,
        total_tokens=16,
    )

    mock_llm = AsyncMock()
    async def fake_generate_response(prompt, history, tools, trace_id, telemetry_service):
        if trace_id and telemetry_service:
            telemetry_service.record_llm_execution(
                trace_id=trace_id,
                tokens=TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150),
                latency_ms=300.0,
            )
        return "Respuesta simulada de prueba"

    mock_llm.generate_response = AsyncMock(side_effect=fake_generate_response)

    use_case = SendChatMessageUseCase(
        chat_repository=mock_repo,
        llm_service=mock_llm,
        input_guardrail=mock_guardrail,
        tools=[],
        telemetry_service=telemetry_service,
    )

    request = ChatRequestDTO(message="¿Cuál es tu experiencia?", session_id="sess-test")
    response = await use_case.execute(request)

    assert response.telemetry is not None
    assert response.telemetry.total_tokens == 166  # 16 (guardrail) + 150 (llm)
    assert response.telemetry.prompt_tokens == 112  # 12 + 100
    assert response.telemetry.completion_tokens == 54  # 4 + 50
    assert response.telemetry.guardrail_blocked is False

    traces = telemetry_service.get_traces()
    assert len(traces) == 1
    assert traces[0].session_id == "sess-test"


def test_telemetry_fastapi_endpoints():
    client = TestClient(app)

    # Clear traces first
    del_res = client.delete("/telemetry/traces")
    assert del_res.status_code == 200

    # Get traces should be empty
    res = client.get("/telemetry/traces")
    assert res.status_code == 200
    assert res.json() == []

    # Send a chat message via endpoint
    chat_res = client.post(
        "/chat",
        json={"message": "¿Hola cuál es tu nombre?", "session_id": "api-test-session"},
    )
    assert chat_res.status_code == 200
    body = chat_res.json()
    assert "telemetry" in body
    assert body["telemetry"] is not None
    assert "trace_id" in body["telemetry"]

    # Verify endpoint GET /telemetry/traces
    res_traces = client.get("/telemetry/traces")
    assert res_traces.status_code == 200
    traces_list = res_traces.json()
    assert len(traces_list) >= 1
    assert traces_list[0]["session_id"] == "api-test-session"

    # Verify endpoint GET /telemetry/traces/{trace_id}
    trace_id = body["telemetry"]["trace_id"]
    res_single = client.get(f"/telemetry/traces/{trace_id}")
    assert res_single.status_code == 200
    assert res_single.json()["trace_id"] == trace_id
