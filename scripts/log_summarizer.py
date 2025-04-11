import os
import json
from datetime import datetime

LOG_DIR = "logs/"
SUMMARY_DIR = "logs/summary/"
SUMMARY_FILE = os.path.join(SUMMARY_DIR, f"log_summary_{datetime.now().strftime('%Y-%m-%d')}.json")

def summarize_logs():
    summary = {
        "date": datetime.now().isoformat(),
        "session_id": f"xrpbot-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "trades": [],
        "modules": set(),
        "errors": []
    }

    log_file = os.path.join(LOG_DIR, "bot.log")
    if not os.path.exists(log_file):
        print("No log file found.")
        return

    with open(log_file, "r") as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get("type") == "trade":
                    summary["trades"].append(entry)
                if module := entry.get("module"):
                    summary["modules"].add(module)
                if entry.get("level") == "ERROR":
                    summary["errors"].append(entry["message"])
            except json.JSONDecodeError:
                continue

    summary["modules"] = list(summary["modules"])

    os.makedirs(SUMMARY_DIR, exist_ok=True)
    with open(SUMMARY_FILE, "w") as out:
        json.dump(summary, out, indent=2)
    print(f"Summary saved to {SUMMARY_FILE}")

if __name__ == "__main__":
    summarize_logs()