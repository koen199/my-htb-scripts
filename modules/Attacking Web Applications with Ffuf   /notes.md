# ffuf

## Directory fuzzing

Assign a wordlist to a keyword argument and use it for directory discovery
```
ffuf -w /snap/seclists/current/Discovery/Web-Content/DirBuster-2007_directory-list-lowercase-2.3-small.txt:FUZZ -u http://94.237.122.95:33225/blog/indexFUZZ
```

Fuzz for common file extensions (assume page is named index)
```
ffuf -w /snap/seclists/current/Discovery/Web-Content/web-extensions.txt:FUZZ -u http://94.237.122.95:33225/blog/indexFUZZ
```

We can do recursive fuzzing as following (recursion depth = 1, meaning we go only 1 deep here and we try the pages with the .php extension)
The -ic is to suppress copyright warnings or some shit
```
ffuf -w /snap/seclists/current/Discovery/Web-Content/DirBuster-2007_directory-list-lowercase-2.3-small.txt:FUZZ -u http://94.237.122.95:33225/FUZZ -recursion -recursion-depth 1 -e .php -v -ic
```

## DNS fuzzing

We can find subdomains like this:
```
ffuf -w /snap/seclists/current/Discovery/DNS/subdomains-top1million-5000.txt:FUZZ -u http://FUZZ.inlanefreight.com
```

## VHOST fuzzing

This works for non-public webservers.. Basically we set the host header here:
```
ffuf -w /snap/seclists/current/Discovery/DNS/subdomains-top1million-5000.txt:FUZZ -u http://academy.htb:PORT/ -H 'Host: FUZZ.academy.htb'
```
Now this will typically return a `200` for each word in the list because the server actually responds.. Typically file sizes of non-existing pages are the same so we can filter them away with:

```
ffuf -w /snap/seclists/current/Discovery/DNS/subdomains-top1million-5000.txt:FUZZ -u http://academy.htb:47259/ -H 'Host: FUZZ.academy.htb' -fs 986
```
## Parameter fuzzing

Parameter fuzzing with GET-requests
```
ffuf -w /snap/seclists/current/Discovery/Web-Content/burp-parameter-names.txt:FUZZ -u http://admin.academy.htb:47259/admin/admin.php?FUZZ=key -fs 798
```
The file size is picked by seeing what is "normally" returned


Parameter fuzzing with POST-requests
```
ffuf -w /snap/seclists/current/Discovery/Web-Content/burp-parameter-names.txt:FUZZ -u http://admin.academy.htb:47259/admin/admin.php -X POST -d 'FUZZ=key' -H 'Content-Type: application/x-www-form-urlencoded'
```
```
ffuf -w ids.txt:FUZZ -u http://admin.academy.htb:47259/admin/admin.php -X POST -d 'id=FUZZ' -H 'Content-Type: application/x-www-form-urlencoded'
```


