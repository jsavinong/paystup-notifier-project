"""Configuration Manager for Paystub Notification System

Handles all environment configuration with validation and default values.
Loads settings from .env file and provides centralized access to application settings.

Environment Variables:
    Required:
    - AUTH_USERNAME: Basic auth username for API access
    - AUTH_PASSWORD: Basic auth password for API access
    
    Optional:
    - SMTP_*: Email server configuration (defaults to Mailtrap test server)
    - DEBUG: Enable debug mode (default: False)
    - FROM_EMAIL: Sender email address for paystubs

Raises:
    ValueError: If required auth credentials are missing
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Settings:
    """Centralized application settings with validation and defaults.
    
    Attributes:
        AUTH_USERNAME (str): API authentication username
        AUTH_PASSWORD (str): API authentication password
        SMTP_SERVER (Optional[str]): SMTP server hostname
        SMTP_PORT (int): SMTP server port (default: 2525)
        SMTP_USERNAME (Optional[str]): SMTP auth username
        SMTP_PASSWORD (Optional[str]): SMTP auth password
        FROM_EMAIL (Optional[str]): Sender email address
        DEBUG (bool): Debug mode flag (default: False)
        LOGO_DIR (str): Path to company logos directory (default: 'logos')
    """
    
    # Authentication
    AUTH_USERNAME: Optional[str] = os.getenv("AUTH_USERNAME")
    AUTH_PASSWORD: Optional[str] = os.getenv("AUTH_PASSWORD")
    
    # Email Configuration
    SMTP_SERVER: Optional[str] = os.getenv("SMTP_SERVER")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "2525"))  # Default Mailtrap port
    SMTP_USERNAME: Optional[str] = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    FROM_EMAIL: Optional[str] = os.getenv("FROM_EMAIL")

    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    LOGO_DIR: str = os.getenv("LOGO_DIR", "logos")

    def __init__(self):
        """Initialize and ensure Docker-compatible paths exist."""
        
        os.makedirs(self.LOGO_DIR, exist_ok=True)


# Validate critical settings
if not all([Settings.AUTH_USERNAME, Settings.AUTH_PASSWORD]):
    raise ValueError("Missing auth credentials in .env!")

# Initialize settings
settings = Settings()