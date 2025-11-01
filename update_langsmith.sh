#!/bin/bash
echo "🔧 LangSmith Configuration Helper"
echo ""
echo "Choose an option:"
echo "1. Add LangSmith API key (I have one)"
echo "2. Disable LangSmith tracing (I don't need it)"
echo "3. Just show instructions (I'll do it manually)"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
  1)
    read -p "Enter your LangSmith API key: " key
    if [ -f .env ]; then
      # Remove old LANGSMITH_API_KEY if exists
      sed -i.bak '/^LANGSMITH_API_KEY=/d' .env 2>/dev/null || sed -i '' '/^LANGSMITH_API_KEY=/d' .env 2>/dev/null
      # Add new one
      echo "LANGSMITH_API_KEY=\"$key\"" >> .env
      # Update tracing to true
      sed -i.bak 's/^LANGSMITH_TRACING=.*/LANGSMITH_TRACING=true/' .env 2>/dev/null || sed -i '' 's/^LANGSMITH_TRACING=.*/LANGSMITH_TRACING=true/' .env 2>/dev/null
      echo "✅ Added LangSmith API key to .env"
      echo "✅ Enabled LANGSMITH_TRACING=true"
      echo ""
      echo "⚠️  You need to restart the server for changes to take effect!"
    else
      echo "❌ .env file not found!"
    fi
    ;;
  2)
    if [ -f .env ]; then
      # Update tracing to false
      if grep -q "^LANGSMITH_TRACING=" .env; then
        sed -i.bak 's/^LANGSMITH_TRACING=.*/LANGSMITH_TRACING=false/' .env 2>/dev/null || sed -i '' 's/^LANGSMITH_TRACING=.*/LANGSMITH_TRACING=false/' .env 2>/dev/null
      else
        echo "LANGSMITH_TRACING=false" >> .env
      fi
      echo "✅ Disabled LangSmith tracing"
      echo ""
      echo "⚠️  You need to restart the server for changes to take effect!"
    else
      echo "❌ .env file not found!"
    fi
    ;;
  3)
    echo ""
    echo "📝 Manual Instructions:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "To enable LangSmith:"
    echo "1. Get API key from: https://smith.langchain.com/"
    echo "2. Add to .env:"
    echo "   LANGSMITH_API_KEY=\"your-key-here\""
    echo "   LANGSMITH_TRACING=true"
    echo ""
    echo "To disable LangSmith:"
    echo "   LANGSMITH_TRACING=false"
    echo ""
    echo "Then restart the server!"
    ;;
  *)
    echo "Invalid choice"
    ;;
esac
