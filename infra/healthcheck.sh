#!/bin/bash
# Aureon Cortex - Health Check Script
# Consolidated diagnostic tool

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              AUREON CORTEX HEALTH CHECK                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"

TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
DOMAIN="${DOMAIN:-https://cortex.elevatmarketing.com}"

# 1. Check API Health
echo -e "\n📡 Checking Cortex API..."
if curl -sf "${DOMAIN}/health" > /dev/null 2>&1; then
    echo "✅ API is responding at ${DOMAIN}/health"
else
    echo "❌ API is NOT responding at ${DOMAIN}"
fi

# 2. Check Telegram Webhook
echo -e "\n🤖 Checking Telegram Webhook..."
if [ -n "$TELEGRAM_BOT_TOKEN" ]; then
    WEBHOOK_INFO=$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo")
    WEBHOOK_URL=$(echo "$WEBHOOK_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin).get('result', {}).get('url', 'NOT SET'))" 2>/dev/null || echo "ERROR")
    PENDING=$(echo "$WEBHOOK_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin).get('result', {}).get('pending_update_count', 0))" 2>/dev/null || echo "0")
    
    echo "   Webhook URL: $WEBHOOK_URL"
    echo "   Pending updates: $PENDING"
    
    if [ "$WEBHOOK_URL" == "NOT SET" ] || [ "$WEBHOOK_URL" == "" ]; then
        echo "⚠️  Webhook not configured! Run: curl -X POST 'https://api.telegram.org/bot\${TOKEN}/setWebhook?url=${DOMAIN}/telegram/webhook'"
    fi
else
    echo "⚠️  TELEGRAM_BOT_TOKEN not set in environment"
fi

# 3. Check Docker containers (if on VPS)
echo -e "\n🐳 Checking Docker containers..."
if command -v docker &> /dev/null; then
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(cortex|traefik|aureon)" || echo "No Aureon containers found"
else
    echo "Docker not available (local environment)"
fi

# 4. Check Traefik routing (if available)
echo -e "\n🌐 Checking Traefik routers..."
if curl -sf "http://localhost:8080/api/http/routers" > /dev/null 2>&1; then
    curl -s "http://localhost:8080/api/http/routers" | python3 -c "
import sys, json
try:
    routers = json.load(sys.stdin)
    for r in routers:
        print(f\"   {r.get('name', 'unknown')}: {r.get('rule', 'no rule')}\")
except:
    print('   Could not parse routers')
" 2>/dev/null
else
    echo "   Traefik API not accessible (normal for local dev)"
fi

echo -e "\n✅ Health check complete"
