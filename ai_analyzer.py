import os
import sys
import requests

# API URL for a free, public LLM provider (Ollama with Llama3)
# This is for demonstration. For production, a private key/service is better.
LLM_API_URL = "https://api.deepinfra.com/v1/openai/chat/completions"
# NOTE: This is a public endpoint and may have rate limits.

def analyze_findings_with_ai(findings_text, api_key):
    if not findings_text:
        return "No findings to analyze.", "info"

    if not api_key:
        return "AI analysis skipped: API key is not configured.", "warning"

    prompt = f"""
    You are a senior penetration tester. Your task is to analyze a Nuclei scan result and provide a brief, actionable summary for a bug bounty hunter.

    Scan Results:
    ---
    {findings_text}
    ---

    Instructions:
    1. Identify the MOST CRITICAL finding. If there are multiple critical ones, pick one.
    2. Ignore low or informational findings.
    3. Provide a 1-2 sentence summary of the critical finding.
    4. Suggest a 1-sentence next step for the hunter to verify it.
    5. If no significant findings are present, just state "No significant vulnerabilities found."

    Your response should be very short and direct.
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
        
    payload = {
        "model": "meta-llama/Llama-3-8b-chat-hf",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 150
    }

    try:
        response = requests.post(LLM_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        summary = result['choices'][0]['message']['content'].strip()
        return summary, "critical"
    except Exception as e:
        return f"AI analysis failed: {str(e)}", "error"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ai_analyzer.py <path_to_findings_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    api_key = os.getenv("DEEPINFRA_API_TOKEN")

    try:
        with open(file_path, 'r') as f:
            content = f.read()
        summary, _ = analyze_findings_with_ai(content, api_key)
        print(summary)
    except FileNotFoundError:
        print(f"Error: Findings file not found at {file_path}")
        sys.exit(1)

