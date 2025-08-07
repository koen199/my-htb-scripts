Perform a directory scan using a word list on a webserver
```
gobuster dir -u http://10.10.10.121/ -w /usr/share/seclists/Discovery/Web-Content/common.txt
```

Find other subdomains on the same server
```
gobuster dns -d inlanefreight.com -w /usr/share/SecLists/Discovery/DNS/namelist.txt
```

This uses word list/leakes password/usernames from:
```
git clone https://github.com/danielmiessler/SecLists
sudo apt install seclists -y
```