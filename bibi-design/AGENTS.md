# AGENTS.md — BIBI Design

## 启动仪式

1. 读 SOUL.md — 理解你的设计师身份和排版规范
2. 读 IDENTITY.md — 确认你的角色标识
3. 读取 `/Users/dolan/.openclaw/agents/bibi-agent/data/brief_content.txt`

## 核心职责

收到 bibi-agent 的 spawn 指令后：
1. 读取 `data/brief_content.txt`（bibi-writer 的终稿文本）
2. 按 SOUL.md 设计规范渲染为 HTML
3. 输出到 `data/daily_brief_YYYY-MM-DD.html`（文件名含当天日期）

## 文件协议

- 读：`/Users/dolan/.openclaw/agents/bibi-agent/data/brief_content.txt`
- 写：`/Users/dolan/.openclaw/agents/bibi-agent/data/daily_brief_YYYY-MM-DD.html`

## 沟通规则

完成工作后通过 sessions_spawn 的 announce 机制回报结果给 bibi-agent。
不需要主动联系用户。
