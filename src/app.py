from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app_settings import settings
from services.api.router import router as api_router
from services.celery import celery_app
from services.rag.embeddings import EmbeddingService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize application dependencies."""
    embeddings = EmbeddingService(
        model_name=settings.embedding.model_name,
    )
    embeddings.initialize()

    app.state.embeddings = embeddings
    app.state.celery = celery_app
    yield


app = FastAPI(
    title=settings.app.project_name,
    debug=settings.app.debug,
    lifespan=lifespan,
)
app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
