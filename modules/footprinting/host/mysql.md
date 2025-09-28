# MySQL

Footprinting a possible mssql service
```
sudo nmap 10.129.14.128 -sV -sC -p3306 --script mysql*
```

Login to a mysql service
```
mysql -u root -h 10.129.14.132
```

