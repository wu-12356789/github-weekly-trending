from __future__ import annotations

import math
from datetime import datetime, timezone
from .models import Repository

CATEGORIES = {
 "人工智能与大模型": ["llm","machine-learning","deep-learning","ai"], "AI Agent": ["agent","agents","mcp"],
 "Web 前端": ["react","vue","frontend","typescript"], "后端与云原生": ["kubernetes","docker","backend","cloud"],
 "数据分析": ["data","analytics","database"], "自动化工具": ["automation","workflow"],
 "网络安全": ["security","pentest"], "桌面软件": ["desktop","electron"], "移动开发": ["android","ios","mobile"],
 "效率工具": ["productivity","cli"], "教育与学习": ["education","tutorial","awesome"], "创意设计": ["design","creative"],
 "开源硬件": ["hardware","arduino","robot"], "编程开发工具": ["developer-tools","compiler","sdk"]}

def categorize(r: Repository) -> str:
    hay = " ".join([r.name, r.description, *r.topics]).lower()
    scores = {c: sum(1 for k in ks if k in hay) for c,ks in CATEGORIES.items()}
    return max(scores, key=scores.get) if max(scores.values()) else "编程开发工具"

def score_repository(r: Repository, now: datetime | None = None, has_history: bool = True) -> float:
    now = now or datetime.now(timezone.utc)
    def days(dt): return max(0.0, (now - dt.astimezone(timezone.utc)).total_seconds()/86400)
    readme = r.readme.lower()
    details = {
      "周新增Star": min(22, math.log1p(r.weekly_stars)*4.0) if has_history else min(12, math.log1p(r.stars)*1.2),
      "异常增速": min(10, (r.weekly_stars/max(r.stars-r.weekly_stars,1))*250) if has_history else max(0, 10-days(r.created_at)/18),
      "总Star": min(8, math.log10(max(r.stars,1))*1.8), "提交活跃": max(0,12-days(r.pushed_at)*0.8),
      "Release新鲜度": max(0,8-days(r.latest_release_at)*0.25) if r.latest_release_at else 0,
      "协作活跃": min(8, math.log1p(r.open_issues)*1.3), "Fork增长": min(5, math.log1p(r.weekly_forks)*1.8),
      "项目新鲜度": max(0,5-days(r.created_at)/90), "README质量": min(10, len(r.readme)/500 + sum(x in readme for x in ["install","usage","example","quickstart"])*1.4),
      "安装与示例": min(5, sum(x in readme for x in ["install","docker","pip ","npm ","example"])),
      "维护状态": max(0,5-days(r.updated_at)*0.3), "实用价值": min(2, 0.5 + bool(r.description)*0.5 + bool(r.homepage)*0.5 + bool(r.license != "未知")*0.5)}
    r.score_details = {k: round(v,2) for k,v in details.items()}; r.score = round(sum(details.values()),2); r.category = categorize(r)
    return r.score

def select_diverse(repos: list[Repository], count: int, max_per_category: int = 3) -> list[Repository]:
    chosen=[]; counts={}
    for r in sorted(repos, key=lambda x:x.score, reverse=True):
        if counts.get(r.category,0) < max_per_category:
            chosen.append(r); counts[r.category]=counts.get(r.category,0)+1
        if len(chosen)==count: return chosen
    for r in sorted(repos, key=lambda x:x.score, reverse=True):
        if r not in chosen: chosen.append(r)
        if len(chosen)==count: break
    return chosen
