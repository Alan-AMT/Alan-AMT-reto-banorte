import os
import pytest

@pytest.fixture(autouse=True, scope="session")
def mock_env():
    # Force empty API keys so that lifespan initializes mock adapters and mock tools
    # rather than making real external API calls during testing.
    os.environ["GEMINI_API_KEY"] = ""
    os.environ["PINECONE_KEY"] = ""
    os.environ["API_KEY"] = ""
