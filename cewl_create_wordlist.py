import glob
import os
import json
import subprocess
from pathlib import Path
from urllib.parse import urljoin

with open('config.json') as fh:
    CONFIG:dict = json.load(fh)

def create_cewl_folder(gobuster_filepath:Path)->Path:
    cewl_path = Path('./cewl') / gobuster_filepath.parent.name
    os.makedirs(cewl_path, exist_ok=True)    
    return cewl_path

def make_urls(
    cewl_folder:Path,
    directories:str
)->list[tuple[str, Path]]:
    urls = []
    foldername = Path(cewl_folder.name)
    protocol = CONFIG['GOBUSTER_PROTOCOL']
    ip_address = CONFIG['TARGET_IP_ADDRESS']
    base_url_path = f'{protocol}://{ip_address}'
    for directory in directories:
        if foldername == Path('root'):
            p = Path(directory).relative_to('/')
        else:
            p = foldername / Path(directory).relative_to('/')
        f = Path('root') / p if foldername == Path('root') else p
        wordlist_path = Path('./cewl') / f / 'wordlist.txt'
        os.makedirs(wordlist_path.parent, exist_ok=True)
        url = urljoin(base_url_path, str(p))
        urls.append((url, wordlist_path))
    return urls
    
def create_word_list(
    cewl_folder:Path,
    directories:str
):
    
    urls = make_urls(cewl_folder, directories)
    for url, wordlist_path in urls:
        cmd = [
            'cewl',
            '--email', 
            url, 
            '--depth',
            str(CONFIG.get('CEWL_RECURSIVE_DEPTH', 3)), 
            '--write', 
            str(wordlist_path)
        ]
        cmd_str = ' '.join(cmd)
        print(f'Executing command: {cmd_str}')
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        print(result.stdout)

def parse_directories_from_file(gobuster_filepath:Path)->list[str]:
    """Extract directory paths from gobuster output file"""
    directories = []
    with open(gobuster_filepath, 'r') as fh:
        lines = fh.readlines()
    for line in lines:
        idx = line.find('(Status:')
        directories.append(line[:idx].strip())
    return directories

# Find all output.txt files in the gobustor folder and its subdirectories
gobuster_files = glob.glob("gobustor/**/output.txt", recursive=True)
gobuster_files:list[Path] = [Path(f) for f in gobuster_files]

for gobuster_filepath in gobuster_files:
    directories = parse_directories_from_file(gobuster_filepath)
    cewl_folder = create_cewl_folder(gobuster_filepath)
    create_word_list(cewl_folder, directories)
    