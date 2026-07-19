from __future__ import annotations

import hashlib, json, logging, time
from pathlib import Path
import httpx

LOG = logging.getLogger(__name__)

class GitHubClient:
    def __init__(self, token: str, cache_dir: Path, timeout: float = 20):
        self.cache_dir=cache_dir; cache_dir.mkdir(parents=True, exist_ok=True)
        headers={"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","User-Agent":"github-weekly-trending"}
        if token: headers["Authorization"] = f"Bearer {token}"
        self.client=httpx.Client(base_url="https://api.github.com", headers=headers, timeout=timeout)
    def get(self, path: str, params: dict | None=None, cache_ttl: int=1800):
        key=hashlib.sha256((path+json.dumps(params or {},sort_keys=True)).encode()).hexdigest(); file=self.cache_dir/f"{key}.json"
        if file.exists() and time.time()-file.stat().st_mtime < cache_ttl:
            return json.loads(file.read_text(encoding="utf-8"))
        last=None
        for attempt in range(4):
            try:
                res=self.client.get(path,params=params)
                if res.status_code in (403,429):
                    reset=int(res.headers.get("x-ratelimit-reset",time.time()+2)); time.sleep(min(30,max(1,reset-int(time.time())))); continue
                if 400 <= res.status_code < 500:
                    raise RuntimeError(f"GitHub 返回不可重试状态 {res.status_code}: {path}")
                res.raise_for_status(); data=res.json(); file.write_text(json.dumps(data,ensure_ascii=False),encoding="utf-8"); return data
            except (httpx.HTTPError, json.JSONDecodeError) as exc:
                last=exc; time.sleep(2**attempt)
        raise RuntimeError(f"GitHub 请求失败: {path}: {last}")
    def close(self): self.client.close()
