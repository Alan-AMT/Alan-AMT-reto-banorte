import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.adapters.agent.gemini_llm_adapter import GeminiLLMAdapter
from infrastructure.adapters.agent.mock_llm_adapter import MockLLMAdapter
from infrastructure.adapters.in_memory_chat_repository import InMemoryChatRepository
from infrastructure.adapters.tools.search_cv_tool import SearchCVTool
from infrastructure.adapters.gemini_input_guardrail import GeminiInputGuardrail
from infrastructure.adapters.in_memory_telemetry_adapter import InMemoryTelemetryAdapter
from infrastructure.api.v1.chat_router import router as chat_router
from infrastructure.api.v1.telemetry_router import router as telemetry_router
from infrastructure.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    print("Loading dependencies with lifespan...")
    app.state.chat_repository = InMemoryChatRepository()
    app.state.telemetry_service = InMemoryTelemetryAdapter()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        app.state.llm_service = GeminiLLMAdapter(api_key=api_key)
        app.state.input_guardrail = GeminiInputGuardrail(api_key=api_key)
    else:
        app.state.llm_service = MockLLMAdapter(bot_name=settings.BOT_NAME)
    
    tools = []
    if api_key and (os.getenv("PINECONE_KEY") or settings.PINECONE_KEY):
        try:
            search_cv_tool = SearchCVTool()
            tools.append(search_cv_tool)
            print("Registered search_cv tool.")
        except Exception as e:
            print(f"Warning: Could not initialize search_cv tool: {e}")
    app.state.tools = tools

    yield
    print("Closing application...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Blueprint for FastAPI Hexagonal Architecture with Domain, Application, and Infrastructure layers.",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers at root and /api/v1
app.include_router(chat_router)
app.include_router(chat_router, prefix=settings.API_V1_STR)

app.include_router(telemetry_router)
app.include_router(telemetry_router, prefix=settings.API_V1_STR)



@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

