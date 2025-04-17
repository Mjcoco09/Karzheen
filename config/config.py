from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = BASE_DIR / 'logs'

# Create necessary directories
for directory in [DATA_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# Trading Configuration
TRADING_CONFIG = {
    'RISK_PERCENTAGE': 0.02,  # 2% risk per trade
    'MIN_DELAY': 120,         # 2 minutes minimum delay
    'MAX_DELAY': 300,         # 5 minutes maximum delay
    'DEFAULT_ASSET': 'EURUSD',  # Default trading asset
    'DEFAULT_TIMEFRAME': '1m',  # Default timeframe
}

# Strategy Configuration
STRATEGY_CONFIG = {
    'SMA_PERIOD': 20,
    'RSI_PERIOD': 14,
    'RSI_OVERBOUGHT': 70,
    'RSI_OVERSOLD': 30,
}

# Telegram Configuration
TELEGRAM_CONFIG = {
    'ADMIN_USER_IDS': [],  # Add admin Telegram user IDs here
    'UPDATE_INTERVAL': 60,  # Seconds between updates
}

# Selenium Configuration
SELENIUM_CONFIG = {
    'HEADLESS': True,
    'TIMEOUT': 30,  # seconds
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
} 