#!/bin/bash

# 🚀 Aureon Cortex Deployment Script (VPS)
# Usage: ./deploy.sh [user@host]

HOST="${1:-root@72.62.171.113}"
DEST="/opt/aureon-cortex"

echo "🧠 Initiating Aureon Cortex Deployment to $HOST..."

# 1. Sync Files (excluding heavy/unnecessary local files)
echo "📡 Syncing files to $DEST..."
rsync -avz --progress \
    --exclude 'venv' \
    --exclude '__pycache__' \
    --exclude '.git' \
    --exclude '.DS_Store' \
    --exclude '*.pyc' \
    ./ "$HOST:$DEST"

# 2. Remote Build & Restart
echo "🔄 Executing Remote Build & Restart..."
ssh "$HOST" "cd $DEST && \
    cp .env.cortex.example .env.cortex && \
    echo '⚠️  REMINDER: Please edit .env.cortex on the server if variables differ from example.' && \
    docker compose -f docker-compose.prod.yml down && \
    docker compose -f docker-compose.prod.yml up -d --build"

echo "✅ Deployment Triggered."
echo "📝 To view logs: ssh $HOST 'docker logs -f aureon-cortex'"

