from domain.ports.input_guardrail import InputGuardrail
from domain.entities.guardrail import GuardrailResult

class MockInputGuardrail(InputGuardrail):
    async def evaluate_prompt(self, prompt: str) -> GuardrailResult:
        # Mock class never blocks and returns 0 latency/tokens
        return GuardrailResult(
            blocked=False,
            category=None,
            block_message="",
            latency_ms=0.0,
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0
        )
