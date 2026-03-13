from app.core.celery_app import celery_app
from app.article.worker_repository import ArticleWorkerRepository


@celery_app.task(name="app.tasks.article_tasks.analyze_article")
def analyze_article(article_data: dict) -> None:
    content = article_data.get("content", "") or ""
    tags = article_data.get("tags", []) or []

    word_count = len(content.split())
    tag_count = len(set(tags))

    analysis = {
        "word_count": word_count,
        "unique_tags": tag_count,
    }

    repository = ArticleWorkerRepository()
    try:
        repository.attach_analysis(
            article_id=article_data["_id"],
            analysis=analysis,
        )
    finally:
        repository.close()