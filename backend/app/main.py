from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.router import api_router
from .core.config import get_settings
from .core.logging import get_logger, setup_logging
from .db.session import init_db

settings = get_settings()
setup_logging(settings.LOG_LEVEL)
logger = get_logger("research_agent.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Research Agent backend...")
    await init_db()
    logger.info(f"Database initialized. Server running on {settings.HOST}:{settings.PORT}")
    yield
    logger.info("Research Agent backend shutting down...")


app = FastAPI(
    title="Research Agent API",
    description="Evidence-grounded autonomous scholarly research agent",
    version="0.1.0",
    lifespan=lifespan,
)

# Narrow CORS configuration for frontend
origins = [
    settings.FRONTEND_ORIGIN,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "research-agent-backend",
        "llm_configured": settings.is_llm_configured,
        "llm_model": settings.LLM_MODEL if settings.is_llm_configured else "discovery-mode",
        "openalex_email": settings.OPENALEX_EMAIL,
        "crossref_mailto": settings.CROSSREF_MAILTO,
    }
