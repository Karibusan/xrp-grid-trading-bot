# 🌀 XRP Grid Trading Bot

**Version 3.1.0-dev**  
Open-source automated trading bot for Kraken (XRP/USD), running 24/7 on local machines, NAS, or Docker containers.

---

## ⚙️ Features

- 🔁 Automated buy/sell trading on Kraken using a grid strategy
- 🧠 Modular and extensible strategy logic (`strategy/`)
- 📲 Pushover notifications (buy/sell/errors)
- 🐳 Docker-ready with `.env` support
- 🔐 No cloud, no tracking — fully local

---

## 📁 Project structure

```
├── src/
│   ├── main.py                 → entry point
│   ├── config_loader.py       → config merge from .env + JSON
│   └── strategy/              → trading logic (plugins)
├── config/
├── logs/
├── scripts/
├── requirements.txt
├── .env.example
├── docker-compose.yml
└── Dockerfile
```

---

## 🚀 Deployment

### 1. Clone the repository

```bash
git clone https://github.com/Karibusan/xrp-grid-trading-bot.git
cd xrp-grid-trading-bot
```

### 2. Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Then fill in your Kraken API keys and Pushover credentials.

### 3. Run with Docker

```bash
docker-compose up --build -d
```

### 4. Logs

```bash
docker logs -f xrp-grid-bot
```

---

## ⚙️ .env Variables

| Variable | Description |
|----------|-------------|
| `API_KEY` | Kraken API key |
| `API_SECRET` | Kraken API secret |
| `PUSHOVER_USER_KEY` | Pushover user key |
| `PUSHOVER_API_TOKEN` | Pushover API token |
| `SYMBOL` | e.g., `XXRPZUSD` |
| `BASE_CURRENCY` | e.g., `XRP` |
| `QUOTE_CURRENCY` | e.g., `USD` |
| `TRADE_AMOUNT` | Amount per trade |
| `DRY_RUN` | `true` or `false` |
| `LOG_LEVEL` | `INFO`, `DEBUG`, `ERROR` |
| `PUID/PGID` | (optional) for Synology Docker permissions |
| `TZ` | e.g., `Europe/London` |

---

## 🧪 Simulation mode (dry-run)

To test the bot without making real trades:

```env
DRY_RUN=true
```

---

## 🔭 Upcoming features

- 📊 Web dashboard (Flask? React?)
- 🧬 Historical market data (via `data/`)
- 💾 Auto-backup of config (via `backups/`)
- 🧠 Machine-learning strategies (boss stuff 😅)

---

## 🤝 Contributing

- Forks and pull requests welcome!
- Clean and commented code under MIT license
- If you’re a solo dev with sleeping crypto: this bot is for you.

---

## 👤 Author

**Karibusan**  
Crypto builder / ethical hacker / post-capitalist dreamer  
MIT License — Do whatever you want with it, as long as it helps someone.

---

## 🕯️ Tribute

This bot is dedicated to **Blaise le Balèze**,  
a legendary Commodore 64 who powered a generation of dreams.  
1980s silicon. Eternal soul.
