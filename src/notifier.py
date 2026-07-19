from __future__ import annotations
import logging, smtplib
from email.message import EmailMessage
from pathlib import Path
from .config import Settings
LOG=logging.getLogger(__name__)
def send_email(settings:Settings,report:Path,date:str)->bool:
    required=[settings.smtp_host,settings.smtp_username,settings.smtp_password,settings.report_recipient]
    if not all(required): LOG.info("SMTP 配置不完整，跳过邮件"); return False
    try:
        msg=EmailMessage(); msg["Subject"]=f"GitHub每周热点项目推荐｜{date}"; msg["From"]=settings.smtp_username; msg["To"]=settings.report_recipient; msg.set_content("本周 GitHub 热点项目报告见附件。")
        msg.add_attachment(report.read_bytes(),maintype="application",subtype="vnd.openxmlformats-officedocument.wordprocessingml.document",filename=report.name)
        with smtplib.SMTP(settings.smtp_host,settings.smtp_port,timeout=30) as s: s.starttls(); s.login(settings.smtp_username,settings.smtp_password); s.send_message(msg)
        return True
    except Exception as exc: LOG.warning("邮件发送失败但报告已生成: %s",exc); return False
