from datetime import datetime,timezone,timedelta
from src.models import Repository
from src.ranking import score_repository,select_diverse
def repo(name,stars,weekly,cat):
    now=datetime.now(timezone.utc); r=Repository(full_name=f"x/{name}",name=name,description="tool",html_url="https://github.com/x/y",stars=stars,weekly_stars=weekly,created_at=now-timedelta(days=30),updated_at=now,pushed_at=now,readme="install usage example docker "*100); r.category=cat; return r
def test_growth_increases_score():
    a,b=repo("a",1000,500,"AI Agent"),repo("b",1000,5,"AI Agent"); assert score_repository(a)>score_repository(b)
def test_diversity_limit():
    rs=[repo(str(i),10000-i,100-i,"AI Agent" if i<4 else "数据分析") for i in range(6)]
    for i,r in enumerate(rs): r.score=100-i
    picked=select_diverse(rs,4,max_per_category=2); assert sum(r.category=="AI Agent" for r in picked)<=2
