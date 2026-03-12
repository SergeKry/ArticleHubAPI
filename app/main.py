from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.db import connect_to_mongo, close_mongo_connection
from app.routes.items import router as items_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
)

app.include_router(items_router)


@app.get("/")
async def root():
    return {"message": "FastAPI + MongoDB is running"}