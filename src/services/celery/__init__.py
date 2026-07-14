from celery import Celery

from app_settings import settings


def create_celery_app() -> Celery:
    """Create a configured Celery application."""
    app = Celery(
        "infocity",
        broker=settings.celery.broker_url,
        backend=settings.celery.result_backend,
        include=["services.celery.sources.tasks"],
    )
    app.conf.task_track_started = settings.celery.task_track_started
    return app


celery_app = create_celery_app()
