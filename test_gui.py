"""
Simple test script to verify GUI components are working correctly.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock tkinter for testing
sys.modules['tkinter'] = Mock()
sys.modules['tkinter.ttk'] = Mock()
sys.modules['pyttsx3'] = Mock()

# Mock Kivy for testing
sys.modules['kivy'] = Mock()
sys.modules['kivy.app'] = Mock()
sys.modules['kivy.uix.screenmanager'] = Mock()
sys.modules['kivy.uix.boxlayout'] = Mock()
sys.modules['kivy.uix.gridlayout'] = Mock()
sys.modules['kivy.uix.label'] = Mock()
sys.modules['kivy.uix.button'] = Mock()
sys.modules['kivy.uix.textinput'] = Mock()
sys.modules['kivy.uix.spinner'] = Mock()
sys.modules['kivy.uix.checkbox'] = Mock()
sys.modules['kivy.uix.scrollview'] = Mock()
sys.modules['kivy.uix.popup'] = Mock()
sys.modules['kivy.metrics'] = Mock()
sys.modules['kivy.properties'] = Mock()

class GUITestCase(unittest.TestCase):
    """Test cases for GUI components."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock Django setup
        with patch('django.setup'):
            with patch('os.environ.setdefault'):
                # Import the desktop app module
                try:
                    import desktop_app
                    self.desktop_app_module = desktop_app
                except ImportError:
                    self.desktop_app_module = None
    
    def test_desktop_app_import(self):
        """Test that the desktop app module can be imported."""
        self.assertIsNotNone(self.desktop_app_module)
    
    def test_screen_manager_creation(self):
        """Test that ScreenManager class exists."""
        if self.desktop_app_module:
            self.assertTrue(hasattr(self.desktop_app_module, 'ScreenManager'))
    
    def test_home_screen_creation(self):
        """Test that HomeScreen class exists."""
        if self.desktop_app_module:
            self.assertTrue(hasattr(self.desktop_app_module, 'HomeScreen'))
    
    def test_feedback_screen_creation(self):
        """Test that FeedbackScreen class exists."""
        if self.desktop_app_module:
            self.assertTrue(hasattr(self.desktop_app_module, 'FeedbackScreen'))
    
    def test_accessibility_settings_screen_creation(self):
        """Test that AccessibilitySettingsScreen class exists."""
        if self.desktop_app_module:
            self.assertTrue(hasattr(self.desktop_app_module, 'AccessibilitySettingsScreen'))


if __name__ == '__main__':
    unittest.main()