# HEARTBEAT.md

## 定期任务

### 记忆压缩检查（每小时一次）
当 session context 超过 **120,000 tokens** 时执行：

1. 将当日日志追加写入 `memory/2026-03-23.md`
2. 运行 `bash scripts/memory_consolidate.sh`
3. ARCHIVED_LOGS 追加摘要
4. git commit 留版本

### 其他定期检查
- 晨报 cron 状态确认
- data/ 目录大小监控
