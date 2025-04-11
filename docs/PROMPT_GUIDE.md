# 🧠 Prompt Guide for AI Interaction

This guide defines what types of prompts are accepted by the bot's LLM interface.

---

## ⚠️ Prompt Policy

The LLM integrated in this project is minimal and experimental.  
To ensure reliability, we limit acceptable prompt types.

---

## ✅ Supported Prompt Types

### 1. `summarize_trades`
- Description: Generates a summary of trading activity
- Input: `log_summary.json`
- Example: `"Summarize today's trades and performance"`

### 2. `diagnose_strategy`
- Description: Checks strategy modules for errors or anomalies
- Input: logs or config snippets
- Example: `"Diagnose this strategy grid and suggest fixes"`

### 3. `optimize_grid`
- Description: Proposes adjustments to the grid based on past results
- Input: previous summary or trade outcomes
- Example: `"How should I adjust my grid based on these last trades?"`

---

## ❌ Not Supported

- General conversation
- Financial predictions
- Prompt injection