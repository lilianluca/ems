from celery import Celery
from celery.schedules import crontab

from src.core.config import settings

celery_app = Celery(
    "ems",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["src.ote.tasks", "src.weather.tasks"],
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
        # Prices are a once-daily auction result: tomorrow's block appears in the
        # early afternoon and never changes afterwards. This frequent schedule is
        # therefore a retry loop, not a refresh — a missed window cannot be
        # recovered, because the upstream API only ever serves today and tomorrow.
        "schedule": crontab(minute="*/30"),
    },
    "fetch-weather-forecasts": {
        "task": "weather.fetch_forecasts",
        "schedule": crontab(minute=0),  # Fetch weather forecasts every hour
    },
}
