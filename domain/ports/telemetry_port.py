from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.telemetry import GuardrailSpan, TokenUsage, ToolCallRecord, TraceRecord


class TelemetryPort(ABC):

    @abstractmethod
    def start_trace(self, session_id: str, trace_id: Optional[str] = None) -> TraceRecord:
        """Starts a new trace session."""
        pass

    @abstractmethod
    def record_guardrail_eval(self, trace_id: str, guardrail_data: GuardrailSpan) -> None:
        """Records guardrail evaluation metrics into an active trace."""
        pass

    @abstractmethod
    def record_tool_execution(self, trace_id: str, tool_data: ToolCallRecord) -> None:
        """Records tool execution details into an active trace."""
        pass

    @abstractmethod
    def record_llm_execution(self, trace_id: str, tokens: TokenUsage, latency_ms: float) -> None:
        """Records LLM token consumption and generation latency into an active trace."""
        pass

    @abstractmethod
    def finalize_trace(
        self,
        trace_id: str,
        status: str = "success",
        error: Optional[str] = None,
    ) -> Optional[TraceRecord]:
        """Finalizes the trace, calculates total duration/tokens, logs structured JSON, and returns the trace."""
        pass

    @abstractmethod
    def get_traces(self) -> List[TraceRecord]:
        """Retrieves all stored trace records."""
        pass

    @abstractmethod
    def get_trace(self, trace_id: str) -> Optional[TraceRecord]:
        """Retrieves a specific trace by trace_id."""
        pass

    @abstractmethod
    def clear_traces(self) -> None:
        """Clears all stored trace records."""
        pass