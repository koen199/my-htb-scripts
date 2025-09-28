Use dnsEnum for subdomain enumeration

```
dnsenum --enum inlanefreight.com -f /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt -r
```

Use gobuster for discovery of different vhosts on one server.
This canges the host header based on the wordlist
```
gobuster vhost -u http://<target_IP_address> -w <wordlist_file> --append-domain
```

gobuster vhost -u http://inlanefreight.htb:51139 -w /snap/seclists/current/Discovery/DNS/subdomains-top1million-110000.txt --append-domain

gobuster vhost -u http://localhost:8888 -w /snap/seclists/current/Discovery/DNS/subdomains-top1million-20000.txt --append-domain inlanefreight.htb

Directory enumeation
```
gobuster dir -u http://web1337.inlanefreight.htb:58659 -w /snap/seclists/current/Discovery/Web-Content/common.txt
```

