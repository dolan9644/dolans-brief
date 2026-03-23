#!/usr/bin/env python3
"""
BIBI Config Sync — 段落级合并
config.json 是单一真相源，但只覆盖可参数化的部分
MEMORY.md 的手写内容（信源列表、排障、方法论）永不覆盖
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
HEARTBEAT = WORKSPACE / "HEARTBEAT.md"
MEMORY_DIR = WORKSPACE / "memory"
TODAY = datetime.now().strftime("%Y-%m-%d")

# MEMORY.md 中需要从 config.json 更新的区块（用注释标记）
SYNC_SECTIONS = {
    "memory_compression": "## 记忆压缩机制",
    "morning_workflow": "## 晨间工作流",
    "rss_architecture": "## RSS 三级分级架构",
    "feishu_config": "## 飞书推送工作流",
    "git_config": "## GitHub Pages 部署",
    "api_config": "## 技术运营配置",
}

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

def build_section(c, section):
    """根据 section 名称从 config.json 生成对应段落"""
    if section == "memory_compression":
        t = c["memory"]["compression_threshold_tokens"]
        days = c["memory"]["archive_keep_days"]
        limit = c["memory"]["archived_log_limit"]
        return f"""## 记忆压缩机制

- **触发阈值**: {t:,} tokens（当前 session 超过此值触发压缩）
- **保留天数**: {days} 天
- **归档限制**: {limit} 条

执行：`bash scripts/memory_consolidate.sh`"""

    elif section == "morning_workflow":
        cron = c["cron"]["morning_brief"]
        files = c["files"]
        return f"""## 晨间工作流

**cron**: {cron['schedule']} | 超时 {cron['timeout']}s | ID: `{cron['id']}`

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

**sub-agent 链路**: bibi-topic → bibi-writer → bibi-design"""

    elif section == "rss_architecture":
        rss = c["rss"]
        return f"""## RSS 三级分级架构

| 阶段 | 来源 | 方式 | Jina 成本 |
|------|------|------|-----------|
| Phase 0 | HN | Firebase API | 0 |
| Phase 0b | arXiv | 官方 API | 0 |
| Phase 1 | 其他 RSS | Jina Reader | 全部 |

**配置**: `automation/fetch_all_rss.py`"""

    elif section == "feishu_config":
        feishu = c["feishu"]
        return f"""## 飞书推送工作流

- **群组**: `{feishu['group_id']}`
- **用户 ID**: `{feishu['user_id']}`
- **铁律**: 卡片退给我才算完成

推送后等用户确认收到，才算闭环。"""

    elif section == "git_config":
        gh = c["github"]
        return f"""## GitHub Pages 部署

- **仓库**: `{gh['repo']}`
- **CDN**: {gh['cdn_base']}"""

    elif section == "api_config":
        apis = c.get("apis", {})
        rows = "\n".join([f"| {name} | {info.get('model','-')} | {info.get('use','-')} |"
                          for name, info in apis.items()])
        return f"""## 技术运营配置

### API 配置
| 服务 | 模型 | 用途 |
|------|------|------|
{rows if rows else "| - | - | - |"}

### 数据同步
> 本文件由 `sync_config.py` 管理 — config.json 是单一真相源
> 手动修改 config.json 后运行 `python3 agent/sync_config.py` 同步"""
    return ""

def update_memory_with_config(memory_text, c):
    """只替换标记区块，保留其他所有内容"""
    result = memory_text
    for section, marker in SYNC_SECTIONS.items():
        new_block = build_section(c, section)
        # 找到 marker 开始的行
        lines = result.split("\n")
        start_idx = None
        end_idx = None
        for i, line in enumerate(lines):
            if marker in line and start_idx is None:
                start_idx = i
            if start_idx is not None and end_idx is None:
                # 找到下一个 ## 标题 或文件末尾
                if i > start_idx and re.match(r"^## ", line):
                    end_idx = i
                    break
        if start_idx is not None:
            end_idx = end_idx or len(lines)
            # 保留 marker 行本身，用新内容替换到下一个 ## 之前
            lines = lines[:start_idx] + new_block.split("\n") + lines[end_idx:]
            result = "\n".join(lines)
    return result

def gen_heartbeat(c):
    threshold = c["memory"]["compression_threshold_tokens"]
    return f"""# HEARTBEAT.md

## 定期任务

### 记忆压缩检查（每小时一次）
当 session context 超过 **{threshold:,} tokens** 时执行：

1. 将当日日志追加写入 `memory/{TODAY}.md`
2. 运行 `bash scripts/memory_consolidate.sh`
3. git commit 留版本

### 其他定期检查
- 晨报 cron 状态确认
- data/ 目录大小监控
"""

def git_commit(msg):
    r = subprocess.run(["git", "add", "-A"], cwd=WORKSPACE, capture_output=True, text=True)
    if r.returncode != 0 and "nothing to commit" not in r.stderr:
        print(f"git add warning: {r.stderr.strip()}")
    r = subprocess.run(["git", "commit", "-m", msg], cwd=WORKSPACE, capture_output=True, text=True)
    if r.returncode != 0 and "nothing to commit" not in r.stderr:
        print(f"git commit warning: {r.stderr.strip()}")
    elif r.returncode == 0:
        print(f"  commit: {msg}")

def main():
    do_commit = "--commit" in sys.argv
    cfg = load_json(CONFIG)

    # HEARTBEAT.md — 整体替换（无手写内容）
    new_hb = gen_heartbeat(cfg)
    old_hb = HEARTBEAT.read_text() if HEARTBEAT.exists() else ""
    if old_hb != new_hb:
        HEARTBEAT.write_text(new_hb)
        print(f"✅ HEARTBEAT.md updated")

    # MEMORY.md — 段落级合并（保留手写内容）
    if MEMORY.exists():
        old_text = MEMORY.read_text()
        new_text = update_memory_with_config(old_text, cfg)
        if new_text != old_text:
            MEMORY.write_text(new_text)
            print(f"✅ MEMORY.md sections updated")
    else:
        # 如果 MEMORY.md 不存在，从头生成
        MEMORY.write_text("# MEMORY.md\n\n")
        print(f"✅ MEMORY.md created (empty)")

    append_daily(f"sync_config v{cfg['meta']['version']}")

    if do_commit:
        git_commit(f"config sync: v{cfg['meta']['version']}")

    print(f"✅ 同步完成{' (git committed)' if do_commit else ''}")

if __name__ == "__main__":
    main()
