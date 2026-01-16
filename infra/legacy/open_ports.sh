#!/usr/bin/expect -f
set timeout 600
set host "root@72.62.171.113"
set password "Equidistante2085.-"

spawn ssh -o StrictHostKeyChecking=no -o PreferredAuthentications=password -o PubkeyAuthentication=no $host "ufw allow 8000/tcp && ufw reload && ufw status | grep 8000"
expect {
    "password:" { send "$password\r" }
    eof
}
