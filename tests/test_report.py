from datetime import datetime
from zoneinfo import ZoneInfo
from zipfile import ZipFile
from src.analyzer import fallback_analysis
from src.collector import demo_repositories
from src.ranking import score_repository
from src.report_generator import ReportGenerator
def test_report_has_docx_and_hyperlinks(tmp_path):
    repos=demo_repositories(2)
    for r in repos: score_repository(r); r.analysis=fallback_analysis(r)
    docx,md=ReportGenerator(tmp_path).generate(repos,datetime.now(ZoneInfo("Asia/Tokyo")),{},False)
    assert docx.exists() and md.exists()
    with ZipFile(docx) as z: rels=z.read("word/_rels/document.xml.rels").decode(); assert "https://github.com/demo/" in rels
