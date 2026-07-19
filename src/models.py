from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class Repository(BaseModel):
    full_name: str
    name: str
    description: str = ""
    html_url: str
    homepage: str = ""
    docs_url: str = ""
    license: str = "未知"
    language: str = "未知"
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    watchers: int = 0
    created_at: datetime
    updated_at: datetime
    pushed_at: datetime
    latest_release: str = "无"
    latest_release_at: datetime | None = None
    readme: str = ""
    topics: list[str] = Field(default_factory=list)
    weekly_stars: int = 0
    weekly_forks: int = 0
    score: float = 0
    category: str = "编程开发工具"
    score_details: dict[str, float] = Field(default_factory=dict)
    analysis: dict = Field(default_factory=dict)


class Snapshot(BaseModel):
    full_name: str
    stars: int
    forks: int
    open_issues: int
    updated_at: datetime
    latest_release: str = "无"
    collected_at: datetime
