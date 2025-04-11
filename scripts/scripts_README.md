# 🛠️ scripts/ — Utility & Automation Scripts

This folder contains helper scripts for automation, maintenance, and deployment.

| Script                            | Description                                                      |
|----------------------------------|------------------------------------------------------------------|
| `backup.sh`                      | Backs up logs, data, and configurations (to `/backups`)         |
| `deploy_to_synology.sh`          | Deploys the bot in Docker on Synology using default `.env`      |
| `deploy_to_synology_custom.sh`   | Custom variant of Synology deploy (manual settings)             |
| `deploy_to_synology_with_password.sh` | Variant with SMTP password injection                       |
| `email_report.py`               | Generates & sends the daily report email                        |
| `log_summarizer.py`             | Analyzes raw logs and outputs a daily summary (JSON)            |
| `test_notifications.py`         | Sends a test Pushover notification to validate credentials      |

> These scripts are optional but useful for sysadmin/devops workflows.

All scripts are written to be executable from project root or mounted into a container.