# Exam
First let's try to find the subdomains
First add `academy.htb` to `/etc/hosts`

Then run ffuz for VHOST discovery:
```
ffuf -w /snap/seclists/current/Discovery/DNS/subdomains-top1million-5000.txt:FUZZ -u http://academy.htb:38981/ -H 'Host: FUZZ.academy.htb' -fs 985
```
We found three domains:
```
archive.academy.htb
faculty.academy.htb
test.academy.htb
```

To find file extensions run the following command for each subdomain:
```
ffuf -w /snap/seclists/current/Discovery/Web-Content/web-extensions.txt:FUZZ -u http://faculty.academy.htb:38981/indexFUZZ
```
We find following extensions are in use: `php,phps,php7`

Next we should find a url which return "You don't have access"... 
```
ffuf -w /snap/seclists/current/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-small.txt:FUZZ -u http://faculty.academy.htb:38981/FUZZ -recursion -recursion-depth 2 -e .php,.phps,.php7  -v -ic -fr "You don't have permission to access this resource."
```

Which gave us a hit on `http://faculty.academy.htb:38981/courses/linux-security.php7`

Next question is to find the parameters this php page accepts...
Let's try the POST request fuzzing first

```
ffuf -w /snap/seclists/current/Discovery/Web-Content/burp-parameter-names.txt:FUZZ  -u http://faculty.academy.htb:38981/courses/linux-security.php7 -X POST -d 'FUZZ=oeps' -H 'Content-Type: applicati
on/x-www-form-urlencoded' -fs 774
```
This lead to the following result: `user` and `username` returned results of different response sizes indicating it could be a parameter.

Next lets fuzz for a valid username:
```
ffuf -w names.txt:FUZZ  -u http://faculty.academy.htb:38981/courses/linux-security.php7 -X POST -d 'username=FUZZ' -H 'Content-Type: application/x-www-form-urlencoded' -fs 781
```
This returns `harry`

Let's check it out with curl to find the flag:
```
curl http://faculty.academy.htb:38981/courses/linux-security.php7 -X POST -d 'username=harry' --header 'Content-Type: application/x-www-form-urlencoded'
```

