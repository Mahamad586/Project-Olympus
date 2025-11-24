#!/bin/bash

TARGET=$1
RESULTS_DIR="recon_results/$TARGET"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M")
TARGET_DIR="$RESULTS_DIR/$TIMESTAMP"

echo "=================================================="
echo "Olympus Recon Module Activated for: $TARGET"
echo "=================================================="

mkdir -p $TARGET_DIR

echo "[*] Installing required tools..."
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
export PATH=$PATH:$(go env GOPATH)/bin

echo "[*] Running subfinder for subdomains..."
subfinder -d $TARGET -o $TARGET_DIR/subdomains.txt
echo "[+] Subfinder finished."

echo "[*] Running httpx to find live web servers..."
cat $TARGET_DIR/subdomains.txt | httpx -o $TARGET_DIR/live_hosts.txt
echo "[+] httpx finished."

echo "=================================================="
echo "Recon module for $TARGET has completed its mission."
echo "Results saved in: $TARGET_DIR"
echo "=================================================="
