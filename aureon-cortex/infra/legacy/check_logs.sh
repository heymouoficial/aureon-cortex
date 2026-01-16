#!/usr/bin/expect -f
set timeout 60
set host "root@72.62.171.113"
set password "Equidistante2085.-"

spawn ssh -o StrictHostKeyChecking=no -o PreferredAuthentications=password -o PubkeyAuthentication=no $host "echo '--- CONTAINER STATUS ---' && docker ps -a | grep aureon && echo '--- LOGS ---' && docker logs --tail 20 aureon-cortex"
expect {
    "password:" { send "$password\r"; exp_continue }
    eof
}
