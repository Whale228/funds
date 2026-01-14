"""
Configuration file for market scanner application.
Contains filters, thresholds, and parameters for stock analysis.
"""

# Universe filters
MIN_MARKET_CAP = 500_000_000  # $500M minimum market capitalization
MIN_PRICE = 3.0  # Minimum stock price
MIN_AVG_VOLUME = 20_000_000  # Minimum average daily volume in dollars

# Number of top stocks to analyze (by market cap)
TOP_N_STOCKS = 100

# Universe mode: 'top100' or 'full' (all US stocks with market cap >= MIN_MARKET_CAP)
UNIVERSE_MODE = 'full'  # Change to 'full' for 5000+ stocks

# Cache settings
USE_CACHED_UNIVERSE = True  # Use cached ticker list if available
UNIVERSE_CACHE_FILE = 'data/us_stock_universe.txt'

# Strong Trend strategy thresholds
STRONG_TREND_MIN_GAIN = 5.0  # 5% gain per day for 3 consecutive days
STRONG_TREND_3DAY_TOTAL = 15.0  # Or 15% total gain over 3 days

# Panic strategy thresholds
PANIC_1DAY_DROP = 8.0  # 8% drop in one day
PANIC_3DAY_DROP = 15.0  # 15% drop over 3 days
PANIC_VOLUME_MULTIPLIER = 1.5  # Volume must be 1.5x average

# Euphoria strategy thresholds
EUPHORIA_1DAY_GAIN = 8.0  # 8% gain in one day
EUPHORIA_5DAY_GAIN = 20.0  # 20% gain over 5 days

# Market settings
TIMEZONE = 'America/New_York'  # NYSE timezone
HISTORY_DAYS = 30  # Days of historical data to fetch
AVG_VOLUME_DAYS = 20  # Days for calculating average volume

# API settings
REQUEST_DELAY = 0.5  # Delay between API requests in seconds
