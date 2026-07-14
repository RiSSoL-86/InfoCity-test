from importlib import import_module
from unittest.mock import MagicMock, patch

from celery import Celery
from fastapi import FastAPI, Request

from services.api.common.dependencies import get_celery, get_embeddings


async def test_lifespan_initializes_dependencies() -> None:
    """Initialize Celery and embeddings in the FastAPI lifespan."""
    app_module = import_module("app")
    embeddings = MagicMock()

    with patch.object(
        app_module,
        "EmbeddingService",
        return_value=embeddings,
    ):
        async with app_module.lifespan(app_module.app):
            assert app_module.app.state.embeddings is embeddings
            assert app_module.app.state.celery is app_module.celery_app

    embeddings.initialize.assert_called_once_with()


def test_state_dependencies_return_initialized_clients() -> None:
    """Return clients stored in the FastAPI application state."""
    test_app = FastAPI()
    celery = Celery("test")
    embeddings = MagicMock()
    test_app.state.celery = celery
    test_app.state.embeddings = embeddings
    request = Request({"type": "http", "app": test_app})

    assert get_celery(request) is celery
    assert get_embeddings(request) is embeddings
