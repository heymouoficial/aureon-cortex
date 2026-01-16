#!/usr/bin/expect -f

set timeout 300
set host "root@72.62.171.113"
set password "Equidistante2085.-"
set src_dir "./"
set remote_dir "/opt/aureon-cortex"

# Colors
proc color_print {msg} {
    puts "\033\[1;32m$msg\033\[0m"
}

color_print "🧠 Aureon Cortex Auto-Deployment Initiated..."
color_print "📡 Target: $host"

# Step 1: Create directory remotely
spawn ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $host "mkdir -p $remote_dir"
expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    eof
}

color_print "✅ Remote directory prepared."

# Step 2: Sync Files
spawn rsync -avz --exclude "__pycache__" --exclude ".git" --exclude ".venv" --exclude ".env" -e "ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no" $src_dir $host:$remote_dir
expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof
}

color_print "✅ Files synced successfully."

# Step 3: Build and Deploy
spawn ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $host "cd $remote_dir && docker compose -f docker-compose.prod.yml build --no-cache && docker compose -f docker-compose.prod.yml up -d"
expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof
}

color_print "🚀 Cortex Deployed & Running!"
color_print "⚠️  IMPORTANT: Please SSH in and configure .env.cortex with your real keys if you haven't yet!"
color_print "   Command: ssh $host"
