import pytest
from domain.entities.chat import ChatMessage, Role
from domain.ports.tool_port import ToolPort
from infrastructure.adapters.agent.mock_llm_adapter import MockLLMAdapter


class DummyTool(ToolPort):
    name = "get_weather"
    description = "Gets the weather for a location."
    args_schema = {
        "type": "OBJECT",
        "properties": {
            "location": {"type": "STRING", "description": "City name"}
        },
        "required": ["location"],
    }

    async def run(self, location: str = "") -> str:
        return f"Weather in {location} is 25C and sunny."


@pytest.mark.anyio
async def test_mock_llm_adapter_with_tools():
    adapter = MockLLMAdapter(bot_name="TestBot")
    tool = DummyTool()
    response = await adapter.generate_response(
        prompt="What is the weather in Monterrey?",
        history=[ChatMessage(role=Role.USER, content="Hello")],
        tools=[tool]
    )
    assert "TestBot" in response
    assert "1 herramientas disponibles" in response
