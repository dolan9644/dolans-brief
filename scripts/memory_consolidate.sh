#!/bin/bash
# =============================================================================
# BIBI Agent Memory Consolidate Script
# 记忆压缩节点：当检测到对话上下文过大时，手动触发此脚本
# 使用方式：./memory_consolidate.sh
# =============================================================================

WORKSPACE="$HOME/.openclaw/agents/bibi-agent"
MEMORY_DIR="$WORKSPACE/memory"
DONE_DIR="$MEMORY_DIR/done"
MEMORY_FILE="$WORKSPACE/MEMORY.md"

mkdir -p "$DONE_DIR"

# 找到最旧的未归档日志（跳过 done/ 和今天的文件）
TODAY=$(date +%Y-%m-%d)
OLDEST=$(find "$MEMORY_DIR" -maxdepth 1 -name "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md" \
    ! -name "*$TODAY*" ! -path "$DONE_DIR/*.md" | sort | head -1)

if [ -z "$OLDEST" ]; then
    echo "No old memory logs to consolidate."
    exit 0
fi

DATE_STR=$(basename "$OLDEST" .md)
echo "Consolidating: $OLDEST"

# 简单摘要：取文件前3行作为摘要
SUMMARY=$(head -3 "$OLDEST" | sed 's/^#*/#/')

# 在 MEMORY.md 末尾追加归档摘要
ARCHIVE_MARKER="<!-- ARCHIVED_LOGS -->"
if ! grep -q "$ARCHIVE_MARKER" "$MEMORY_FILE"; then
    echo "" >> "$MEMORY_FILE"
    echo "$ARCHIVE_MARKER" >> "$MEMORY_FILE"
fi

sed -i '' "/$ARCHIVE_MARKER/i\\$DATE_STR: $SUMMARY" "$MEMORY_FILE" 2>/dev/null || \
    echo "$DATE_STR: $SUMMARY" >> "$MEMORY_FILE"

# 移动到 done/
mv "$OLDEST" "$DONE_DIR/"

echo "✅ Consolidated $OLDEST → done/"
echo "📝 Summary: $DATE_STR: $(echo $SUMMARY | head -c 80)..."
