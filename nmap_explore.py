import subprocess
import os
import json
import xml.etree.ElementTree as ET



with open('config.json') as fh:
    CONFIG = json.load(fh)

def create_folders():
    #Create required folders
    os.makedirs('./nmap_result', exist_ok=True)
    os.makedirs('./nmap_result/no_scripts_result', exist_ok=True)
    os.makedirs('./nmap_result/with_scripts_result', exist_ok=True)

def scan_all_ports_without_scripts():
    print('Scan open ports and do non-invasive service discovery')
    result = subprocess.run(
        ['nmap', '-sV', '-p-', '-oA', 'nmap_result/no_scripts_result/common_ports',CONFIG['TARGET_IP_ADDRESS']], 
        capture_output=True,
        text=True
    )
    print("Output:\n", result.stdout)
    print("Errors:\n", result.stderr)

def scan_all_ports_with_scripts(open_ports:list[str]):
    print('Do invasive scan on open ports')
    result = subprocess.run(
        ['nmap', '-sV', '-sC', '-p', ','.join(open_ports), '-oA', 'nmap_result/with_scripts_result/common_ports',CONFIG['TARGET_IP_ADDRESS']], 
        capture_output=True,
        text=True
    )
    print("Output:\n", result.stdout)
    print("Errors:\n", result.stderr)

def read_open_ports()->list[str]:
    tree = ET.parse('nmap_result/no_scripts_result/common_ports.xml')
    root = tree.getroot()
    ports = root.findall('.//port')
    return [p.get('portid') for p in ports]


create_folders()
scan_all_ports_without_scripts()
open_ports = read_open_ports()
scan_all_ports_with_scripts(open_ports)