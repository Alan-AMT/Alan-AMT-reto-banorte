from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.api.v1.chat_router import router as chat_router
from infrastructure.config.settings import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Blueprint for FastAPI Hexagonal Architecture with Domain, Application, and Infrastructure layers.",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Chat Router at root /chat and /api/v1/chat
app.include_router(chat_router)
app.include_router(chat_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
