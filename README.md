# 🌀 XRP Grid Trading Bot

> ⚠️ **Disclaimer:**  
> This project is for educational and experimental purposes only.  
> It does **not** constitute financial advice, investment recommendations, or trading guarantees.  
> Use at your own risk.


**Version 4.0-dev**  
Open-source automated trading bot for Kraken (XRP/USD), now powered by LLM-based strategy suggestions. Runs 24/7 on local machines, NAS, or Docker containers.

> A project born to give a second life to forgotten crypto —  
> Helping small holders leverage capital… without feeding the beast.

---

## ⚙️ Features

- 🔁 Automated buy/sell trading on Kraken using a grid strategy
- 🤖 Optional AI advisor (OpenAI, Mistral, local LLM via Ollama)
- 🧠 Modular strategy system with plugin architecture
- 📲 Pushover notifications (buy/sell/errors)
- 🐳 Docker-ready with `.env` support
- 🔐 Full local execution possible — no cloud dependency

---

## 📁 Project structure

```
xrp-grid-trading-bot/
├── src/
│   ├── main.py
│   ├── config_loader.py
│   ├── ai/
│   │   ├── llm_client.py
│   │   └── providers/
│   │       └── openai.py
│   └── strategy/
│       ├── ai_strategy_advisor.py
│       └── ... (other modules)
```

---

## 🚀 Quickstart

### 1. Clone the repository

```bash
git clone https://github.com/Karibusan/xrp-grid-trading-bot.git
cd xrp-grid-trading-bot
```

### 2. Configuration

Copy and customize the `.env` file:

```bash
cp .env.example .env
```

### 3. Run with Docker

```bash
docker-compose up --build -d
```

---

## 🧪 AI Integration (optional)

```env
LLM_PROVIDER=openai        # or local / mistral / huggingface
LLM_API_KEY=sk-...         # if required
LLM_MODEL=gpt-4
LLM_LOCAL_URL=http://localhost:11434  # for Ollama or local deployment
```

You can call AI strategy suggestions from logs using `ai_strategy_advisor.evaluate_market(log_excerpt)`.

---

## 🤝 Contributing

Forks welcome. Issues encouraged. PRs blessed.  
If this project helps you, pay it forward — and consider sharing how you used it.

---

## 👤 Author

**Yan Urquiza**  
📧 Email: [ulcan19@pm.me](mailto:ulcan19@pm.me)  
Crypto builder • Ethical hacker • Post-capitalist dreamer

MIT License — Use, fork, improve.  
If this helps you, pay it forward. If it inspires you, reach out.  
Together, we code beyond borders.
