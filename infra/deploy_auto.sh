#!/usr/bin/expect -f
set timeout 600
set host "root@72.62.171.113"
set password "Equidistante2085.-"

# Ensure we act from project root
cd /Users/astursadeth/multiversa-lab

# 1. Sync Code (Excluding local garbage and secrets initially)
puts "\n📡 (1/3) Syncing Codebase to VPS..."
spawn rsync -avz -e "ssh -o StrictHostKeyChecking=no -o PreferredAuthentications=password -o PubkeyAuthentication=no" --exclude ".git" --exclude "__pycache__" --exclude "venv" --exclude ".env.cortex" aureon-cortex/ $host:/opt/aureon-cortex/
expect {
    "password:" { send "$password\r"; exp_continue }
    "yes/no" { send "yes\r"; exp_continue }
    eof
}

# 2. Sync Secrets (Crucial .env.cortex with new keys)
puts "\n🔐 (2/3) Syncing Secrets (.env.cortex)..."
spawn scp -o StrictHostKeyChecking=no -o PreferredAuthentications=password -o PubkeyAuthentication=no aureon-cortex/.env.cortex $host:/opt/aureon-cortex/.env.cortex
expect {
    "password:" { send "$password\r" }
    eof
}

# 3. Remote Build & Restart
puts "\n🏗️  (3/3) Executing Remote Build & Restart on VPS..."
spawn ssh -o StrictHostKeyChecking=no -o PreferredAuthentications=password -o PubkeyAuthentication=no $host "cd /opt/aureon-cortex/infra && docker compose down && docker compose -f docker-compose.prod.yml up -d --build --force-recreate && docker ps | grep aureon"
expect {
    "password:" { send "$password\r" }
    eof
}

puts "\n✅ DEPLOYMENT COMPLETE! Aureon should be online."
