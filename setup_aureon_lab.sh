#!/bin/bash

# Aureon Lab Setup - MacBook Air M1 Base Configuration
echo "🧠 Configuring Aureon Laboratory on MacBook Air M1..."

# 1. Install core dependencies
echo "📦 Installing Homebrew packages..."
brew install python3 nodejs npm redis postgresql docker cloudflared

# 2. Setup Python environment
echo "🐍 Setting up Python environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip

# 3. Install Cortex dependencies
echo "🔧 Installing Cortex dependencies..."
cd /Users/astursadeth/multiversa-lab/portality/cortex
pip install -r requirements.txt

# 4. Start local services
echo "🗄️ Starting local services..."
brew services start redis
brew services start postgresql

# 5. Setup environment variables
echo "⚙️ Setting up environment..."
if [ ! -f .env.local ]; then
    cp .env.cortex .env.local
    echo "📝 Created .env.local from .env.cortex"
fi

# 6. Test local Aureon server
echo "🚀 Starting local Aureon server..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
SERVER_PID=$!

echo "✅ Aureon Lab Setup Complete!"
echo "📋 Summary:"
echo "  - Local server: http://localhost:8000"
echo "  - Environment: .env.local"
echo "  - Services: Redis, PostgreSQL running"
echo ""
echo "🔥 Issue: Telegram API blocked by your network"
echo "💡 Solution: Use Cloudflare Tunnel or VPN"
echo ""
echo "📞 Next commands:"
echo "  cloudflared tunnel login"
echo "  cloudflared tunnel create aureon-local"
echo "  cloudflared tunnel route dns aureon-local aureon.yourdomain.com"

# Wait a moment for server to start
sleep 3

# Test server health
curl -s http://localhost:8000/health || echo "❌ Server not responding yet"

echo "🎯 Server running with PID: $SERVER_PID"
echo "🛑 Stop with: kill $SERVER_PID"