With the smbclient tool you can enumerate shares on a target host
```
smbclient -N -L \\\\10.129.42.254
```

Login to a specific share as a user (bon)

```
smbclient -U bob \\\\10.129.42.254\\users
```