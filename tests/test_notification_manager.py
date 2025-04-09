#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for the Notification Manager module
"""

import os
import json
import unittest
from unittest.mock import patch, MagicMock
import sys
sys.path.append('../src')
from notification_manager import NotificationManager, PushoverNotifier, ConsoleNotifier

class TestNotificationManager(unittest.TestCase):
    """Test cases for the NotificationManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_config = {
            "pushover": {
                "enabled": True,
                "user_key": "test_user_key",
                "app_token": "test_app_token",
                "device": "test_device",
                "sound": "test_sound",
                "priority": 0
            },
            "high_priority_trades": True
        }
    
    def test_initialization_with_config_dict(self):
        """Test initialization with a config dictionary"""
        manager = NotificationManager(config=self.test_config)
        self.assertIn('pushover', manager.notifiers)
        self.assertIn('console', manager.notifiers)
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='{"pushover": {"enabled": true, "user_key": "file_user_key", "app_token": "file_app_token"}}')
    def test_initialization_with_config_file(self, mock_open, mock_exists):
        """Test initialization with a config file"""
        mock_exists.return_value = True
        manager = NotificationManager(config_path='fake_path.json')
        self.assertIn('pushover', manager.notifiers)
        self.assertIn('console', manager.notifiers)
    
    def test_send_notification_all_notifiers(self):
        """Test sending a notification through all notifiers"""
        manager = NotificationManager(config=self.test_config)
        
        # Mock the send methods
        for notifier_type, notifier in manager.notifiers.items():
            notifier.send = MagicMock(return_value={"success": True})
        
        result = manager.send_notification("Test Title", "Test Message")
        
        # Verify all notifiers were called
        for notifier_type, notifier in manager.notifiers.items():
            notifier.send.assert_called_once()
            self.assertIn(notifier_type, result)
    
    def test_send_notification_specific_notifiers(self):
        """Test sending a notification through specific notifiers"""
        manager = NotificationManager(config=self.test_config)
        
        # Mock the send methods
        for notifier_type, notifier in manager.notifiers.items():
            notifier.send = MagicMock(return_value={"success": True})
        
        result = manager.send_notification("Test Title", "Test Message", notifier_types=['console'])
        
        # Verify only console notifier was called
        manager.notifiers['console'].send.assert_called_once()
        if 'pushover' in manager.notifiers:
            manager.notifiers['pushover'].send.assert_not_called()
    
    def test_send_trade_notification(self):
        """Test sending a trade notification"""
        manager = NotificationManager(config=self.test_config)
        manager.send_notification = MagicMock(return_value={"success": True})
        
        result = manager.send_trade_notification("buy", 100.0, 0.5, 50.0)
        
        # Verify send_notification was called with correct parameters
        manager.send_notification.assert_called_once()
        args, kwargs = manager.send_notification.call_args
        self.assertEqual(args[0], "XRP BUY EXECUTED")
        self.assertIn("100.0", args[1])
        self.assertIn("0.5", args[1])
        self.assertEqual(kwargs.get('priority'), 1)  # High priority for trades
    
    def test_send_error_notification(self):
        """Test sending an error notification"""
        manager = NotificationManager(config=self.test_config)
        manager.send_notification = MagicMock(return_value={"success": True})
        
        result = manager.send_error_notification("API Error", "Failed to connect", "Timeout")
        
        # Verify send_notification was called with correct parameters
        manager.send_notification.assert_called_once()
        args, kwargs = manager.send_notification.call_args
        self.assertEqual(args[0], "XRP Bot Error: API Error")
        self.assertIn("Failed to connect", args[1])
        self.assertIn("Timeout", args[1])
        self.assertEqual(kwargs.get('priority'), 1)  # High priority for errors


class TestPushoverNotifier(unittest.TestCase):
    """Test cases for the PushoverNotifier class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.notifier = PushoverNotifier(
            user_key="test_user_key",
            app_token="test_app_token",
            device="test_device",
            sound="test_sound",
            priority=0
        )
    
    @patch('requests.post')
    def test_send_success(self, mock_post):
        """Test successful notification sending"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": 1}
        mock_post.return_value = mock_response
        
        result = self.notifier.send("Test Title", "Test Message")
        
        # Verify request was made with correct parameters
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://api.pushover.net/1/messages.json")
        self.assertEqual(kwargs['data']['token'], "test_app_token")
        self.assertEqual(kwargs['data']['user'], "test_user_key")
        self.assertEqual(kwargs['data']['title'], "Test Title")
        self.assertEqual(kwargs['data']['message'], "Test Message")
        self.assertEqual(kwargs['data']['device'], "test_device")
        self.assertEqual(kwargs['data']['sound'], "test_sound")
        
        # Verify result
        self.assertTrue(result['success'])
    
    @patch('requests.post')
    def test_send_failure(self, mock_post):
        """Test failed notification sending"""
        # Mock failed response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Invalid token"
        mock_post.return_value = mock_response
        
        result = self.notifier.send("Test Title", "Test Message")
        
        # Verify request was made
        mock_post.assert_called_once()
        
        # Verify result
        self.assertFalse(result['success'])
        self.assertIn("HTTP 400", result['error'])
    
    def test_missing_credentials(self):
        """Test behavior with missing credentials"""
        notifier = PushoverNotifier(user_key="", app_token="")
        result = notifier.send("Test Title", "Test Message")
        
        # Verify result
        self.assertFalse(result['success'])
        self.assertIn("credentials not configured", result['error'])


class TestConsoleNotifier(unittest.TestCase):
    """Test cases for the ConsoleNotifier class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.notifier = ConsoleNotifier()
    
    @patch('builtins.print')
    def test_send(self, mock_print):
        """Test console notification"""
        result = self.notifier.send(
            "Test Title", 
            "Test Message",
            url="http://example.com",
            attachment="test.jpg"
        )
        
        # Verify print was called
        self.assertTrue(mock_print.called)
        
        # Verify result
        self.assertTrue(result['success'])


if __name__ == '__main__':
    unittest.main()
