from typing import Optional
from enum import Enum
from dataclasses import dataclass

class BlockedCategory(str, Enum):
    OFF_TOPIC = "off-topic"
    PROMPT_INJECTION = "prompt-injection"
    TOXIC = "toxic"
    UNSUPPORTED_ACTION = "unsupported-action"

BLOCK_MESSAGES: dict[BlockedCategory, str] = {
    BlockedCategory.OFF_TOPIC: (
        "Prefiero enfocar esta conversación en mi trayectoria profesional. "
        "Pregúntame sobre mi experiencia, proyectos o habilidades técnicas."
    ),
    BlockedCategory.PROMPT_INJECTION: (
        "No puedo seguir esa instrucción. Sigamos hablando sobre mi perfil "
        "profesional — ¿qué te gustaría saber sobre mi experiencia?"
    ),
    BlockedCategory.TOXIC: (
        "Prefiero mantener esta conversación en un tono profesional y respetuoso. "
        "Estoy aquí para hablarte de mi trayectoria — ¿en qué puedo ayudarte?"
    ),
    BlockedCategory.UNSUPPORTED_ACTION: (
        "Eso no lo puedo gestionar directamente aquí, pero puedes escribirme "
        "a alan.munoz.dev@outlook.com y con gusto lo platicamos."
    ),
}

@dataclass
class GuardrailResult:
    blocked: bool
    category: Optional[BlockedCategory]
    block_message: str
    latency_ms: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

