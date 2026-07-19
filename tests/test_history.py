from datetime import datetime,timezone,timedelta
from src.collector import demo_repositories
from src.history_manager import HistoryManager
def test_history_growth(tmp_path):
    h=HistoryManager(tmp_path/"history.json"); repos=demo_repositories(1); h.save(repos,datetime.now(timezone.utc)); repos[0].stars+=42; repos[0].forks+=3; h.apply_growth(repos); assert repos[0].weekly_stars==42 and repos[0].weekly_forks==3
