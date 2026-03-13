from celery import Celery

from app.config import settings

celery_app = Celery(
    "app",
    broker=settings.resolved_redis_url,
    backend=settings.resolved_redis_url,
)

celery_app.conf.update(
    task_default_queue="default",
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    imports=(
        "app.tasks.email_tasks",
        "app.tasks.article_tasks",
        "app.tasks.analytics_tasks",
    ),
    beat_schedule={
        "collect-total-articles-every-12-hours": {
            "task": "app.tasks.analytics_tasks.collect_total_articles_snapshot",
            "schedule": 60 * 60 * 12,
        },
    },
)