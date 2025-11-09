#!/bin/bash
# Enhanced script to monitor LangGraph Studio logs with error highlighting

LOG_FILE="/tmp/langgraph_debug.log"

echo "=== LangGraph Studio Debug Log Monitor ==="
echo ""
echo "Log file: $LOG_FILE"
echo "Press Ctrl+C to stop monitoring"
echo ""
echo "---"

# Function to highlight errors
tail -f "$LOG_FILE" 2>/dev/null | while IFS= read -r line; do
    if echo "$line" | grep -qiE "error|exception|traceback|fail|502|401|500|crash"; then
        echo -e "\033[31m$line\033[0m"  # Red for errors
    elif echo "$line" | grep -qiE "warning"; then
        echo -e "\033[33m$line\033[0m"  # Yellow for warnings
    elif echo "$line" | grep -qiE "info.*query|info.*agent|info.*tool"; then
        echo -e "\033[32m$line\033[0m"  # Green for query/agent info
    else
        echo "$line"
    fi
done

