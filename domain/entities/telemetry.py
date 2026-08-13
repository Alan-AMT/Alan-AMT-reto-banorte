from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def add(self, prompt: int = 0, completion: int = 0, total: Optional[int] = None):
        self.prompt_tokens += prompt
        self.completion_tokens += completion
        self.total_tokens += total if total is not None else (prompt + completion)


@dataclass
class ToolCallRecord:
    tool_name: str
    args: Dict[str, Any] = field(default_factory=dict)
    result_summary: Optional[str] = None
    latency_ms: float = 0.0
    success: bool = True
    error: Optional[str] = None


@dataclass
class GuardrailSpan:
    evaluated: bool = True
    blocked: bool = False
    category: Optional[str] = None
    block_message: Optional[str] = None
    latency_ms: float = 0.0
    tokens: TokenUsage = field(default_factory=TokenUsage)


@dataclass
class TraceRecord:
    trace_id: str
    session_id: str
    start_time: datetime = field(default_factory=utc_now)
    end_time: Optional[datetime] = None
    total_latency_ms: float = 0.0
    guardrail: Optional[GuardrailSpan] = None
    tool_calls: List[ToolCallRecord] = field(default_factory=list)
    llm_tokens: TokenUsage = field(default_factory=TokenUsage)
    total_tokens: TokenUsage = field(default_factory=TokenUsage)
    status: str = "in_progress"  # "in_progress", "success", "blocked", "error"
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert trace record to structured dictionary for JSON logging."""
        return {
            "trace_id": self.trace_id,
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_latency_ms": round(self.total_latency_ms, 2),
            "status": self.status,
            "error": self.error,
            "tokens": {
                "prompt_tokens": self.total_tokens.prompt_tokens,
                "completion_tokens": self.total_tokens.completion_tokens,
                "total_tokens": self.total_tokens.total_tokens,
            },
            "guardrail": {
                "blocked": self.guardrail.blocked if self.guardrail else False,
                "category": self.guardrail.category if self.guardrail else None,
                "latency_ms": round(self.guardrail.latency_ms, 2) if self.guardrail else 0.0,
            } if self.guardrail else None,
            "tool_calls": [
                {
                    "tool_name": t.tool_name,
                    "args": t.args,
                    "latency_ms": round(t.latency_ms, 2),
                    "success": t.success,
                    "error": t.error,
                }
                for t in self.tool_calls
            ],
        }
