from app.core.celery_app import celery_app
from app.notifications.worker_repository import EmailNotificationWorkerRepository


@celery_app.task(name="app.tasks.email_tasks.log_welcome_email")
def log_welcome_email(
    user_id: str,
    email: str,
    name: str,
) -> None:
    repository = EmailNotificationWorkerRepository()
    try:
        subject = "Welcome to the Article Hub"
        body = f"Hello {name}, welcome to the Article Hub."

        repository.create_email_log(
            user_id=user_id,
            email=email,
            subject=subject,
            body=body,
        )
    finally:
        repository.close()