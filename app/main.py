from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.auth.repository import AuthRepository
from app.article.repository import ArticleRepository
from app.config import settings
from app.db import connect_to_mongo, close_mongo_connection
from app.notifications.repository import EmailNotificationRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()

    auth_repository = AuthRepository()
    await auth_repository.create_indexes()

    article_repository = ArticleRepository()
    await article_repository.create_indexes()

    email_notification_repository = EmailNotificationRepository()
    await email_notification_repository.create_indexes()

    yield

    await close_mongo_connection()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
        swagger_ui_parameters={
            "persistAuthorization": True,
        },
    )
    app.include_router(api_router)
    return app


app = create_app()