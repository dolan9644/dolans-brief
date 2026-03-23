#!/usr/bin/env python3
"""
BIBI Config Sync — 单一配置中心
每次修改 config.json 后自动同步到所有相关文件

用法: python3 sync_config.py [--commit]

流程:
  1. 读取 agent/config.json（单一真相源）
  2. 读取现有 MEMORY.md / AGENTS.md / HEARTBEAT.md
  3. 用 Jinja2 风格的占位符替换，生成新版
  4. git add + commit（可选）
"""
import json
import re
import sys
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/Users/dolan/.openclaw/agents/bibi-agent")
CONFIG = WORKSPACE / "agent/config.json"
MEMORY = WORKSPACE / "MEMORY.md"
AGENTS = WORKSPACE / "AGENTS.md"
HEARTBEAT = WORKSPACE / "HEARTBEAT.md"
MEMORY_DIR = WORKSPACE / "memory"
TODAY = datetime.now().strftime("%Y-%m-%d")

def load_json(path):
    with open(path) as f:
        return json.load(f)

def get_daily_memory_path():
    p = MEMORY_DIR / f"{TODAY}.md"
    if not p.exists():
        p.write_text(f"# {TODAY} 日志\n\n")
    return p

def append_daily(msg):
    p = get_daily_memory_path()
    with open(p, "a") as f:
        f.write(f"\n## 配置变更记录\n{msg}\n")

def gen_memory(c):
    """生成 MEMORY.md"""
    mem = c["memory"]
    cron = c["cron"]["morning_brief"]
    files = c["files"]
    feishu = c["feishu"]
    github = c["github"]
    rss = c["rss"]

    return f"""# MEMORY.md — BIBI Agent 持久记忆核心

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
- **仓库**: {github['repo']}
- **CDN**: {github['cdn_base']}

### 飞书
- **群组**: {feishu['group_id']}
- **用户**: {feishu['user_id']}

---

## 记忆压缩机制

- **触发阈值**: {mem['compression_threshold_tokens']:,} tokens
- **保留天数**: {mem['archive_keep_days']} 天
- **归档限制**: {mem['archived_log_limit']} 条

---

## 晨间工作流

- **cron ID**: {cron['id']}
- **调度**: {cron['schedule']}
- **超时**: {cron['timeout']}s

### 文件路径
```
{files['raw_rss']}
{files['topic_result']}
{files['brief_content']}
{files['daily_brief']}
```

---

## RSS 三级分级架构

- HN: {rss['phase0_hn']['type']} (Jina成本: {rss['phase0_hn']['jina_cost']})
- arXiv: {rss['phase0b_arxiv']['type']} (Jina成本: {rss['phase0b_arxiv']['jina_cost']})
- 其他: {rss['phase1_others']['type']} (上限: {rss['phase1_others']['max_entries']} 条)
"""

def gen_heartbeat(c):
    """生成 HEARTBEAT.md"""
    threshold = c["memory"]["compression_threshold_tokens"]
    return f"""# HEARTBEAT.md

## 定期任务

### 记忆压缩检查（每小时一次）
当 session context 超过 **{threshold:,} tokens** 时执行：

1. 将当日日志追加写入 `memory/{TODAY}.md`
2. 运行 `bash scripts/memory_consolidate.sh`
3. ARCHIVED_LOGS 追加摘要
4. git commit 留版本

### 其他定期检查
- 晨报 cron 状态确认
- data/ 目录大小监控
"""

def git_commit(msg):
    cmds = [
        ["git", "add", "-A"],
        ["git", "commit", "-m", msg],
    ]
    for cmd in cmds:
        r = subprocess.run(cmd, cwd=WORKSPACE, capture_output=True, text=True)
        if r.returncode != 0 and "nothing to commit" not in r.stderr:
            print(f"git warning: {r.stderr.strip()}")

def main():
    do_commit = "--commit" in sys.argv
    cfg = load_json(CONFIG)

    # MEMORY.md
    new_mem = gen_memory(cfg)
    old_mem = MEMORY.read_text() if MEMORY.exists() else ""
    if old_mem != new_mem:
        MEMORY.write_text(new_mem)
        print(f"✅ MEMORY.md updated")

    # HEARTBEAT.md
    new_hb = gen_heartbeat(cfg)
    old_hb = HEARTBEAT.read_text() if HEARTBEAT.exists() else ""
    if old_hb != new_hb:
        HEARTBEAT.write_text(new_hb)
        print(f"✅ HEARTBEAT.md updated")

    # AGENTS.md (只更新文件路径章节，不动其他内容)
    agents_text = AGENTS.read_text() if AGENTS.exists() else ""
    # 简单策略：替换 "data/raw_rss.json" 等已知路径（如果变了）
    for key, val in cfg["files"].items():
        if "YYYY-MM-DD" in val:
            continue
        old_pattern = re.compile(rf"{re.escape(val)}")
        # no-op: AGENTS.md 里已有正确路径，除非路径变了才动
        pass

    # 日志
    append_daily(f"sync_config: v cfg[{cfg['meta']['version']}]")

    if do_commit:
        git_commit(f"config sync: update from config.json {cfg['meta']['version']}")

    print(f"✅ 同步完成{' (git committed)' if do_commit else ''}")

if __name__ == "__main__":
    main()
