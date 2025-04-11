# 🌀 XRP Grid Trading Bot

> ⚠️ **Disclaimer:**  
> This project is for educational and experimental purposes only.  
> It does **not** constitute financial advice, investment recommendations, or trading guarantees.  
> Use at your own risk.

**Version 4.2.0**  
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
│   ├── ai/
│   ├── strategy/
│   ├── config_loader.py
│   └── main.py
├── docs/
│   ├── README_AI.md
│   ├── CONTRIBUTING.md
│   └── SECURITY.md
```

---

## 🧭 Documentation

- [📘 AI Integration Guide](docs/README_AI.md)
- [🤝 Contributing](docs/CONTRIBUTING.md)
- [🔐 Security Policy](docs/SECURITY.md)

---

## 👤 Author

**Yan Urquiza**  
📧 Email: [ulcan19@pm.me](mailto:ulcan19@pm.me)  
Crypto builder • Ethical hacker • Post-capitalist dreamer

MIT License — Use, fork, improve.  
If this helps you, pay it forward. If it inspires you, reach out.  
Together, we code beyond borders.

---

### 🧪 Testing Status (Read Before Use)

> ⚠️ **Disclaimer:**
>
> This bot has not been heavily tested yet.  
> We are in the process of building its core architecture, and many features are still experimental.

- ✅ It works on small amounts and behaves as expected under most conditions  
- 🚧 However, bugs or unexpected behaviors may still occur  
- 🧪 Full test coverage will follow the release of version 5.0

**We welcome early users and testers.**  
If you run into issues, please open an [issue](https://github.com/Karibusan/xrp-grid-trading-bot/issues) or share anonymized logs to help us improve.

> Together, we debug. Together, we grow.
