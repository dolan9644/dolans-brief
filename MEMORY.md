# MEMORY.md — BIBI Agent 持久记忆核心

> 本文件由 sync_config.py 管理 — config.json 是单一真相源
> 可参数化内容（路径、阈值、cron）由 sync 自动更新
> 手写内容（信源列表、排障、方法论）永不覆盖

---

## 技术运营配置

### API 配置
| 服务 | 模型 | 用途 |
|------|------|------|
| - | - | - |

### 数据同步
> 本文件由 `sync_config.py` 管理 — config.json 是单一真相源
> 手动修改 config.json 后运行 `python3 agent/sync_config.py` 同步
## GitHub Pages 部署

- **仓库**: `dolan9644/bibi-intel`
- **CDN**: https://cdn.jsdelivr.net/gh/dolan9644/bibi-intel@main/docs/
## 飞书推送工作流

- **群组**: `oc_ed18b6ceeaccabc19fceb48b66e0e091`
- **用户 ID**: `ou_3a88b7b21440fb9d99cd0b4399f64b3a`
- **铁律**: 卡片退给我才算完成

推送后等用户确认收到，才算闭环。
## ⚠️ 重要已知问题 & 排障记录（2026-03-23 最新）

| 问题 | 根因 | 状态 |
|------|------|------|
| YouTube 字幕提取全量失败 | YouTube InnerTube API 对服务器 IP 开启 bot 检测 | 🔴 阻塞 |
| baoyu-youtube-transcript skill 安装成功但下载被 block | 同上 | 🔴 需备用方案 |
| session context 过大导致 exec 结果被吞 | OpenClaw exec 输出在过大 context 下被丢弃 | 🔴 需手动 restart |
| GitHub push 被 secret scanning 拦 | sessions/*.jsonl 包含 GitHub token | ✅ 已修复：sessions/*.jsonl* 进 .gitignore |

---

## 🚨 核心方法论：联网学习循环

**适用场景：所有代码、LLM 工具、API、prompt 工程相关的工作**

核心链路：**搜最新资料 → 学习 → 实践 → 不会就查源文档 → 验证 → 再搜 → 直到解决**

---

## 记忆压缩机制

- **触发阈值**: 120,000 tokens（当前 session 超过此值触发压缩）
- **保留天数**: 7 天
- **归档限制**: 30 条

执行：`bash scripts/memory_consolidate.sh`
## 晨间工作流

**cron**: 0 6 * * * @ Asia/Shanghai | 超时 1800s | ID: `0eef9649-42e1-4bc3-822f-dc155181e934`

**三级分级抓取**：
- HN Firebase API（零 Jina）
- arXiv 官方 API（零 Jina）
- 其他 → Jina 提取

**文件路径**：
```
data/raw_rss.json
data/topic_result.json
data/brief_content.txt
data/daily_brief_YYYY-MM-DD.html
```

**sub-agent 链路**: bibi-topic → bibi-writer → bibi-design
## RSS 三级分级架构

| 阶段 | 来源 | 方式 | Jina 成本 |
|------|------|------|-----------|
| Phase 0 | HN | Firebase API | 0 |
| Phase 0b | arXiv | 官方 API | 0 |
| Phase 1 | 其他 RSS | Jina Reader | 全部 |

**配置**: `automation/fetch_all_rss.py`
## RSS 信源分层体系（2026-03-22 最终版）

| 等级 | 权重 | 来源 | 核心价值 |
|------|------|------|---------|
| ★★★★★ S | 5 | Latent Space、Eugene Yan、Simon Willison | 每日必读，独立 Practitioner |
| ★★★★ A | 4 | No Priors、a16z AI、Pragmatic Engineer、Hacker News | 商业/资本/变现视角 |
| ★★★★ B | 4 | Dwarkesh Podcast、20VC、Lex Fridman Podcast | 顶级访谈，信息密度最高 |
| ★★★★ C | 4 | Andrej Karpathy YouTube、Lex Fridman YouTube | YouTube 字幕（暂不可用，仅标题） |
| ★ D | 3 | OpenClaw/LangChain/AutoGen Commits、晚点 | 开源生态/国内视角 |
| ★ E | 2-3 | 稀土掘金、Google Alerts | 补充源 |
| ★ F | 1 | Anthropic/HuggingFace 官方博客 | 官方 PR，权重最低 |

**关键规则**：
- 官方博客权重从 4 降到 1
- bibi-topic 负责智能筛选和跨日查重（/tmp/ 前 7 天）
- YouTube 内容用 RSS media:description，不走 Jina

---

## 时效性过滤规则

```python
RECENCY_BAN_KEYWORDS = [
    "anniversary", "十周年", "十年", "回顾", "history of", "looking back",
    "in memory", "纪念", " obituary", "讣告", "去世", "passed away",
    "retrospective", "回首", "x周年",
]
MAX_CONTENT_AGE_DAYS = 14
```

---

## 待办 & 未来优化

- [ ] 补全心跳压缩机制（120k 阈值已配置）
- [ ] BeautifulSoup 直抓 36Kr / 机器之心
- [ ] HN Top Blogs OPML（200+ 精选博客）
