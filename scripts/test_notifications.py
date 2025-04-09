#!/bin/bash
# Script de test des notifications Pushover pour le Bot de Trading XRP v3.0

# Vérification que le fichier de configuration existe
CONFIG_FILE="../config/notification_config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Erreur: Fichier de configuration des notifications non trouvé: $CONFIG_FILE"
    echo "Veuillez copier notification_config.json.example vers notification_config.json et configurer vos identifiants Pushover."
    exit 1
fi

# Vérification de Python
if ! command -v python3 &> /dev/null; then
    echo "Erreur: Python 3 n'est pas installé ou n'est pas dans le PATH."
    exit 1
fi

# Création d'un script Python temporaire pour tester les notifications
TEMP_SCRIPT=$(mktemp)
cat > "$TEMP_SCRIPT" << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import requests
import time
from datetime import datetime

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

try:
    from src.notification_manager import NotificationManager
except ImportError:
    print("Erreur: Impossible d'importer NotificationManager. Vérifiez que le module est correctement installé.")
    sys.exit(1)

def test_notifications():
    """Teste les différents niveaux de notification Pushover."""
    print("Test des notifications Pushover pour le Bot de Trading XRP v3.0")
    print("=" * 60)
    
    # Charger la configuration
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'notification_config.json')
    if not os.path.exists(config_path):
        print(f"Erreur: Fichier de configuration non trouvé: {config_path}")
        return False
    
    try:
        # Initialiser le gestionnaire de notifications
        notification_manager = NotificationManager(config_path=config_path)
        print("Gestionnaire de notifications initialisé avec succès.")
        
        # Vérifier si Pushover est activé
        if not notification_manager.is_pushover_enabled():
            print("Erreur: Pushover n'est pas activé dans la configuration.")
            print("Veuillez activer Pushover et configurer vos identifiants.")
            return False
        
        # Tester la notification de statut
        print("\nTest 1/5: Notification de statut...")
        notification_manager.send_notification(
            title="Test de notification",
            message=f"Ceci est un test de notification de statut. Heure: {datetime.now().strftime('%H:%M:%S')}",
            level="status"
        )
        time.sleep(2)
        
        # Tester la notification de trade
        print("Test 2/5: Notification de trade...")
        notification_manager.send_trade_notification(
            trade_type="buy",
            volume=100.0,
            price=0.5123,
            total=51.23
        )
        time.sleep(2)
        
        # Tester la notification de rapport journalier
        print("Test 3/5: Notification de rapport journalier...")
        notification_manager.send_daily_report_notification({
            "trades_executed": 12,
            "profit_loss": "+2.34%",
            "current_balance": "123.45 GBP",
            "open_orders": 8
        })
        time.sleep(2)
        
        # Tester la notification d'efficacité
        print("Test 4/5: Notification d'efficacité...")
        notification_manager.send_efficiency_notification({
            "cpu_usage": 12.5,
            "memory_usage": 45.2,
            "api_calls": 87,
            "response_time": 0.23,
            "execution_time": 1.45,
            "additional_metrics": "Tout fonctionne normalement"
        })
        time.sleep(2)
        
        # Tester la notification d'erreur
        print("Test 5/5: Notification d'erreur...")
        notification_manager.send_error_notification(
            error_type="test_error",
            error_message="Ceci est un test de notification d'erreur",
            severity="medium"
        )
        
        print("\nTous les tests de notification ont été envoyés.")
        print("Veuillez vérifier votre appareil Pushover pour confirmer la réception des notifications.")
        return True
        
    except Exception as e:
        print(f"Erreur lors du test des notifications: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_notifications()
    sys.exit(0 if success else 1)
EOF

# Rendre le script exécutable
chmod +x "$TEMP_SCRIPT"

# Exécuter le script de test
echo "Exécution du test des notifications Pushover..."
python3 "$TEMP_SCRIPT"
TEST_RESULT=$?

# Supprimer le script temporaire
rm "$TEMP_SCRIPT"

# Afficher le résultat
if [ $TEST_RESULT -eq 0 ]; then
    echo "Test des notifications terminé avec succès."
    echo "Veuillez vérifier votre appareil Pushover pour confirmer la réception des notifications."
else
    echo "Le test des notifications a échoué."
    echo "Veuillez vérifier votre configuration Pushover et réessayer."
fi

exit $TEST_RESULT
