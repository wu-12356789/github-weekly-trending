from __future__ import annotations

import base64, io, logging
from pathlib import Path
import httpx
from PIL import Image, ImageDraw, ImageFont
from .models import Repository

LOG=logging.getLogger(__name__)
def font(size):
    for p in [r"C:\Windows\Fonts\msyh.ttc",r"C:\Windows\Fonts\simhei.ttf",r"C:\Windows\Fonts\arial.ttf",
              "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"]:
        try: return ImageFont.truetype(p,size)
        except OSError: pass
    return ImageFont.load_default()
def card(path:Path,title:str,category:str,summary:str,keywords:list[str],audience:str):
    img=Image.new("RGB",(1600,900),(12,29,53)); d=ImageDraw.Draw(img)
    d.rounded_rectangle((90,90,1510,810),35,fill=(242,247,252),outline=(58,142,190),width=5)
    d.text((150,145),title,font=font(64),fill=(15,45,75)); d.text((150,245),category,font=font(34),fill=(24,116,170))
    d.multiline_text((150,330),summary[:90],font=font(34),fill=(35,45,55),spacing=14)
    d.text((150,500),"关键词  "+"  ·  ".join(keywords[:3]),font=font(30),fill=(55,88,110)); d.text((150,590),"适合人群  "+audience[:45],font=font(28),fill=(55,65,75))
    d.text((150,735),"AI / 自动生成的非官方示意信息卡",font=font(22),fill=(110,120,130)); path.parent.mkdir(parents=True,exist_ok=True); img.save(path)
class ImageGenerator:
    def __init__(self,key:str,model:str): self.key=key; self.model=model
    def generate(self,r:Repository,path:Path):
        a=r.analysis; summary=a.get("summary",r.description); keywords=[r.category,r.language,"开源"]
        if self.key:
            try:
                prompt=f"为中文科技周报制作16:9抽象科技插画，主题 {r.name} / {r.category}，表现 {summary[:120]}。不要文字、Logo或软件界面，不要暗示官方宣传。"
                res=httpx.post("https://api.openai.com/v1/images/generations",headers={"Authorization":f"Bearer {self.key}"},json={"model":self.model,"prompt":prompt,"size":"1536x1024","quality":"low"},timeout=120); res.raise_for_status(); path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(base64.b64decode(res.json()["data"][0]["b64_json"])); return
            except Exception as exc: LOG.warning("图片 API 失败，使用信息卡: %s",exc)
        card(path,r.name,r.category,summary,keywords,a.get("audience","开发者"))
    def cover(self,path:Path,date:str): card(path,"GitHub 每周热点项目推荐",date,"本周值得关注的开源项目、趋势与应用建议",["趋势","开源","实用"],"学生 · 开发者 · 团队")
