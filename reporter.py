import os
import requests
import sys
import subprocess

def send_discord_notification(webhook_url, embed):
    if not webhook_url:
        print("[WARN] Discord webhook URL is not set. Skipping notification.")
        return
        
    data = {"embeds": [embed]}
    try:
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()
        print("[INFO] Successfully sent notification to Discord.")
    except requests.exceptions.RequestException as e:
        print(f"[ERR] Failed to send Discord notification: {e}")

def run_ai_analysis(findings_file):
    if not os.path.exists(findings_file) or os.path.getsize(findings_file) == 0:
        return "No findings file to analyze.", "info"
        
    try:
        # We need to call the ai_analyzer.py script
        process = subprocess.run(
            ['python', 'ai_analyzer.py', findings_file],
            capture_output=True, text=True, check=True
        )
        return process.stdout.strip(), "critical"
    except subprocess.CalledProcessError as e:
        return f"AI analysis script failed: {e.stderr}", "error"
    except FileNotFoundError:
        return "ai_analyzer.py not found.", "error"


def analyze_and_report(target, webhook_url):
    embed = {
        "title": f"🏛️ Olympus AI Report: `{target}`",
        "color": 0xaaaaaa, # Grey by default
        "fields": []
    }

    target_path = os.path.join("recon_results", target)
    if not os.path.exists(target_path):
        embed["description"] = "❌ No results directory found. The workflow might have failed early."
        embed["color"] = 0xff0000 # Red
        send_discord_notification(webhook_url, embed)
        return

    all_dirs = [os.path.join(target_path, d) for d in os.listdir(target_path) if os.path.isdir(os.path.join(target_path, d))]
    if not all_dirs:
        embed["description"] = "❌ No timestamped result directory found."
        embed["color"] = 0xff0000 # Red
        send_discord_notification(webhook_url, embed)
        return
            
    latest_dir = max(all_dirs, key=os.path.getmtime)
        
    nuclei_file = os.path.join(latest_dir, "nuclei_findings.txt")
        
    ai_summary, status = run_ai_analysis(nuclei_file)

    embed["fields"].append({"name": "🧠 AI Summary", "value": f"```{ai_summary}```"})

    if status == "critical" and "No significant" not in ai_summary:
        embed["color"] = 0xffd700 # Gold
        embed["description"] = "🚨 **Potential High-Impact Vulnerability Identified!**"
    elif status == "error":
        embed["color"] = 0xff0000 # Red
    else:
        embed["color"] = 0x00ff00 # Green
        embed["description"] = "✅ Scan complete. No critical issues flagged by AI."

    send_discord_notification(webhook_url, embed)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python reporter.py <target_domain>")
        sys.exit(1)
        
    target_domain = sys.argv[1]
    discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")
        
    analyze_and_report(target_domain, discord_webhook)
