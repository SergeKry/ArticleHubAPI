from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ArticleHub API"

    mongo_root_username: str
    mongo_root_password: str
    mongo_db: str = "myapp"
    mongo_host: str = "mongo"
    mongo_port: int = 27017

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @property
    def mongo_url(self) -> str:
        return (
            f"mongodb://{self.mongo_root_username}:"
            f"{self.mongo_root_password}@{self.mongo_host}:{self.mongo_port}/"
        )


settings = Settings()