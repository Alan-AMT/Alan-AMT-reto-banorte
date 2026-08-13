from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from domain.ports.telemetry_port import TelemetryPort
from infrastructure.api.dependencies import get_telemetry_service

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])


@router.get(
    "/traces",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Get all in-memory telemetry execution traces",
    description="Retrieves a list of all captured LLM traces including token usage, latencies, tool calls, and guardrail results.",
)
async def get_all_traces(
    telemetry_service: TelemetryPort = Depends(get_telemetry_service),
) -> List[Dict[str, Any]]:
    traces = telemetry_service.get_traces()
    return [t.to_dict() for t in traces]


@router.get(
    "/traces/{trace_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get specific telemetry trace by trace ID",
)
async def get_trace_by_id(
    trace_id: str,
    telemetry_service: TelemetryPort = Depends(get_telemetry_service),
) -> Dict[str, Any]:
    trace = telemetry_service.get_trace(trace_id)
    if not trace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trace with ID '{trace_id}' not found.",
        )
    return trace.to_dict()


@router.delete(
    "/traces",
    status_code=status.HTTP_200_OK,
    summary="Clear all in-memory telemetry execution traces",
)
async def clear_all_traces(
    telemetry_service: TelemetryPort = Depends(get_telemetry_service),
):
    telemetry_service.clear_traces()
    return {"status": "success", "message": "All traces cleared"}

