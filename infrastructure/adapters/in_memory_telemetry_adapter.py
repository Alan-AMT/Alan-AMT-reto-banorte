import json
import logging
import uuid
from typing import Dict, List, Optional
from domain.entities.telemetry import (
    GuardrailSpan,
    TokenUsage,
    ToolCallRecord,
    TraceRecord,
    utc_now,
)
from domain.ports.telemetry_port import TelemetryPort

logger = logging.getLogger("telemetry")


class InMemoryTelemetryAdapter(TelemetryPort):

    def __init__(self, enable_console_logging: bool = True):
        self._traces: Dict[str, TraceRecord] = {}
        self.enable_console_logging = enable_console_logging

    def start_trace(self, session_id: str, trace_id: Optional[str] = None) -> TraceRecord:
        tid = trace_id or str(uuid.uuid4())
        trace = TraceRecord(trace_id=tid, session_id=session_id, start_time=utc_now())
        self._traces[tid] = trace
        return trace

    def record_guardrail_eval(self, trace_id: str, guardrail_data: GuardrailSpan) -> None:
        trace = self._traces.get(trace_id)
        if not trace:
            return
        trace.guardrail = guardrail_data
        trace.total_tokens.add(
            prompt=guardrail_data.tokens.prompt_tokens,
            completion=guardrail_data.tokens.completion_tokens,
            total=guardrail_data.tokens.total_tokens,
        )

    def record_tool_execution(self, trace_id: str, tool_data: ToolCallRecord) -> None:
        trace = self._traces.get(trace_id)
        if not trace:
            return
        trace.tool_calls.append(tool_data)

    def record_llm_execution(self, trace_id: str, tokens: TokenUsage, latency_ms: float) -> None:
        trace = self._traces.get(trace_id)
        if not trace:
            return
        trace.llm_tokens.add(
            prompt=tokens.prompt_tokens,
            completion=tokens.completion_tokens,
            total=tokens.total_tokens,
        )
        trace.total_tokens.add(
            prompt=tokens.prompt_tokens,
            completion=tokens.completion_tokens,
            total=tokens.total_tokens,
        )

    def finalize_trace(
        self,
        trace_id: str,
        status: str = "success",
        error: Optional[str] = None,
    ) -> Optional[TraceRecord]:
        trace = self._traces.get(trace_id)
        if not trace:
            return None

        trace.end_time = utc_now()
        trace.total_latency_ms = (trace.end_time - trace.start_time).total_seconds() * 1000.0
        trace.status = status
        trace.error = error

        if self.enable_console_logging:
            log_payload = trace.to_dict()
            logger.info(f"[TELEMETRY_TRACE] {json.dumps(log_payload, ensure_ascii=False)}")

        return trace

    def get_traces(self) -> List[TraceRecord]:
        return list(self._traces.values())

    def get_trace(self, trace_id: str) -> Optional[TraceRecord]:
        return self._traces.get(trace_id)
