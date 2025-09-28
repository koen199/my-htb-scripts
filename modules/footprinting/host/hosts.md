# Host based fingerprinting

## FTP
using following command to get to ftp server as anonymous user
```
ftp anonymous@IP_ADDREESSS
get flag.txt
```

## SMB

Display a list of all shares logged in as the anonymous user
```
smbclient -N -L //10.129.14.128

#After enumaration log in to a specific share "notes"
smbclient //10.129.14.128/notes
#List possible commands using "help"
help
```

System commands can be run when logged in via the smbclient by prefixing the command with "!", For example:
```
!ls
```

### rpcclient
We can interact with the SMB server via an RPC client
```
rpcclient -U "" 10.129.14.128

#Run the help command to list which RPC calls are possible as this user
help

#User enumeration is especially usefull and can be done via 
enumdomusers

#Given the output a user can be queried with 
queryuser 0x3e9

However, it can also happen that not all commands are available to us, and we have certain restrictions based on the user. However, the query queryuser <RID> is mostly allowed based on the RID. So we can use the rpcclient to brute force the RIDs to get information

for i in $(seq 500 1100);do rpcclient -N -U "" 10.129.14.128 -c "queryuser 0x$(printf '%x\n' $i)" | grep "User Name\|user_rid\|group_rid" && echo "";done

### Impacket - Samrdump.py
```
#We can also use a samrdump.py script for this
samrdump.py 10.129.14.128
```

### SMBMap
```
smbmap -H 10.129.14.128
```

### CrackMapExec
```
crackmapexec smb 10.129.14.128 --shares -u '' -p ''
```
### Enum4Linux
```
./enum4linux-ng.py 10.129.14.128 -A
```

## NFS
NFS (Netwok file sharing) typically uses two ports (111 ->portmapper and 2049 --> actual NFS service)

You can discover stuff about possible NFS with nmap using some scripts
```
sudo nmap --script nfs* 10.129.14.128 -sV -p111,2049
```

Show available mounts
```
showmount -e 10.129.14.128
```

Mounting NFS Share
```
mkdir test
sudo mount -t nfs 10.129.26.136:/var/nfs /home/azureuser/repositories/my-htb-scripts/test
cd test
tree .

#as specific user
sudo mount -t nfs -o uid=$uid,gid=$gid 10.129.26.136:/var/nfs /home/azureuser/repositories/my-htb-scripts/test

#unmount later
sudo umount ./test
```

# DNS

Find other related zones
```
dig ns inlanefreight.htb @10.129.14.128
```

Find the version of the DNS-server
```
dig CH TXT version.bind 10.129.120.85
```

Show more info (not all will be shown)
```
dig any inlanefreight.htb @10.129.14.128
```

Ask for a zone transfer (sync from primarty to seconday DNS servers)... Potentially internal IP addresses could leak 
```
dig axfr internal.inlanefreight.htb @10.129.14.128
```

Subdomain brute forcing using a word list
```
for sub in $(cat /opt/useful/seclists/Discovery/DNS/subdomains-top1million-110000.txt);do dig $sub.inlanefreight.htb @10.129.14.128 | grep -v ';\|SOA' | sed -r '/^\s*$/d' | grep $sub | tee -a subdomains.txt;done
```

Also tools like DNSenum can be used for this
```
dnsenum --dnsserver 10.129.14.128 --enum -p 0 -s 0 -o subdomains.txt -f /opt/useful/seclists/Discovery/DNS/subdomains-top1million-110000.txt inlanefreight.htb
```