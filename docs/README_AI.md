# 🧠 AI Integration — XRP Grid Trading Bot (v4.0+)

This bot includes optional AI-driven strategy suggestions via LLMs (large language models).  
You can plug any compatible provider, from OpenAI to your own local Ollama server.

---

## 💡 Purpose

The AI module reads and interprets trade logs or summaries, then proposes strategic insights.  
Use it for:

- Detecting patterns in trades
- Getting real-time strategic suggestions
- Running post-trade analysis with fresh ideas

---

## ⚙️ Supported Providers

| Provider     | Environment setup                        | Notes                          |
|--------------|-------------------------------------------|--------------------------------|
| **OpenAI**   | `LLM_PROVIDER=openai`                     | Requires API key               |
| **Ollama**   | `LLM_PROVIDER=local`                      | No key required, self-hosted   |
| **Mistral (HuggingFace)** | `LLM_PROVIDER=mistral`       | Future support planned         |

---

## 🔧 .env Example (OpenAI)

```env
LLM_PROVIDER=openai
LLM_API_KEY=sk-xxxxxxxxxx
LLM_MODEL=gpt-4
```

## 🔧 .env Example (Local via Ollama)

```env
LLM_PROVIDER=local
LLM_LOCAL_URL=http://localhost:11434
LLM_MODEL=mistral
```

---

## 📥 How it works

Call this in your strategy logic or manually:

```python
from strategy.ai_strategy_advisor import evaluate_market

log_excerpt = "2025-04-12 01:12:03 - BUY at 0.52 | 2025-04-12 01:37:42 - SELL at 0.54"
suggestion = evaluate_market(log_excerpt)
print(suggestion)
```

The result is logged and returned as text.

---

## 🔐 Privacy & Philosophy

All AI support is **optional** and **modular**.  
No vendor lock-in. You choose your model, your hosting, your privacy.

We believe in tools that serve people, not the other way around.

MIT licensed. Post-capitalist friendly.