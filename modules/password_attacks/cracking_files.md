Finding private keys on a system

```
grep -rnE '^\-{5}BEGIN [A-Z0-9]+ PRIVATE KEY\-{5}$' /* 2>/dev/null
```

We can check if the found keys are encrypted by "opening" them, if we need to input 
a passphrase they are encrypted.
```
ssh-keygen -yf ~/.ssh/id_ed25519 
```

# Cracking an excel file

```
python3 office2john.py Confidential.xlsx > excel.hash    #generate hash
john --format=office --wordlist=rockyou.txt excel.hash   #crack the hash
john excel.hash --show #show the password
```
/dev/loop8

sudo dislocker /dev/loop27 -u1234qwer -- /media/bitlocker

sudo dislocker /dev/loop27 -u1234qwer -- /media/bitlocker