
"""
Configuration settings for SkyHustle Bot
"""
import os
import logging
import base64
import json
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Configuration:
    """Bot configuration class"""
    telegram_token: str
    admin_chat_id: int
    google_credentials: dict
    spreadsheet_id: str

    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        token = os.getenv("TELEGRAM_TOKEN")
        if not token:
            raise ValueError("No TELEGRAM_TOKEN found in environment variables!")
        
        admin_id_str = os.getenv("ADMIN_CHAT_ID", "0")
        try:
            admin_id = int(admin_id_str)
        except ValueError:
            logger.warning("Invalid ADMIN_CHAT_ID, defaulting to 0")
            admin_id = 0
            
        # Get base64 encoded credentials
        creds_b64 = os.getenv("GOOGLE_CREDENTIALS_B64")
        if not creds_b64:
            raise ValueError("No GOOGLE_CREDENTIALS_B64 found in environment variables!")
        
        # Decode the credentials
        try:
            creds_json = base64.b64decode(creds_b64).decode('utf-8')
            google_creds = json.loads(creds_json)
        except Exception as e:
            raise ValueError(f"Failed to decode Google credentials: {e}")
        
        spreadsheet_id = os.getenv("SPREADSHEET_ID")
        if not spreadsheet_id:
            raise ValueError("No SPREADSHEET_ID found in environment variables!")
            
        return cls(
            telegram_token=token,
            admin_chat_id=admin_id,
            google_credentials=google_creds,
            spreadsheet_id=spreadsheet_id
        )

# Create a global configuration instance
CONFIG = Configuration.from_env()
