# 📜 Changelog

## [4.2.0] — 2025-04-11

### 🧠 Log Intelligence & AI Preparation

- Added `log_summarizer.py` to auto-generate daily JSON summaries of trading logs
- Created `PROMPT_GUIDE.md` to define acceptable AI prompt types
- Introduced `log_formatter.py` for structured, JSON-based logging
- Added `validate_env.py` to check required environment variables on startup
- Established `/logs/summary/` for AI-ready memory architecture

> This version lays the foundation for autonomous, intelligent bot behavior in v5.0.  
> Structured logs = memory. Prompts = communication. AI = augmentation.

---

## [4.1.0] — 2025-04-11

### 🚧 Consolidation & Core Reinforcement

- Added `requirements.txt` with minimal clean dependencies
- Added `.gitignore` to exclude logs, compiled files, env
- Added `setup.py` for optional future packaging

### 🧪 Testing & CI

- Introduced `tests/` directory with first unit test (`config_loader`)
- Added GitHub Actions (`ci.yml`) to run tests automatically on push/PR
- Modularized testing structure for future extensions

### 📚 Documentation Expansion

- `README.md` updated with legal disclaimer and clear doc links
- `README_AI.md` now includes a dedicated AI usage disclaimer
- Added `CONTRIBUTING.md` for external collaborators
- Added `SECURITY.md` for vulnerability reporting
- Added `ROADMAP.md` outlining v5.0 and beyond

---

## [4.0.0] — 2025-04-10

### 🔁 Modular AI Bot Core

- Refactored structure into `/src/`, `/strategy/`, `/ai/`
- Enabled optional OpenAI integration for strategy advising
- Added `.env` support and Synology NAS compatibility
- Docker and local run support
- Included Pushover notification integration

---

## [3.0.2] — Legacy Version

- Stable trading grid with basic config
- First draft of strategy modules
- Lacked AI features or structured logging