import subprocess
import json
import os

with open('config.json') as fh:
    CONFIG:dict = json.load(fh)

def scan_directories_with_gobuster(root_path:str):
    protocol = CONFIG.get('GOBUSTER_PROTOCOL', 'http')
    port = CONFIG.get('GOBUSTER_PORT', '80')
    ip = CONFIG['TARGET_IP_ADDRESS']
    url = f"{protocol}://{ip}:{port}/{root_path}"
    wordlist = CONFIG.get('GOBUSTER_WORD_LIST', '/snap/seclists/Discovery/Web-Content/common.txt')
    folder = 'root' if root_path == '' else root_path
    path = f'./gobustor/{folder}'
    os.makedirs(path, exist_ok=True)
    cmd = [
        'gobuster',
        'dir',
        '-u' ,
        url,
        '--wordlist',
        wordlist, 
        '-o',
        f'{path}/output.txt'
    ]
    cmd_str = ' '.join(cmd)
    print(f'Executing command: {cmd_str}')
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )
    print(result.stdout)

for root_dir in CONFIG['GOBUSTER_ROOT_DIRECTORIES']:
    scan_directories_with_gobuster(root_dir)