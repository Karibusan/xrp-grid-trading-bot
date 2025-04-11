# 🤖 AI Integration — XRP Grid Trading Bot

> ⚠️ This AI system is experimental and educational. It is not intended as a financial advisor.

---

## 🔧 How to enable or disable the AI

To activate the AI modules (strategy advisor, log suggestions), edit your `.env`:

```dotenv
AI_ENABLED=true
```

To disable all AI functionality (default fallback mode):

```dotenv
AI_ENABLED=false
```

---

## ⚙️ AI Configuration Variables

| Variable       | Description                                 | Example                  |
|----------------|---------------------------------------------|--------------------------|
| `AI_ENABLED`   | Activate the AI layer (true/false)          | `true`                   |
| `LLM_PROVIDER` | The AI provider to use                      | `openai`, `local`, etc. |
| `AI_MODEL`     | Model to call                               | `gpt-4`, `mistral-7b`    |
| `TEMPERATURE`  | Randomness of the AI (0 = deterministic)    | `0.7`                    |
| `MAX_TOKENS`   | Max token length of output                  | `500`                    |
| `LOG_PROMPTS`  | Log prompts sent to the LLM (true/false)    | `true`                   |

---

## 📬 Daily Reporting (Optional)

The AI may provide suggestions in the daily report based on your logs.  
To enable this, make sure `EMAIL_ENABLED=true` and fill out SMTP config.

---

## 🧠 Prompt Types Supported

See [`docs/PROMPT_GUIDE.md`](./PROMPT_GUIDE.md) for prompt types and rules.

---

## 🔐 Ethical & Safe

This bot favors:
- Local-first & private-by-default AI
- Full transparency of config and behavior
- Modularity for future open-source LLMs

---