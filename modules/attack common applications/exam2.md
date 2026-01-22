# Exam 2

ffuf -w ~/repositories/SecLists/Discovery/DNS/subdomains-top1million-5000.txt:FUZZ -u https://gitlab.inlanefreight.local -H 'Host: FUZZ.inlanefreight.local' 

An nmap scan showed the following:
```Starting Nmap 7.95 ( https://nmap.org ) at 2026-01-21 05:02 EST
Nmap scan report for gitlab.inlanefreight.local (10.129.201.90)
Host is up (0.27s latency).
Not shown: 994 closed tcp ports (reset)
PORT     STATE SERVICE
22/tcp   open  ssh
25/tcp   open  smtp
80/tcp   open  http
389/tcp  open  ldap
443/tcp  open  https
8180/tcp open  unknown
```

Let's attempt some vhost discovery:
```
ffuf -w ~/repositories/SecLists/Discovery/DNS/subdomains-top1million-5000.txt:FUZZ -u https://gitlab.inlanefreight.local -H 'Host: FUZZ.inlanefreight.local' 
```

This resultated in the following subdomains beeing found:
```
monitoring              [Status: 302, Size: 27, Words: 5, Lines: 1, Duration: 445ms]
blog                    [Status: 200, Size: 50118, Words: 16140, Lines: 1015, Duration: 1477ms]
gitlab                  [Status: 301, Size: 339, Words: 20, Lines: 10, Duration: 67ms]
```

Browsing the gitlab page we find credentials for the `nagios`application running on `monitoring.inlanefreight.local`. The password is `oilaKglm7M09@CPL&^lC`. The username is the default username: `nagiosadmin`

With msfconsole we can find an authenticated RCE exploit we can use which gives us a remote shell
