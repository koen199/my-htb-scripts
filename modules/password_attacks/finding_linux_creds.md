Look for config files, db, notes & scripts
```
for l in $(echo ".conf .config .cnf");do echo -e "\nFile extension: " $l; find / -name *$l 2>/dev/null | grep -v "lib\|fonts\|share\|core" ;done
for l in $(echo ".sql .db .*db .db*");do echo -e "\nDB File extension: " $l; find / -name *$l 2>/dev/null | grep -v "doc\|lib\|headers\|share\|man";done
find /home/* -type f -name "*.txt" -o ! -name "*.*"
for l in $(echo ".py .pyc .pl .go .jar .c .sh");do echo -e "\nFile extension: " $l; find / -name *$l 2>/dev/null | grep -v "doc\|lib\|headers\|share";done
```

Check for chron jobs
```
cat /etc/crontab 
ls -la /etc/cron.*/
```
Check the bash history
```
tail -n5 /home/*/.bash*
```


