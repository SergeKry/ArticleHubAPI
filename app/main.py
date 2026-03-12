from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.auth.repository import AuthRepository
from app.config import settings
from app.db import connect_to_mongo, close_mongo_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()

    repository = AuthRepository()
    await repository.create_indexes()

    yield

    await close_mongo_connection()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(api_router)