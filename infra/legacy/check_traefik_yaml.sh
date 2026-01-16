#!/usr/bin/expect -f

set timeout 30
set host "root@72.62.171.113"
set password "Equidistante2085.-"

spawn ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $host "docker exec dokploy-traefik cat /etc/traefik/traefik.yml 2>/dev/null || docker exec dokploy-traefik cat /traefik.yml 2>/dev/null || echo 'No traefik.yml found'"
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
