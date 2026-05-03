"""
Configuration Module
Central configuration for ALFA bot
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """ALFA Bot Configuration"""
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    # Web3 / Blockchain
    WEB3_PROVIDER_URL = os.getenv("WEB3_PROVIDER_URL", "https://mainnet.base.org")
    ALFA_CONTRACT_ADDRESS = os.getenv("ALFA_CONTRACT_ADDRESS")
    CONTRACT_ABI_PATH = os.getenv("CONTRACT_ABI_PATH", "abi/ALFA_Contract_ABI.json")
    SIGNER_PRIVATE_KEY = os.getenv("SIGNER_PRIVATE_KEY")
    
    # Google Drive (for encrypted file storage)
    GOOGLE_DRIVE_CREDENTIALS = os.getenv("GOOGLE_DRIVE_CREDENTIALS_PATH")
    GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    
    # File Processing
    MAX_FILE_SIZE_GB = 2
    UPLOAD_TEMP_DIR = "/tmp/alfa_uploads"
    SUPPORTED_FORMATS = ['.mp4', '.mkv', '.mov', '.webm', '.avi', '.flv', '.wmv']
    
    # Encryption
    ENCRYPTION_ALGORITHM = "AES256-CBC"
    HASH_ALGORITHMS = ["SHA256", "SHA384", "SHA512"]
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR = "logs"
    
    # API Keys / External Services
    GAME_API_KEY = os.getenv("GAME_API_KEY")  # For game database queries
    
    @classmethod
    def validate(cls) -> bool:
        """Validate all required configuration"""
        required = [
            "TELEGRAM_BOT_TOKEN",
            "WEB3_PROVIDER_URL",
            "ALFA_CONTRACT_ADDRESS",
            "SIGNER_PRIVATE_KEY",
        ]
        
        missing = []
        for key in required:
            if not getattr(cls, key, None):
                missing.append(key)
        
        if missing:
            raise ValueError(f"Missing required config: {', '.join(missing)}")
        
        return True


# Create directories if needed
os.makedirs(Config.UPLOAD_TEMP_DIR, exist_ok=True)
os.makedirs(Config.LOG_DIR, exist_ok=True)
