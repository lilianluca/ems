from celery import Celery
from celery.schedules import crontab

from src.core.config import settings

celery_app = Celery(
    "ems",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["src.ote.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    "fetch-ote-prices": {
        "task": "ote.fetch_prices",
        "schedule": crontab(minute="*/30"),
    },
}
