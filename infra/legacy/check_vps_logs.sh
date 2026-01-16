#!/usr/bin/expect -f

set timeout 30
set host "root@72.62.171.113"
set password "Equidistante2085.-"
set remote_dir "/opt/aureon-cortex"

spawn ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $host "cd $remote_dir && docker compose -f docker-compose.prod.yml logs --tail=100 cortex"
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
