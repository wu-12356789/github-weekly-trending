from __future__ import annotations
import argparse, json, logging
from datetime import datetime
from zoneinfo import ZoneInfo
from .analyzer import Analyzer
from .collector import Collector, demo_repositories
from .config import Settings
from .github_client import GitHubClient
from .history_manager import HistoryManager
from .image_generator import ImageGenerator
from .notifier import send_email
from .ranking import score_repository, select_diverse
from .report_generator import ReportGenerator

def parse_args():
    p=argparse.ArgumentParser(); p.add_argument("--project-count",type=int); p.add_argument("--generate-images",action="store_true"); p.add_argument("--no-images",action="store_true"); p.add_argument("--demo",action="store_true"); return p.parse_args()
def run():
    args=parse_args(); cfg=Settings(); count=args.project_count or cfg.project_count; generate=False if args.no_images else (True if args.generate_images else cfg.generate_images)
    logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s %(name)s: %(message)s"); log=logging.getLogger("weekly")
    now=datetime.now(ZoneInfo(cfg.report_timezone)); history=HistoryManager(cfg.history_path); old=history.load()
    if args.demo: repos=demo_repositories(max(count,10))
    else:
        client=GitHubClient(cfg.github_token,cfg.cache_dir,cfg.request_timeout)
        try: repos=Collector(client).collect(count)
        finally: client.close()
    history.apply_growth(repos)
    for r in repos: score_repository(r,now,has_history=bool(old) or args.demo)
    repos=select_diverse(repos,count); analyzer=Analyzer(cfg.openai_api_key,cfg.openai_model)
    for r in repos:
        try: r.analysis=analyzer.analyze(r)
        except Exception as exc: log.warning("分析失败 %s: %s",r.full_name,exc)
    raw=cfg.root/"data"/"raw"/f"{now.date()}.json"; raw.parent.mkdir(parents=True,exist_ok=True); raw.write_text(json.dumps([r.model_dump(mode="json") for r in repos],ensure_ascii=False,indent=2),encoding="utf-8")
    images={}; image_dir=cfg.root/"output"/"images"/str(now.date()); gen=ImageGenerator(cfg.openai_api_key,cfg.openai_image_model)
    if generate:
        cover=image_dir/"cover.png"; gen.cover(cover,str(now.date())); images["cover"]=cover
        for r in repos[:cfg.image_project_limit]:
            path=image_dir/f"{r.full_name.replace('/','__')}.png"
            try: gen.generate(r,path); images[r.full_name]=path
            except Exception as exc: log.warning("图片失败 %s: %s",r.full_name,exc)
    docx,md=ReportGenerator(cfg.root/"output"/"reports").generate(repos,now,images,bool(old))
    history.save(repos,now); send_email(cfg,docx,str(now.date())); log.info("完成: %s | %s",docx,md); return docx,md
if __name__=="__main__": run()
