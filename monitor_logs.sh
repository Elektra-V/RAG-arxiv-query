#!/bin/bash
# Script to monitor LangGraph Studio logs in real-time

echo "=== LangGraph Studio Log Monitor ==="
echo ""
echo "Press Ctrl+C to stop monitoring"
echo ""
echo "Monitoring log file: /tmp/langgraph_tunnel.log"
echo ""

tail -f /tmp/langgraph_tunnel.log

