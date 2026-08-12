import os
from typing import List, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

from domain.entities.chat import ChatMessage, Role, TextPart, ToolCallPart, ToolResultPart
from domain.ports.llm_service_port import LLMServicePort
from domain.ports.tool_port import ToolPort


def from_gemini(content: types.Content) -> ChatMessage:
    """Converts a Google GenAI Content object into a domain ChatMessage."""
    parts = []
    if content.parts:
        for part in content.parts:
            if part.text:
                parts.append(TextPart(part.text))
            elif part.function_call:
                parts.append(
                    ToolCallPart(
                        name=part.function_call.name,
                        args=dict(part.function_call.args),
                    )
                )
            elif part.function_response:
                parts.append(
                    ToolResultPart(
                        name=part.function_response.name,
                        result=part.function_response.response,
                    )
                )

    if content.role == "user":
        role = Role.USER
    elif content.role == "context":
        role = Role.TOOL
    else:
        role = Role.ASSISTANT

    return ChatMessage(role=role, parts=parts)


class GeminiLLMAdapter(LLMServicePort):
    def __init__(self, api_key: str = None, model_name: str = "gemini-3.5-flash-lite"):
        if not api_key:
            load_dotenv()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name

    @property
    def client(self):
        if not self.api_key:
            return None
        return genai.Client(api_key=self.api_key)

    def _ensure_client(self):
        if not self.client:
            raise ValueError(
                "Google GenAI Client is not initialized. Please set the GEMINI_API_KEY environment variable."
            )

    def _map_to_google_contents(self, history: list[ChatMessage]) -> list[types.Content]:
        """Maps domain ChatMessage list to Google GenAI Content types."""
        google_contents = []
        for msg in history:
            if msg.role == Role.USER or msg.role == "user":
                role = "user"
            elif msg.role == Role.TOOL or msg.role == "tool" or msg.role == "context":
                role = "context"
            else:
                role = "model"

            parts = []
            if hasattr(msg, "parts") and msg.parts:
                for part in msg.parts:
                    if isinstance(part, TextPart):
                        parts.append(types.Part.from_text(text=part.text))
                    elif isinstance(part, ToolCallPart):
                        parts.append(types.Part.from_function_call(name=part.name, args=part.args))
                    elif isinstance(part, ToolResultPart):
                        res = part.result if isinstance(part.result, dict) else {"result": part.result}
                        parts.append(types.Part.from_function_response(name=part.name, response=res))
                        role = "context"
            else:
                parts.append(types.Part.from_text(text=msg.content))

            google_contents.append(
                types.Content(
                    role=role,
                    parts=parts
                )
            )
        return google_contents

    async def generate_response(
        self,
        prompt: str,
        history: list[ChatMessage],
        tools: Optional[list[ToolPort]] = None,
        max_iterations: int = 10,
    ) -> str:
        self._ensure_client()

        user_message = ChatMessage(role=Role.USER, content=prompt)
        contents = self._map_to_google_contents(history + [user_message])

        tools_dict = {t.name: t for t in tools} if tools else {}

        google_tools = []
        if tools:
            declarations = [
                types.FunctionDeclaration(
                    name=t.name,
                    description=t.description,
                    parameters=t.args_schema,
                )
                for t in tools
            ]
            google_tools = [types.Tool(function_declarations=declarations)]

        system_instruction = """
        # Identidad

        Eres el agente profesional de Alan Muñoz. Tu propósito es representar su trayectoria profesional mediante una conversación clara, natural y útil.

        Tu función principal es ayudar a otras personas a conocer:
        - Su experiencia profesional.
        - Sus habilidades técnicas y profesionales.
        - Sus proyectos y logros.
        - Su formación académica.
        - Sus intereses profesionales.
        - Los puestos, oportunidades o tipos de trabajo que busca.
        - Su experiencia con tecnologías, herramientas y metodologías.

        # Personalidad

        - Profesional, pero cercano y natural.
        - Claro y directo.
        - Seguro de la información que conoces, pero nunca inventes datos.
        - Responde de forma conversacional, evitando sonar como un CV copiado.
        - Sé breve cuando la pregunta sea sencilla y más detallado cuando sea necesario.
        - Cuando sea útil, relaciona experiencias, habilidades y proyectos para dar contexto.

        # Reglas de información

        1. Responde únicamente utilizando la información disponible en el contexto, CV, documentos o fuentes proporcionadas por el sistema o las herramientas.

        2. Nunca inventes:
        - Experiencias laborales.
        - Empresas.
        - Cargos.
        - Fechas.
        - Tecnologías.
        - Proyectos.
        - Logros.
        - Certificaciones.
        - Información personal.

        3. Si no tienes suficiente información para responder, dilo claramente:
        "No tengo información suficiente sobre ese punto en mi perfil."

        # Alcance

        Tu conversación está limitada principalmente al perfil profesional de Alan Muñoz.

        # Estilo de respuesta

        - Usa español por defecto.
        - Si el usuario escribe en inglés, puedes responder en inglés.
        - Utiliza listas cuando ayuden a organizar información.
        - Evita respuestas excesivamente largas.
        """

        for iteration in range(max_iterations):
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.0,
                    tools=google_tools if google_tools else None,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(
                        disable=True
                    )
                ),
                contents=contents,
            )

            if not response.candidates or not response.candidates[0].content or not response.candidates[0].content.parts:
                raise ValueError("Empty response received from Google Gemini API.")

            # Check if Gemini decided to call a function/tool
            if response.function_calls:
                call = response.function_calls[0]
                print(f"[AgentLoop] Gemini solicitó ejecutar la herramienta: {call.name} con args: {call.args}")

                # 1. Guardar la solicitud del modelo en el historial de llamadas Gemini
                google_content = response.candidates[0].content
                contents.append(google_content)

                # 2. Buscar la herramienta correspondiente
                tool = tools_dict.get(call.name)
                if not tool:
                    raise ValueError(f"Herramienta no encontrada: {call.name}")

                # 3. Ejecutar la herramienta manualmente
                try:
                    result = await tool.run(**call.args)
                except Exception as e:
                    print(f"Error al ejecutar tool {call.name}: {e}")
                    result = f"Error al ejecutar la herramienta {call.name}: {str(e)}"

                # 4. Construir la respuesta de la función para el modelo (rol context)
                res_dict = result if isinstance(result, dict) else {"result": result}
                function_response_part = types.Part.from_function_response(
                    name=call.name,
                    response=res_dict
                )
                tool_response_content = types.Content(role="context", parts=[function_response_part])
                contents.append(tool_response_content)
            else:
                # No hay llamadas a herramientas, retornamos el texto final
                return response.text
        else:
            raise ValueError(f"Se alcanzó el límite máximo de iteraciones ({max_iterations}) en el Agent Loop.")