#!/usr/bin/expect -f
set timeout 600
set host "root@72.62.171.113"
set password "Equidistante2085.-"

spawn ssh -o StrictHostKeyChecking=no -o PreferredAuthentications=password -o PubkeyAuthentication=no $host "docker compose -f /opt/aureon-cortex/infra/docker-compose.prod.yml down && docker compose -f /opt/aureon-cortex/infra/docker-compose.prod.yml up -d --build --force-recreate && docker ps | grep aureon"
expect {
    "password:" { send "$password\r"; exp_continue }
    eof
}
