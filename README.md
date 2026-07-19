# GitHub 每周热点项目推荐系统

每周采集 GitHub 候选仓库，结合历史快照计算真实周增长与综合热度，输出中文 Word/Markdown 科技周报。默认每周五日本时间 16:00（UTC 07:00）由 GitHub Actions 执行。

## 目标、范围与验收

- 真实模式调用 GitHub REST API；`--demo` 使用内置模拟数据，适合首次验收和无 Token 环境。
- 默认推荐 10 个跨领域项目，保留原始数据、历史快照、评分明细和清晰日志。
- 生成可点击超链接、目录、页码、图片卡片的 `.docx` 与同内容 `.md`。
- OpenAI 和图片生成均为可选增强；没有 Key 时自动使用规则分析与 Pillow 信息卡。
- 单仓库、图片或邮件失败不会中断主报告；网络层带缓存、超时、重试和限流等待。

不包含：绕过 GitHub API 限流、抓取私人仓库、自动执行候选项目代码、对开源项目作安全背书。

## 环境与安装

要求 Python 3.11+。建议创建虚拟环境：

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
```

GitHub Token：在 GitHub Settings → Developer settings → Personal access tokens 创建；只读取公开仓库时使用最小权限。将其配置为本地 `GITHUB_TOKEN` 或仓库 Actions Secret，切勿提交真实密钥。

OpenAI：可选。将平台 API Key 配置为 `OPENAI_API_KEY` 后，系统通过 Responses API 增强中文分析，并使用 `gpt-image-2` 生成配图；未配置时使用规则摘要和本地信息卡。模型可通过 `OPENAI_MODEL`、`OPENAI_IMAGE_MODEL` 修改。

## 本地运行

```bash
python -m src.main
python -m src.main --project-count 10 --generate-images
python -m src.main --project-count 10 --no-images
python -m src.main --demo --project-count 10 --no-images
```

首次建议运行 `--demo`。真实模式会查询近 7 天活跃、新建和发布项目；修改 `PROJECT_COUNT` 调整数量，设置 `GENERATE_IMAGES=false` 或使用 `--no-images` 关闭图片。报告位于 `output/reports/`，图片位于 `output/images/YYYY-MM-DD/`。

## GitHub Actions

工作流 `.github/workflows/weekly-github-trending.yml` 支持手动触发及：

```yaml
cron: "0 7 * * 5"
```

即每周五 UTC 07:00 / `Asia/Tokyo` 16:00。修改定时时只需调整 cron（GitHub Actions cron 始终按 UTC）。运行结束后，在 Actions → 对应运行 → Artifacts 下载 Word/Markdown 报告。

建议配置 Secrets：

- 必需（真实采集推荐）：`GITHUB_TOKEN`（工作流也会回退到内置 `github.token`）
- 可选增强：`OPENAI_API_KEY`
- 可选邮件：`SMTP_HOST`、`SMTP_PORT`、`SMTP_USERNAME`、`SMTP_PASSWORD`、`REPORT_RECIPIENT`

邮件配置完整时发送 Word 附件；缺任一项则记录并跳过。企业微信、钉钉、Telegram、Discord、Slack 可在 `src/notifier.py` 的通知接口上扩展。

## 数据与评分

综合分满分 100：周新增 Star 22、异常增速 10、总 Star 8、提交活跃 12、Release 新鲜度 8、Issue/PR 活跃 8、Fork 周增长 5、项目新鲜度 5、README 质量 10、安装/示例 5、维护状态 5、实际价值 2。首次无历史快照时使用近期活跃、创建/发布新鲜度与当前规模的代理指标，并在报告中标注估算。

为避免榜单单一，最终选择会限制同一分类默认最多 3 个；明显热点不足时自动放宽。历史保存于 `data/repository_history.json`，原始采集数据保存于 `data/raw/YYYY-MM-DD.json`。

## 测试与排错

```bash
pytest -q
python -m src.main --demo --project-count 3 --no-images
```

- GitHub 403：检查 Token、API rate limit 和 Actions permissions。
- OpenAI 失败：确认 Key/额度/模型权限；系统会自动降级，不影响报告。
- 中文字体缺失：安装微软雅黑、黑体、宋体或 Noto Sans CJK；信息卡会自动寻找可用字体。
- Word 目录未刷新：在 Word 中按 `Ctrl+A`、`F9` 更新字段；报告同时包含静态目录文字以便无头环境阅读。
- SMTP 失败：检查端口和 STARTTLS；邮件失败只记录警告。
- 网络不稳定：缓存保存在 `.cache/`，可稍后重试；不要删除历史文件，否则无法计算真实周增长。

## 维护说明

模型、权重和分类关键词集中配置；网络、分析、图片、报告、通知与历史模块解耦。新增通知渠道应实现独立函数，保持失败隔离。许可证为 MIT。
