#!/usr/bin/expect -f

set timeout 300
set host "root@72.62.171.113"
set password "Equidistante2085.-"
set cmd [lindex $argv 0]

spawn ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $host $cmd
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
