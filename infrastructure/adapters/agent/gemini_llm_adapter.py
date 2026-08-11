from domain.ports.llm_service_port import LLMServicePort
import os
from dotenv import load_dotenv

from domain.entities.chat import ChatMessage
from domain.ports.llm_service_port import LLMServicePort

from google import genai
from google.genai import types


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

    async def generate_response(self, prompt: str, history: list[ChatMessage]) -> str:
        self._ensure_client()
        
        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            config=types.GenerateContentConfig(
                system_instruction=f""" 
                """,
                temperature=0.0,
                tools=[],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                )
            ),
            contents=prompt,
        )
        
        return response.text