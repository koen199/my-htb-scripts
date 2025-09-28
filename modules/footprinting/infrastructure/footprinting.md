# Footprinting

## Finding subdomains and open port using public information
### Certificate inspection
Examination of the SSL-certificate can lead to other domains used by the company

### Crt.sh 
* `crt.sh` Certificate Transparency is a process that is intended to enable the verification of issued digital certificates for encrypted Internet connections ( https://crt.sh/ ) 

```
#List all domains similar to "infranefreight" found with crt.sh (registrated certificates with similar domain names) into a file "subdomainlist"
curl -s https://crt.sh/\?q\=inlanefreight.com\&output\=json | jq . | grep name | cut -d":" -f2 | grep -v "CN=" | cut -d'"' -f2 | awk '{gsub(/\\n/,"\n");}1;' | sort -u > subdomainlist

#Find ip addresses of these domains
for i in $(cat subdomainlist);do host $i | grep "has address" | grep inlanefreight.com | cut -d" " -f4 >> ip-addresses.txt;done
```

### Shodan

Shodan can be used too find open ports on the found IP addresses

```
for i in $(cat ip-addresses.txt);do shodan host $i;done
```

## DNS records

Query the DNS records of the domain to uncover usefull information
```
dig any inlanefreight.com
```

## Searching cloud storage

We can use google to look for documents stored in cloud storage

```
google this (Azure)
intext:company inurl:blob.core.windows.net

google this (AWS)
intext:company inurl:amazoneaws.com
```

## Usefull sites
https://buckets.grayhatwarfare.com/


