from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "念想 API"
    app_env: str = "development"
    secret_key: str = Field(default="ABC")
    access_token_expire_minutes: int = 60 * 24 * 7
    database_url: str = "mysql+pymysql://ABC:ABC@localhost:3306/nianxiang?charset=utf8mb4"
    dashscope_api_key: str = ""
    qwen_model: str = "qwen-plus"
    frontend_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.frontend_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
