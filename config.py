"""Application configuration. Loads .env via python-dotenv."""
import os
from dotenv import load_dotenv

load_dotenv()

# Alpha Vantage
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"

# Database
DB_PATH = os.getenv("DB_PATH", "data/dashboard.db")

# Cache TTLs (seconds)
QUOTE_CACHE_TTL = int(os.getenv("QUOTE_CACHE_TTL", "60"))
HISTORICAL_CACHE_TTL = int(os.getenv("HISTORICAL_CACHE_TTL", "3600"))

# Timeframe presets — maps label to (yfinance period, yfinance interval)
TIMEFRAMES = {
    "1D": ("1d", "5m"),
    "5D": ("5d", "15m"),
    "1M": ("1mo", "1h"),
    "3M": ("3mo", "1d"),
    "6M": ("6mo", "1d"),
    "1Y": ("1y", "1d"),
    "5Y": ("5y", "1wk"),
    "MAX": ("max", "1mo"),
}
