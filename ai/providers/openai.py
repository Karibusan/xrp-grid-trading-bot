import os
import requests

def ask(prompt, model=None):
    model = model or os.getenv("LLM_MODEL", "gpt-4")
    api_key = os.getenv("LLM_API_KEY")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    json_data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a crypto trading assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=json_data
    )

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"OpenAI API Error: {response.status_code} {response.text}")