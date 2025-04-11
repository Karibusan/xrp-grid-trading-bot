import os
import json
from dotenv import load_dotenv

def load_config(config_path='config.json'):
    # Charger les variables depuis le fichier .env
    load_dotenv()

    # Config par défaut depuis le .env
    config = {
        "api_key": os.getenv("API_KEY"),
        "api_secret": os.getenv("API_SECRET"),
        "symbol": os.getenv("SYMBOL", "XXRPZUSD"),
        "base_currency": os.getenv("BASE_CURRENCY", "XRP"),
        "quote_currency": os.getenv("QUOTE_CURRENCY", "USD"),
        "pushover_user_key": os.getenv("PUSHOVER_USER_KEY"),
        "pushover_api_token": os.getenv("PUSHOVER_API_TOKEN"),
        "trade_amount": float(os.getenv("TRADE_AMOUNT", 5)),
        "dry_run": os.getenv("DRY_RUN", "false").lower() == "true",
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
    }

    # Si le fichier JSON existe, on le fusionne (écrase les valeurs .env si précisé)
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            print(f"[config_loader] Erreur de lecture du fichier config.json : {e}")

    return config
