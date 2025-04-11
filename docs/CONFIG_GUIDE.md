# ⚙️ Configuration Guide

This guide lists and explains all configuration parameters available in the `.env` file and optional `config.json`.

---

## 🔐 .env Parameters

| Variable           | Description                                      | Example               |
|--------------------|--------------------------------------------------|------------------------|
| `API_KEY`          | Kraken API key                                   | `XXXXXXXXXXXX`         |
| `API_SECRET`       | Kraken API secret                                | `YYYYYYYYYYYY`         |
| `SYMBOL`           | Trading pair                                     | `XXRPZUSD`             |
| `BASE_CURRENCY`    | Base currency symbol                             | `XRP`                  |
| `QUOTE_CURRENCY`   | Quote currency symbol                            | `USD`                  |
| `TRADE_AMOUNT`     | Amount to trade per operation                    | `5`                    |
| `DRY_RUN`          | Simulate trades only (no real orders)            | `true` or `false`      |
| `LOG_LEVEL`        | Log verbosity                                    | `INFO`, `DEBUG`, etc.  |
| `TZ`               | Timezone for logs and schedule                   | `Europe/London`        |
| `PUID` / `PGID`    | Docker user/group ID (Synology compatible)       | `1026`, `100`          |

---

## 🤖 AI Parameters

| Variable         | Description                          |
|------------------|--------------------------------------|
| `AI_ENABLED`     | Activate AI layer (`true` / `false`) |
| `LLM_PROVIDER`   | AI provider (`openai`, `local`, etc) |
| `AI_MODEL`       | LLM model name                       |
| `TEMPERATURE`    | Output randomness (0 to 1)           |
| `MAX_TOKENS`     | Max output length                    |
| `LOG_PROMPTS`    | Log prompts sent to the AI           |

---

## 📬 Email Report Parameters

| Variable           | Description                         |
|--------------------|-------------------------------------|
| `EMAIL_ENABLED`    | Enable/disable report email         |
| `SMTP_SERVER`      | SMTP server                         |
| `SMTP_PORT`        | SMTP port (usually 587)             |
| `SMTP_USER`        | Email user/login                    |
| `SMTP_PASSWORD`    | Password for email auth             |
| `REPORT_RECIPIENT` | Destination email address           |

---

## 🧾 config.json (optional override)

You can also define persistent parameters in a `config/config.json` file.

Example:

```json
{
  "symbol": "XXRPZUSD",
  "trade_amount": 5,
  "dry_run": true
}
```

If present, this will override `.env` values **unless explicitly disabled**.

---
---

## 🧪 Experimental Config Files

The following files are included for future modules that are still in development:

| Config File                                      | Purpose                                  | Status             |
|--------------------------------------------------|------------------------------------------|--------------------|
| `api_client_config.json.example`                | Used to define API endpoints and keys    | Planned for v6     |
| `capital_migration_config.json.example`         | Strategy module for capital shifting     | Placeholder        |
| `error_handler_config.json.example`             | Error management configuration           | Not yet integrated |
| `notification_config.json.example`              | Notification config (may duplicate .env) | To unify           |
| `signal_collapse_config.json.example`           | Collapse detection module config         | Not yet wired      |
| `strategic_bifurcation_config.json.example`     | Strategy decision-making module          | Placeholder        |
| `survivability_config.json.example`             | Module for survivability logic           | Planned            |
| `technological_convergence_config.json.example` | Convergence analysis module config       | Placeholder        |

> These files are safe to leave in the `config/` folder.  
> They are **not yet used in production**, but may be activated in v5+ depending on development progress.

---