# 📜 Changelog

## [4.3.0] — 2025-04-11

### 💌 Daily Report by Email (NEW)

- Added `scripts/email_report.py` to generate and send a daily trading summary
- Report includes trades, session info, module usage, error count, basic suggestions
- SMTP support via `.env` — fully configurable

### 🧠 Improved AI Integration

- Updated `README_AI.md` with instructions to activate/deactivate AI features
- `.env.example` now includes full LLM configuration block
- AI behavior is now fully toggleable and documented

### 📚 Documentation & Dev Experience

- New `docs/CONFIG_GUIDE.md`: explains all `.env` and `config.json` parameters
- Added `config/config.json.example` (now valid JSON without comments)
- New `scripts/README.md` explains the purpose of each utility script
- New section “🧪 Experimental Config Files” in `CONFIG_GUIDE.md` for future modules
- `.env.example` made more readable with clear headers and emoji sections

### 🛠 Dev-Ready & Community-Friendly

- Consistent naming across all config files
- Scripts folder validated and commented
- Project now easier to contribute to (dev onboarding, future PRs)

> 🧠 This version prepares the ground for v5.0: full AI integration, multi-agent logic, and config introspection.

## [4.2.0] — 2025-04-11

### 🔧 System Consolidation

- Unified configuration format (.env and config.json)
- Cleaned up unused imports and legacy AI references
- Added fallback behavior for missing config values
- Improved logging format for module outputs

### 📁 File & Structure Cleanup

- Renamed ambiguous variables and folders
- Added clear module boundaries in strategy and ai layers
- Cleaned legacy logs and commented unused configs

### 🧪 Dev Mode Compatibility

- DRY_RUN now respected across all modules
- Improved stability for Synology deployment