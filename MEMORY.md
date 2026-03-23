# MEMORY.md — BIBI Agent 持久记忆核心

> 本文件由 sync_config.py 自动生成 — 手动修改将被覆盖
> 源文件: agent/config.json

---

## 技术运营配置

### API 配置
| 服务 | 模型 | 用途 |
|------|------|------|
| 小米 MiMo | `mimo-v2-pro` | **默认模型** |
| 小米 MiMo | `mimo-v2-flash` | 备用 / 快速任务 |
| MiniMax | `minimax-cn/MiniMax-M2.5-highspeed` | 临时指定 |

### GitHub Pages
- **仓库**: dolan9644/bibi-intel
- **CDN**: https://cdn.jsdelivr.net/gh/dolan9644/bibi-intel@main/docs/

### 飞书
- **群组**: oc_ed18b6ceeaccabc19fceb48b66e0e091
- **用户**: ou_3a88b7b21440fb9d99cd0b4399f64b3a

---

## 记忆压缩机制

- **触发阈值**: 120,000 tokens
- **保留天数**: 7 天
- **归档限制**: 30 条

---

## 晨间工作流

- **cron ID**: 0eef9649-42e1-4bc3-822f-dc155181e934
- **调度**: 0 6 * * * @ Asia/Shanghai
- **超时**: 1800s

### 文件路径
```
data/raw_rss.json
data/topic_result.json
data/brief_content.txt
data/daily_brief_YYYY-MM-DD.html
```

---

## RSS 三级分级架构

- HN: firebase_api (Jina成本: 0)
- arXiv: official_api (Jina成本: 0)
- 其他: jina_reader (上限: 200 条)
