#!/bin/bash

TARGET=$1
RESULTS_DIR="recon_results/$TARGET"
LATEST_DIR=$(ls -td $RESULTS_DIR/*/ | head -1)
APK_ANALYSIS_DIR="$LATEST_DIR/apk_analysis"

echo "=================================================="
echo "Olympus Android Hunter Module Activated for: $TARGET"
echo "=================================================="

# Simple check for APK links in live hosts (this is a basic example)
LIVE_HOSTS_FILE="$LATEST_DIR/live_hosts.txt"
if [ ! -f "$LIVE_HOSTS_FILE" ]; then
    echo "[WRN] live_hosts.txt not found. Skipping Android scan."
    exit 0
fi

# Find APK URLs (a more advanced version would use a crawler)
APK_URLS=$(grep -iE '\.apk$' $LIVE_HOSTS_FILE | head -n 1)

if [ -z "$APK_URLS" ]; then
    echo "[INFO] No direct .apk links found for $TARGET. Skipping analysis."
    exit 0
fi

mkdir -p $APK_ANALYSIS_DIR
echo "[*] Found APK links. Starting analysis..."

# Install tools
sudo apt-get update
sudo apt-get install -y apktool

for url in $APK_URLS; do
    echo "[*] Downloading APK from: $url"
    wget -q -O "$APK_ANALYSIS_DIR/app.apk" "$url"

    if [ -f "$APK_ANALYSIS_DIR/app.apk" ]; then
        echo "[*] Decompiling APK..."
        apktool d -f "$APK_ANALYSIS_DIR/app.apk" -o "$APK_ANALYSIS_DIR/decompiled_code"

        echo "[*] Searching for secrets and sensitive info in decompiled code..."
        grep -rE 'api_key|secret|password|token' "$APK_ANALYSIS_DIR/decompiled_code" > "$APK_ANALYSIS_DIR/findings.txt"
            
        echo "[+] Android analysis complete. Findings saved."
    else
        echo "[ERR] Failed to download APK from $url."
    fi
done

echo "=================================================="
echo "Android Hunter module for $TARGET has completed."
echo "=================================================="
