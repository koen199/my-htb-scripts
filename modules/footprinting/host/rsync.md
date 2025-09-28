# Rsync

Find possible rsync servers
```
sudo nmap -sV -p 873 127.0.0.1 (here localhost)

#Connect to them via nc
nc -nv 127.0.0.1 873
#execute command to list shares
list

#Enumerate files
rsync -av --list-only rsync://127.0.0.1/dev
```