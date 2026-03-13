from app.core.celery_app import celery_app
from app.analytics.worker_repository import AnalyticsWorkerRepository


@celery_app.task(name="app.tasks.analytics_tasks.collect_total_articles_snapshot")
def collect_total_articles_snapshot() -> None:
    repository = AnalyticsWorkerRepository()
    try:
        total_articles = repository.count_articles()
        repository.create_snapshot(
            metric="total_articles",
            value=total_articles,
        )
    finally:
        repository.close()