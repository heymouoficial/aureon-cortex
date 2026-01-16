#!/usr/bin/expect -f

set timeout 30
set host "root@72.62.171.113"
set password "Equidistante2085.-"

spawn ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $host {cat > /etc/dokploy/traefik/dynamic/cortex.yml << 'EOFCONFIG'
http:
  routers:
    cortex:
      rule: "Host(`cortex.elevatmarketing.com`)"
      entryPoints:
        - websecure
      service: cortex
      tls:
        certResolver: letsencrypt
  services:
    cortex:
      loadBalancer:
        servers:
          - url: "http://aureon-cortex:8000"
EOFCONFIG}
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
