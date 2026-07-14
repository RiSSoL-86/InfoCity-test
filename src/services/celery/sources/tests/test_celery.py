from app_settings import settings
from services.celery import create_celery_app


def test_create_celery_app_uses_settings() -> None:
    """Create Celery with configured transport and task modules."""
    app = create_celery_app()

    assert app.conf.broker_url == settings.celery.broker_url
    assert app.conf.result_backend == settings.celery.result_backend
    assert app.conf.task_track_started is settings.celery.task_track_started
    assert "services.celery.sources.tasks" in app.conf.include
