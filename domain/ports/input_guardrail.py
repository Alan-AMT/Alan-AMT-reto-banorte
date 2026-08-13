from domain.entities.guardrail import GuardrailResult
from abc import ABC
from abc import abstractmethod

class InputGuardrail(ABC):
    @abstractmethod
    async def evaluate_prompt(self, prompt: str) -> GuardrailResult:
        pass


# class OutputGuardrail(ABC):
#     @abstractmethod
#     async def evaluate_response(self, response: str) -> GuardrailResult:
#         pass