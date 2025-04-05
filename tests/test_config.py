"""Test module for config.py settings management."""

import os
import pytest
from unittest.mock import patch
from app.config import Settings, settings

class TestConfig:
    """Test suite for application configuration."""
    
    def test_required_auth_credentials(self):
        """Test that auth credentials are required."""
        # Test will fail if the .env file is missing required credentials
        assert settings.AUTH_USERNAME is not None
        assert settings.AUTH_PASSWORD is not None
        assert isinstance(settings.AUTH_USERNAME, str)
        assert isinstance(settings.AUTH_PASSWORD, str)
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        assert settings.SMTP_PORT == 2525  # Default Mailtrap port
        assert settings.DEBUG is True
        assert settings.LOGO_DIR == "logos"
    
    def test_logo_dir_creation(self):
        """Test that logo directory is created if it doesn't exist."""
        assert os.path.exists(settings.LOGO_DIR)
        assert os.path.isdir(settings.LOGO_DIR)
    
    @patch.dict('os.environ', {
        'AUTH_USERNAME': 'admin',
        'AUTH_PASSWORD': 'password123',
        'SMTP_PORT': '2525',
        'DEBUG': 'True',
        'LOGO_DIR': 'logos'
    })
    def test_environment_overrides(self):
        """Test that environment variables override defaults."""
        test_settings = Settings()
        
        assert test_settings.AUTH_USERNAME == 'admin'
        assert test_settings.AUTH_PASSWORD == 'password123'
        assert test_settings.SMTP_PORT == 2525
        assert test_settings.DEBUG is True
        assert test_settings.LOGO_DIR == 'logos'
    
    