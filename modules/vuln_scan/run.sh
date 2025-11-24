#!/bin/bash

TARGET=$1
RESULTS_DIR="recon_results/$TARGET"
LATEST_DIR=$(ls -td $RESULTS_DIR/*/ | head -1)

if [ ! -d "$LATEST_DIR" ]; then
  echo "[ERR] Reconnaissance results not found for $TARGET. Run 'recon' module first."
  exit 1
fi

LIVE_HOSTS_FILE="$LATEST_DIR/live_hosts.txt"
NUCLEI_OUTPUT_FILE="$LATEST_DIR/nuclei_findings.txt"

echo "=================================================="
echo "Olympus Vulnerability Scan Module Activated for: $TARGET"
echo "Using live hosts from: $LIVE_HOSTS_FILE"
echo "=================================================="

if [ ! -f "$LIVE_HOSTS_FILE" ] || [ ! -s "$LIVE_HOSTS_FILE" ]; then
    echo "[WRN] live_hosts.txt is empty or does not exist. Skipping Nuclei scan."
    exit 0
fi

echo "[*] Installing Nuclei..."
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
export PATH=$PATH:$(go env GOPATH)/bin
nuclei -update-templates

echo "[*] Running Nuclei against live hosts..."
nuclei -l $LIVE_HOSTS_FILE -t "technologies,cves,vulnerabilities,misconfiguration" -o $NUCLEI_OUTPUT_FILE

echo "[+] Nuclei scan finished."
echo "=================================================="
echo "Vulnerability Scan module for $TARGET has completed."
echo "Results saved in: $NUCLEI_OUTPUT_FILE"
echo "=================================================="
