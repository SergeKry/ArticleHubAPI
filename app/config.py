from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ArticleHub API"

    # Universal Mongo config
    mongo_url: str | None = None
    mongo_root_username: str | None = None
    mongo_root_password: str | None = None
    mongo_db: str = "myapp"
    mongo_host: str = "mongo"
    mongo_port: int = 27017

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    # Universal Redis config
    redis_url: str | None = None
    redis_host: str = "redis"
    redis_port: int = 6379

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @property
    def resolved_mongo_url(self) -> str:
        if self.mongo_url:
            return self.mongo_url

        if not self.mongo_root_username or not self.mongo_root_password:
            raise ValueError(
                "Either MONGO_URL or both MONGO_ROOT_USERNAME and "
                "MONGO_ROOT_PASSWORD must be provided."
            )

        return (
            f"mongodb://{self.mongo_root_username}:"
            f"{self.mongo_root_password}@{self.mongo_host}:{self.mongo_port}/"
        )

    @property
    def resolved_redis_url(self) -> str:
        if self.redis_url:
            return self.redis_url
        return f"redis://{self.redis_host}:{self.redis_port}/0"


settings = Settings()