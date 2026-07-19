from __future__ import annotations

import json, logging
import httpx
from .models import Repository

LOG=logging.getLogger(__name__)
def fallback_analysis(r: Repository) -> dict:
    desc=r.description or "一个仍需阅读官方说明进一步确认定位的开源项目"
    return {"summary":f"{r.name} 是{r.category}领域项目。{desc}","why_hot":f"近期提交活跃，综合热度得分 {r.score:.1f}；本周新增 Star {r.weekly_stars}。首次运行时增长数字可能为估算。",
      "principle":"通过可复用的开源组件、命令行或服务接口完成核心任务；具体架构以官方文档为准。","features":["提供可复用的核心能力和公开源码","README 包含安装或使用线索","社区可通过 Issue 与 PR 协作","支持从最小示例逐步扩展"],
      "scenarios":["学生：用最小示例理解该领域的工程结构","程序员：在测试环境验证后集成到个人项目","团队：用于原型评估和技术选型对比"],"audience":"适合有一定编程基础的用户、专业开发者和评估型团队；零基础用户应优先选择带安装包或图形界面的项目。",
      "quickstart":["阅读官方 README 并确认系统要求","在隔离环境按官方命令安装","运行最小示例或演示项目","验证数据、权限和许可证后再扩大使用"],
      "pros":["近期活跃","源码透明","可从小规模试用"],"limitations":["热门不等于稳定","安装方式可能随版本变化","生产使用前需要安全审计"],"platforms":"以官方 README 为准，通常支持 Windows、macOS 或 Linux 中的部分平台","difficulty":"中等","production":"需完成版本锁定、安全审计和压力测试后再决定",
      "ratings":{"热度":min(5,round(r.score/20,1)),"实用性":4.0,"创新性":3.8,"易用性":3.2,"项目成熟度":min(5,2.5+r.stars/30000),"推荐指数":min(5,round(r.score/20,1))}}

class Analyzer:
    def __init__(self,key:str,model:str): self.key=key; self.model=model
    def analyze(self,r:Repository)->dict:
        base=fallback_analysis(r)
        if not self.key: return base
        prompt=f"用中文分析 GitHub 项目并只返回 JSON，字段与示例完全一致：{json.dumps(base,ensure_ascii=False)}。项目元数据：{r.model_dump_json(exclude={'readme','analysis'})}。README 摘要：{r.readme[:8000]}。不要复制 README，不确定处明确说明。"
        try:
            res=httpx.post("https://api.openai.com/v1/responses",headers={"Authorization":f"Bearer {self.key}"},json={"model":self.model,"input":prompt},timeout=60); res.raise_for_status(); data=res.json()
            text=data.get("output_text") or "".join(c.get("text","") for o in data.get("output",[]) for c in o.get("content",[]) if c.get("type")=="output_text")
            parsed=json.loads(text[text.find("{"):text.rfind("}")+1]); return {**base,**parsed}
        except Exception as exc: LOG.warning("AI 分析失败，使用规则分析: %s",exc); return base
