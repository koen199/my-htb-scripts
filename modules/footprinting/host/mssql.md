# MSSQL
A SQL database developed by microsoft

Scanning the target with scripts:

```
sudo nmap --script ms-sql-info,ms-sql-empty-password,ms-sql-xp-cmdshell,ms-sql-config,ms-sql-ntlm-info,ms-sql-tables,ms-sql-hasdbaccess,ms-sql-dac,ms-sql-dump-hashes --script-args mssql.instance-port=1433,mssql.username=sa,mssql.password=,mssql.instance-name=MSSQLSERVER -sV -p 1433 10.129.201.248
```

Use metasploit to footprint further
```
msfconsole
use auxiliary/scanner/mssql/mssql_ping
show options
set rhosts 10.129.201.248
run
```

Using the testclient

```
python3 mssqlclient.py Administrator@10.129.201.248 -windows-auth
```