import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))

from src.notification_manager import NotificationManager, PushoverNotifier

class TestNotificationManager(unittest.TestCase):
    
    def setUp(self):
        # Créer une configuration de test
        self.test_config = {
            "pushover": {
                "enabled": True,
                "user_key": "test_user_key",
                "app_token": "test_app_token",
                "device": "",
                "sound": "pushover",
                "priority": 0
            },
            "notification_levels": {
                "trade": True,
                "daily_report": True,
                "efficiency": True,
                "error": True,
                "debug": False
            },
            "level_settings": {
                "trade": {
                    "priority": 0,
                    "sound": "cashregister"
                },
                "daily_report": {
                    "priority": -1,
                    "sound": "classical"
                },
                "efficiency": {
                    "priority": -1,
                    "sound": "mechanical"
                },
                "error": {
                    "priority": 1,
                    "sound": "siren"
                },
                "debug": {
                    "priority": -2,
                    "sound": "none"
                }
            },
            "throttling": {
                "enabled": True,
                "max_notifications_per_hour": {
                    "trade": 20,
                    "daily_report": 2,
                    "efficiency": 4,
                    "error": 10,
                    "debug": 5
                },
                "min_time_between_notifications_seconds": {
                    "trade": 30,
                    "daily_report": 3600,
                    "efficiency": 900,
                    "error": 60,
                    "debug": 300
                }
            }
        }
        
        # Créer un fichier de configuration temporaire
        self.config_path = "/tmp/test_notification_config.json"
        with open(self.config_path, "w") as f:
            json.dump(self.test_config, f)
        
        # Initialiser le gestionnaire de notifications avec le fichier de configuration temporaire
        self.notification_manager = NotificationManager(config_path=self.config_path)
    
    def tearDown(self):
        # Supprimer le fichier de configuration temporaire
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
    
    @patch('src.notification_manager.PushoverNotifier.send_notification')
    def test_send_notification(self, mock_send):
        # Configurer le mock
        mock_send.return_value = True
        
        # Appeler la méthode à tester
        result = self.notification_manager.send_notification(
            title="Test Title",
            message="Test Message",
            level="status"
        )
        
        # Vérifier que la méthode a été appelée avec les bons arguments
        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        self.assertEqual(kwargs["title"], "Test Title")
        self.assertEqual(kwargs["message"], "Test Message")
        self.assertTrue(result)
    
    @patch('src.notification_manager.PushoverNotifier.send_notification')
    def test_send_trade_notification(self, mock_send):
        # Configurer le mock
        mock_send.return_value = True
        
        # Appeler la méthode à tester
        result = self.notification_manager.send_trade_notification(
            trade_type="buy",
            volume=100.0,
            price=0.5,
            total=50.0
        )
        
        # Vérifier que la méthode a été appelée avec les bons arguments
        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        self.assertIn("Achat", kwargs["title"])
        self.assertIn("100.0", kwargs["message"])
        self.assertIn("0.5", kwargs["message"])
        self.assertEqual(kwargs["sound"], "cashregister")
        self.assertTrue(result)
    
    @patch('src.notification_manager.PushoverNotifier.send_notification')
    def test_send_daily_report_notification(self, mock_send):
        # Configurer le mock
        mock_send.return_value = True
        
        # Appeler la méthode à tester
        result = self.notification_manager.send_daily_report_notification({
            "trades_executed": 10,
            "profit_loss": "+5.2%",
            "current_balance": "1000 XRP",
            "open_orders": 5
        })
        
        # Vérifier que la méthode a été appelée avec les bons arguments
        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        self.assertIn("Rapport", kwargs["title"])
        self.assertIn("10", kwargs["message"])
        self.assertIn("+5.2%", kwargs["message"])
        self.assertEqual(kwargs["sound"], "classical")
        self.assertTrue(result)
    
    @patch('src.notification_manager.PushoverNotifier.send_notification')
    def test_send_efficiency_notification(self, mock_send):
        # Configurer le mock
        mock_send.return_value = True
        
        # Appeler la méthode à tester
        result = self.notification_manager.send_efficiency_notification({
            "cpu_usage": 10.5,
            "memory_usage": 25.3,
            "api_calls": 100,
            "response_time": 0.2,
            "execution_time": 1.5
        })
        
        # Vérifier que la méthode a été appelée avec les bons arguments
        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        self.assertIn("Efficacité", kwargs["title"])
        self.assertIn("10.5", kwargs["message"])
        self.assertIn("25.3", kwargs["message"])
        self.assertEqual(kwargs["sound"], "mechanical")
        self.assertTrue(result)
    
    @patch('src.notification_manager.PushoverNotifier.send_notification')
    def test_send_error_notification(self, mock_send):
        # Configurer le mock
        mock_send.return_value = True
        
        # Appeler la méthode à tester
        result = self.notification_manager.send_error_notification(
            error_type="test_error",
            error_message="Test Error Message",
            severity="high"
        )
        
        # Vérifier que la méthode a été appelée avec les bons arguments
        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        self.assertIn("ERREUR", kwargs["title"])
        self.assertIn("test_error", kwargs["message"])
        self.assertIn("Test Error Message", kwargs["message"])
        self.assertEqual(kwargs["sound"], "siren")
        self.assertTrue(result)
    
    def test_is_pushover_enabled(self):
        # Vérifier que Pushover est activé
        self.assertTrue(self.notification_manager.is_pushover_enabled())
        
        # Désactiver Pushover
        self.notification_manager.config["pushover"]["enabled"] = False
        
        # Vérifier que Pushover est désactivé
        self.assertFalse(self.notification_manager.is_pushover_enabled())
    
    @patch('src.notification_manager.PushoverNotifier.send_notification')
    def test_throttling(self, mock_send):
        # Configurer le mock
        mock_send.return_value = True
        
        # Appeler la méthode plusieurs fois
        for i in range(5):
            result = self.notification_manager.send_error_notification(
                error_type="test_error",
                error_message=f"Test Error Message {i}",
                severity="high"
            )
            # Les premières notifications devraient réussir
            self.assertTrue(result)
        
        # Modifier le compteur de notifications pour simuler le dépassement de la limite
        self.notification_manager.notification_counts["error"] = 11
        
        # La prochaine notification devrait être limitée
        result = self.notification_manager.send_error_notification(
            error_type="test_error",
            error_message="This should be throttled",
            severity="high"
        )
        
        # Vérifier que la notification a été limitée
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
