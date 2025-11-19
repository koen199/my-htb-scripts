#!/bin/bash

# Path to the directory containing wordlists
WORDLIST_DIR="/snap/seclists/current/Passwords"
# Path to the file containing NTLM hashes
HASH_FILE="hash2.txt"

# Find all .txt files and loop through them
find "$WORDLIST_DIR" -type f -name '*.txt' | while read -r FILEPATH; do
    echo "Running John with wordlist: $FILEPATH"
    /home/azureuser/repositories/john/run/john --wordlist="$FILEPATH" --format=NT "$HASH_FILE"
done
