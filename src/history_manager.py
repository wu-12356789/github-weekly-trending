from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from .models import Repository, Snapshot


class HistoryManager:
    def __init__(self, path: Path): self.path = path
    def load(self) -> dict[str, Snapshot]:
        if not self.path.exists(): return {}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return {k: Snapshot.model_validate(v) for k, v in data.items()}
        except (json.JSONDecodeError, ValueError): return {}
    def apply_growth(self, repos: list[Repository]) -> None:
        old = self.load()
        for repo in repos:
            prev = old.get(repo.full_name)
            repo.weekly_stars = max(0, repo.stars - prev.stars) if prev else 0
            repo.weekly_forks = max(0, repo.forks - prev.forks) if prev else 0
    def save(self, repos: list[Repository], collected_at: datetime) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        existing = self.load()
        for r in repos:
            existing[r.full_name] = Snapshot(full_name=r.full_name, stars=r.stars, forks=r.forks,
                open_issues=r.open_issues, updated_at=r.updated_at, latest_release=r.latest_release,
                collected_at=collected_at)
        self.path.write_text(json.dumps({k: v.model_dump(mode="json") for k,v in existing.items()}, ensure_ascii=False, indent=2), encoding="utf-8")
