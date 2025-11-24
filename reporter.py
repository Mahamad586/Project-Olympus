import os
import requests
import sys

def send_discord_notification(webhook_url, message):
    if not webhook_url:
        print("[WARN] Discord webhook URL is not set. Skipping notification.")
        return
        
    data = {"content": message}
    try:
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()
        print("[INFO] Successfully sent notification to Discord.")
    except requests.exceptions.RequestException as e:
        print(f"[ERR] Failed to send Discord notification: {e}")

def analyze_and_report(target, webhook_url):
    report_parts = [f"## 🏛️ Olympus Report for: `{target}`"]
    base_path = "recon_results"
        
    # Find the latest timestamped directory for the target
    target_path = os.path.join(base_path, target)
    if not os.path.exists(target_path):
        report_parts.append("❌ No results directory found. The workflow might have failed early.")
        send_discord_notification(webhook_url, "\n".join(report_parts))
        return

    all_dirs = [os.path.join(target_path, d) for d in os.listdir(target_path) if os.path.isdir(os.path.join(target_path, d))]
    if not all_dirs:
        report_parts.append("❌ No timestamped result directory found inside the target folder.")
        send_discord_notification(webhook_url, "\n".join(report_parts))
        return
            
    latest_dir = max(all_dirs, key=os.path.getmtime)
    report_parts.append(f"📁 Results Path: `{latest_dir}`")

    # Check Nuclei findings
    nuclei_file = os.path.join(latest_dir, "nuclei_findings.txt")
    if os.path.exists(nuclei_file) and os.path.getsize(nuclei_file) > 0:
        with open(nuclei_file, 'r') as f:
            findings = f.readlines()
            
        high_critical_findings = [line.strip() for line in findings if "[high]" in line or "[critical]" in line]
            
        if high_critical_findings:
            report_parts.append("\n**🚨 HIGH/CRITICAL VULNERABILITIES FOUND! 🚨**")
            for finding in high_critical_findings:
                report_parts.append(f"```{finding}```")
        else:
            report_parts.append("\n✅ No high/critical vulnerabilities found by Nuclei.")
            report_parts.append(f"Total findings: {len(findings)}")
    else:
        report_parts.append("\n⚠️ Nuclei findings file is empty or missing.")

    final_report = "\n".join(report_parts)
    send_discord_notification(webhook_url, final_report)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python reporter.py <target_domain>")
        sys.exit(1)
        
    target_domain = sys.argv[1]
    discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")
        
    analyze_and_report(target_domain, discord_webhook)
