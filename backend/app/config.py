"""Nexus-Lore 应用配置"""
from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ---- Database ----
    database_url: str = "postgresql+asyncpg://nexus:nexus_pass@localhost:5432/nexus_lore"

    # ---- AI Provider ----
    ai_provider: str = "ollama"
    ai_api_key: str | None = None
    ai_endpoint: str = "http://localhost:11434"
    ai_model: str = "llama3"

    # ---- App ----
    app_name: str = "Nexus-Lore API"
    debug: bool = True
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
