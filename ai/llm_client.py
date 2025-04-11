import os

def ask_llm(prompt, model=None):
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if provider == "openai":
        from .providers import openai
        return openai.ask(prompt, model)
    
    elif provider == "mistral":
        from .providers import mistral
        return mistral.ask(prompt, model)

    elif provider == "local":
        from .providers import local_llama
        return local_llama.ask(prompt, model)

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")