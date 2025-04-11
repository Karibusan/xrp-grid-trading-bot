# scripts/email_report.py

import os
import smtplib
from email.message import EmailMessage
import json
from datetime import datetime

SUMMARY_DIR = "logs/summary/"
DEFAULT_SUMMARY_FILE = f"log_summary_{datetime.now().strftime('%Y-%m-%d')}.json"

def load_summary(filename=None):
    if not filename:
        filename = os.path.join(SUMMARY_DIR, DEFAULT_SUMMARY_FILE)
    if not os.path.exists(filename):
        return None
    with open(filename, 'r') as f:
        return json.load(f)

def generate_email_body(summary):
    if not summary:
        return "No data available for the selected day."

    body = f"""
📊 DAILY REPORT - {summary['date']}

🔁 Session ID: {summary['session_id']}
💰 Trades executed: {len(summary.get('trades', []))}
🧠 Modules used: {", ".join(summary.get('modules', [])) or "N/A"}
⚠️ Errors: {len(summary.get('errors', []))}

—

Suggestions (basic):
- Consider adjusting grid width if trades = 0
- Validate API keys if errors occurred
"""
    return body.strip()

def send_email(subject, content):
    if os.getenv("EMAIL_ENABLED", "false").lower() != "true":
        print("Email sending disabled by config.")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = os.getenv("SMTP_USER")
    msg["To"] = os.getenv("REPORT_RECIPIENT")
    msg.set_content(content)

    try:
        with smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT"))) as server:
            server.starttls()
            server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD"))
            server.send_message(msg)
            print("Daily report sent.")
    except Exception as e:
        print(f"Error sending report: {e}")

if __name__ == "__main__":
    summary = load_summary()
    body = generate_email_body(summary)
    send_email("📬 XRP Bot - Daily Report", body)
