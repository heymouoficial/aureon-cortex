#!/usr/bin/expect -f

set timeout 30
set host "root@72.62.171.113"
set password "Equidistante2085.-"

spawn ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $host "curl -s http://localhost:8080/api/http/routers | python3 -m json.tool | head -100"
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
