"""
Data loader module for fetching stock data from Yahoo Finance.
Handles ticker list retrieval and stock data fetching with error handling.
"""

import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta
import config


def get_sp500_tickers():
    """
    Get list of S&P 500 ticker symbols from Wikipedia.
    Falls back to a predefined top 100 list if Wikipedia fetch fails.

    Returns:
        list: List of ticker symbols
    """
    try:
        # Try to fetch from Wikipedia
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        tables = pd.read_html(url)
        sp500_table = tables[0]
        tickers = sp500_table['Symbol'].tolist()

        # Clean up tickers (remove dots, etc.)
        tickers = [ticker.replace('.', '-') for ticker in tickers]

        print(f"Successfully fetched {len(tickers)} tickers from S&P 500")
        return tickers

    except Exception as e:
        print(f"Error fetching S&P 500 list: {e}")
        print("Using fallback top 100 stocks list")

        # Fallback: predefined list of top stocks by market cap
        return [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B', 'UNH', 'XOM',
            'JNJ', 'JPM', 'V', 'PG', 'MA', 'HD', 'CVX', 'MRK', 'ABBV', 'PEP',
            'KO', 'AVGO', 'COST', 'PFE', 'WMT', 'TMO', 'MCD', 'CSCO', 'ACN', 'DHR',
            'ADBE', 'ABT', 'NKE', 'TXN', 'NEE', 'CRM', 'LIN', 'PM', 'DIS', 'ORCL',
            'VZ', 'WFC', 'CMCSA', 'BMY', 'AMD', 'INTC', 'RTX', 'UPS', 'QCOM', 'HON',
            'AMGN', 'BA', 'INTU', 'CAT', 'AMAT', 'GE', 'IBM', 'LOW', 'SPGI', 'SBUX',
            'BLK', 'DE', 'GILD', 'ELV', 'ADP', 'LMT', 'BKNG', 'PLD', 'MDLZ', 'ADI',
            'ISRG', 'CI', 'TJX', 'MMC', 'VRTX', 'SYK', 'C', 'REGN', 'ZTS', 'MO',
            'NOW', 'CB', 'SO', 'PGR', 'DUK', 'ETN', 'BSX', 'BDX', 'CME', 'ITW',
            'EOG', 'APD', 'USB', 'CL', 'HUM', 'MMM', 'GD', 'AON', 'TGT', 'SLB'
        ]


def get_top_tickers(n=100):
    """
    Get top N tickers from S&P 500.

    Args:
        n (int): Number of tickers to return

    Returns:
        list: List of top N ticker symbols
    """
    all_tickers = get_sp500_tickers()
    return all_tickers[:n]


def fetch_stock_data(ticker):
    """
    Fetch comprehensive stock data for a given ticker.

    Args:
        ticker (str): Stock ticker symbol

    Returns:
        dict: Dictionary containing stock data with keys:
            - ticker: Stock symbol
            - current_price: Current stock price
            - previous_close: Previous day's closing price
            - market_cap: Market capitalization
            - avg_volume_20d: 20-day average volume
            - price_history: DataFrame with OHLCV data for 30 days
            - volume_history: List of daily volumes
            Returns None if data fetch fails
    """
    try:
        # Create ticker object
        stock = yf.Ticker(ticker)

        # Fetch historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=config.HISTORY_DAYS)

        hist = stock.history(start=start_date, end=end_date)

        # Check if we have sufficient data
        if hist.empty or len(hist) < 5:
            print(f"  {ticker}: Insufficient historical data")
            return None

        # Get current info
        info = stock.info

        # Extract required fields with fallbacks
        current_price = hist['Close'].iloc[-1] if len(hist) > 0 else None
        previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else None

        # Market cap with fallback
        market_cap = info.get('marketCap', None)
        if market_cap is None:
            # Try to calculate from shares outstanding
            shares = info.get('sharesOutstanding', None)
            if shares and current_price:
                market_cap = shares * current_price

        # Calculate average volume over last 20 days
        if len(hist) >= config.AVG_VOLUME_DAYS:
            avg_volume_20d = hist['Volume'].tail(config.AVG_VOLUME_DAYS).mean()
        else:
            avg_volume_20d = hist['Volume'].mean()

        # Validate required data
        if current_price is None or market_cap is None:
            print(f"  {ticker}: Missing critical data (price or market cap)")
            return None

        # Build result dictionary
        stock_data = {
            'ticker': ticker,
            'current_price': float(current_price),
            'previous_close': float(previous_close) if previous_close else float(current_price),
            'market_cap': float(market_cap),
            'avg_volume_20d': float(avg_volume_20d),
            'price_history': hist[['Open', 'High', 'Low', 'Close', 'Volume']].copy(),
            'volume_history': hist['Volume'].tolist()
        }

        return stock_data

    except Exception as e:
        print(f"  {ticker}: Error fetching data - {str(e)}")
        return None


def load_stocks_data(tickers, delay=None):
    """
    Load stock data for multiple tickers with progress tracking.

    Args:
        tickers (list): List of ticker symbols
        delay (float): Delay between requests in seconds (uses config default if None)

    Returns:
        list: List of stock data dictionaries (excludes failed fetches)
    """
    if delay is None:
        delay = config.REQUEST_DELAY

    all_data = []
    total = len(tickers)

    print(f"\nFetching data for {total} tickers...")

    for i, ticker in enumerate(tickers, 1):
        print(f"[{i}/{total}] Fetching {ticker}...")

        data = fetch_stock_data(ticker)
        if data:
            all_data.append(data)
            print(f"  {ticker}: Success (${data['current_price']:.2f}, MCap: ${data['market_cap']/1e9:.1f}B)")

        # Rate limiting
        if i < total:
            time.sleep(delay)

    print(f"\nSuccessfully loaded {len(all_data)}/{total} stocks")
    return all_data
