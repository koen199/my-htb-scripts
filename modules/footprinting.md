# Footprinting

## Finding subdomains
* Examination of the SSL-certificate can lead to other domains used by the company
* `crt.sh` Certificate Transparency is a process that is intended to enable the verification of issued digital certificates for encrypted Internet connections ( https://crt.sh/ ) 

```
#Find all subdomains using crt.sh
curl -s https://crt.sh/\?q\=inlanefreight.com\&output\=json | jq . | grep name | cut -d":" -f2 | grep -v "CN=" | cut -d'"' -f2 | awk '{gsub(/\\n/,"\n");}1;' | sort -u
```


