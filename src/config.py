from __future__ import annotations

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    github_token: str = ""
    openai_api_key: str = ""
    report_timezone: str = "Asia/Tokyo"
    project_count: int = Field(10, ge=1, le=30)
    generate_images: bool = True
    image_project_limit: int = Field(10, ge=0, le=30)
    report_language: str = "zh-CN"
    openai_model: str = "gpt-5.6-terra"
    openai_image_model: str = "gpt-image-2"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    report_recipient: str = ""
    request_timeout: float = 20.0
    root: Path = Path(__file__).resolve().parents[1]

    @property
    def history_path(self) -> Path: return self.root / "data" / "repository_history.json"
    @property
    def cache_dir(self) -> Path: return self.root / ".cache"
