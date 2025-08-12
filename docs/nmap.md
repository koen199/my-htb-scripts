Scan a target on a specific port and attempt to return to version of the service
```
sudo nmap -sV -p 8080 10.129.42.254
```

Scan a target on all the ports, with -sC run scripts to fingerprint the service, -sV attempts to find the version of the service
```
sudo nmap -sC -sV -p- 10.129.42.254
```

The oA command specifies that the output is saved to files in different formats
```
nmap -sV --open -oA nibbles_initial_scan 10.129.42.190
```

A good intial reccon approach could be
```
# Scan the 1000 most open port and output to a file... do service discovery (-sV)
nmap -sV --open -oA output_file <ip address>

# Already start a slow full port scan
nmap -p- --open -oA nibbles_full_tcp_scan 10.129.42.190.

#In the mean time run fingerprinting scripts on the found open ports (-sC)
nmap -sC -p 22,80 -oA nibbles_script_scan 10.129.42.190.

#On some service like http we can run specific scripts
nmap -sV --script=http-enum -oA nibbles_nmap_http_enum 10.129.42.190 
```

Do an aggresive scan 
```
-sC = Only runs default scripts.
-A = Runs default scripts plus OS detection, version detection, and traceroute.
sudo nmap 10.129.2.28 -p 80 -A
```

Scan for vulnerabilities
```
sudo nmap 10.129.2.28 -p 80 -sV --script vuln 
```