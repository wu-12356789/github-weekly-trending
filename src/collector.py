from __future__ import annotations

import base64, logging
from datetime import datetime, timedelta, timezone
from .github_client import GitHubClient
from .models import Repository

LOG=logging.getLogger(__name__)
def dt(v): return datetime.fromisoformat(v.replace("Z","+00:00"))

class Collector:
    def __init__(self, client: GitHubClient): self.client=client
    def collect(self, target: int) -> list[Repository]:
        since=(datetime.now(timezone.utc)-timedelta(days=7)).date().isoformat()
        queries=[f"pushed:>={since} stars:>200",f"created:>={since} stars:>20",f"pushed:>={since} topic:ai stars:>50"]
        items={}
        for query in queries:
            try:
                for raw in self.client.get("/search/repositories",{"q":query,"sort":"stars","order":"desc","per_page":min(50,max(20,target*3))})["items"]: items[raw["full_name"]]=raw
            except Exception as exc: LOG.warning("候选查询失败但继续: %s",exc)
        repos=[]
        for raw in list(items.values())[:max(target*5,30)]:
            try: repos.append(self._enrich(raw))
            except Exception as exc: LOG.warning("跳过 %s: %s",raw.get("full_name"),exc)
        if not repos: raise RuntimeError("未采集到仓库；请检查网络或使用 --demo")
        return repos
    def _enrich(self, x):
        full=x["full_name"]; readme=""; release=None
        try:
            rr=self.client.get(f"/repos/{full}/readme",cache_ttl=21600); readme=base64.b64decode(rr.get("content","")).decode("utf-8","ignore")[:16000]
        except Exception: pass
        try: release=self.client.get(f"/repos/{full}/releases/latest",cache_ttl=3600)
        except Exception: pass
        lic=(x.get("license") or {}).get("spdx_id") or "未知"
        return Repository(full_name=full,name=x["name"],description=x.get("description") or "",html_url=x["html_url"],homepage=x.get("homepage") or "",
          docs_url=(x.get("homepage") or x["html_url"]+"#readme"),license=lic,language=x.get("language") or "未知",stars=x.get("stargazers_count",0),forks=x.get("forks_count",0),
          open_issues=x.get("open_issues_count",0),watchers=x.get("watchers_count",0),created_at=dt(x["created_at"]),updated_at=dt(x["updated_at"]),pushed_at=dt(x["pushed_at"]),
          latest_release=(release or {}).get("tag_name","无"),latest_release_at=dt(release["published_at"]) if release and release.get("published_at") else None,
          readme=readme,topics=x.get("topics") or [])

def demo_repositories(count=10):
    now=datetime.now(timezone.utc); cats=[("agent-lab","AI Agent","Python"),("local-llm-kit","人工智能与大模型","Python"),("swift-web","Web 前端","TypeScript"),("cloud-box","后端与云原生","Go"),("data-lens","数据分析","Python"),("auto-flow","自动化工具","Python"),("secure-scan","网络安全","Rust"),("desk-note","桌面软件","TypeScript"),("learn-code","教育与学习","Jupyter Notebook"),("maker-board","开源硬件","C++")]
    out=[]
    for i,(name,cat,lang) in enumerate(cats[:count]):
        r=Repository(full_name=f"demo/{name}",name=name,description=f"用于演示的{cat}开源项目，提供清晰安装教程与可运行示例。",html_url=f"https://github.com/demo/{name}",homepage=f"https://example.com/{name}",docs_url=f"https://example.com/{name}/docs",license="MIT",language=lang,stars=30000-i*1800,forks=2200-i*120,open_issues=80+i*3,created_at=now-timedelta(days=120+i*40),updated_at=now-timedelta(hours=i+1),pushed_at=now-timedelta(hours=i*2+1),latest_release=f"v1.{i}.0",latest_release_at=now-timedelta(days=i+1),readme="# Install\npip install demo\n## Usage\nQuickstart example with Docker and API.\n"*30,topics=[cat,"developer-tools"])
        r.category=cat; r.weekly_stars=850-i*55; r.weekly_forks=70-i*4; out.append(r)
    return out
