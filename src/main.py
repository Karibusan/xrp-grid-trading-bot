import time
from config_loader import load_config
from utils.logger import setup_logger
from market.kraken_client import KrakenClient
from strategy import strategy_selector
from executor.trade_executor import TradeExecutor
from notifier.pushover import send_notification

# Charger la configuration fusionnée (.env + config.json)
config = load_config()

# Setup du logger
logger = setup_logger(log_level=config.get("log_level", "INFO"))

# Dry-run info
if config.get("dry_run"):
    logger.warning("⚠️ Le bot est en mode simulation (dry-run) : aucun trade réel ne sera effectué.")

# Initialisation du client Kraken et de l'exécuteur de trade
kraken = KrakenClient(config["api_key"], config["api_secret"])
executor = TradeExecutor(kraken, dry_run=config["dry_run"])

# Symboles et paramètres de trading
symbol = config["symbol"]
base_currency = config["base_currency"]
quote_currency = config["quote_currency"]
trade_amount = config["trade_amount"]

# Boucle principale
def main_loop():
    try:
        logger.info("⏳ Récupération des données de marché...")
        price_data = kraken.get_ohlc_data(symbol)
        logger.info("📈 Analyse stratégique en cours...")
        signals = strategy_selector.analyze(price_data, config)

        if signals.get("buy"):
            logger.info("💰 Signal d'achat détecté.")
            executor.buy(symbol, trade_amount)
            send_notification("Signal d'achat exécuté.")

        if signals.get("sell"):
            logger.info("🔻 Signal de vente détecté.")
            executor.sell(symbol, trade_amount)
            send_notification("Signal de vente exécuté.")

    except Exception as e:
        logger.error(f"💥 Erreur dans la boucle principale : {e}")
        send_notification(f"Erreur : {e}")

if __name__ == "__main__":
    logger.info("🚀 Démarrage du XRP Grid Trading Bot")
    while True:
        main_loop()
        time.sleep(60)  # Attente de 1 minute avant la prochaine itération
