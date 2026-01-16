#!/bin/bash

# Cloudflare Tunnel Setup for Aureon Lab
echo "🚀 Setting up Cloudflare Tunnel for Aureon Lab..."

# Install cloudflared if not present
if ! command -v cloudflared &> /dev/null; then
    echo "📦 Installing cloudflared..."
    brew install cloudflared
fi

# Login to Cloudflare
echo "🔐 Login to Cloudflare..."
cloudflared tunnel login

# Create tunnel
echo "🔧 Creating tunnel..."
TUNNEL_NAME="aureon-lab"
cloudflared tunnel create $TUNNEL_NAME

# Get tunnel UUID
TUNNEL_UUID=$(cloudflared tunnel list | grep $TUNNEL_NAME | awk '{print $1}')

# Create config file
mkdir -p ~/.cloudflared
cat > ~/.cloudflared/config.yml << EOF
tunnel: $TUNNEL_UUID
credentials-file: ~/.cloudflared/$TUNNEL_UUID.json

ingress:
  - hostname: aureon.yourdomain.com
    service: http://localhost:8000
  - service: http_status:404
EOF

# Create DNS record
echo "🌐 Creating DNS record..."
cloudflared tunnel route dns $TUNNEL_NAME aureon.yourdomain.com

echo "✅ Cloudflare Tunnel configured!"
echo "📋 Next steps:"
echo "1. Replace 'aureon.yourdomain.com' with your actual domain"
echo "2. Run: cloudflared tunnel run $TUNNEL_NAME"
echo "3. Test Aureon via: https://aureon.yourdomain.com"