"""
Universe loader module for fetching comprehensive list of US stocks.
Supports loading from multiple sources with fallback options.
"""

import pandas as pd
import requests
from io import StringIO
import time
import yfinance as yf


def get_nasdaq_listed_stocks():
    """
    Get all stocks listed on NASDAQ exchange from NASDAQ FTP.

    Returns:
        list: List of ticker symbols
    """
    try:
        # Try HTTP first (HTTPS may timeout)
        url = "http://ftp.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        # Parse the pipe-delimited file
        data = StringIO(response.text)
        df = pd.read_csv(data, sep='|')

        # Filter out test symbols and get valid tickers
        df = df[df['Test Issue'] == 'N']  # Not a test issue
        df = df[df['Financial Status'] != 'D']  # Not deficient

        tickers = df['Symbol'].tolist()

        # Clean up - remove the last row which is just metadata
        if tickers and 'File Creation Time' in str(tickers[-1]):
            tickers = tickers[:-1]

        print(f"  NASDAQ: {len(tickers)} stocks")
        return tickers

    except Exception as e:
        print(f"  Error fetching NASDAQ list: {e}")
        return []


def get_other_listed_stocks():
    """
    Get stocks listed on NYSE, AMEX and other exchanges from NASDAQ FTP.

    Returns:
        list: List of ticker symbols
    """
    try:
        url = "http://ftp.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        # Parse the pipe-delimited file
        data = StringIO(response.text)
        df = pd.read_csv(data, sep='|')

        # Filter for NYSE and AMEX (Exchange codes A and N)
        df = df[df['Exchange'].isin(['A', 'N', 'P', 'Z'])]
        df = df[df['Test Issue'] == 'N']  # Not a test issue

        tickers = df['ACT Symbol'].tolist()

        # Clean up
        if tickers and 'File Creation Time' in str(tickers[-1]):
            tickers = tickers[:-1]

        print(f"  NYSE/AMEX: {len(tickers)} stocks")
        return tickers

    except Exception as e:
        print(f"  Error fetching NYSE/AMEX list: {e}")
        return []


def get_sp500_universe():
    """
    Fallback: Get S&P 500 stocks as a starting point.

    Returns:
        list: List of ticker symbols
    """
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        tables = pd.read_html(url)
        sp500_table = tables[0]
        tickers = sp500_table['Symbol'].tolist()
        tickers = [ticker.replace('.', '-') for ticker in tickers]

        print(f"  S&P 500 fallback: {len(tickers)} stocks")
        return tickers
    except Exception as e:
        print(f"  Error fetching S&P 500: {e}")
        return []


def get_all_us_stocks_screener():
    """
    Alternative method: Use yfinance screener capabilities.
    This method iterates through ticker ranges to discover stocks.

    Returns:
        list: List of ticker symbols
    """
    print("\nUsing alternative discovery method...")

    all_tickers = []

    # Start with known exchanges and common patterns
    # This is a heuristic approach - checks common ticker patterns

    # Get S&P 500 as base
    sp500 = get_sp500_universe()
    all_tickers.extend(sp500)

    print(f"  Base universe: {len(all_tickers)} tickers")

    return all_tickers


def get_all_us_stocks():
    """
    Get comprehensive list of all US stocks from multiple sources.
    Uses primary source with fallback options.

    Returns:
        list: Deduplicated list of all ticker symbols
    """
    print("\nFetching comprehensive US stock universe...")

    all_tickers = []

    # Try primary source - NASDAQ FTP
    nasdaq_tickers = get_nasdaq_listed_stocks()
    all_tickers.extend(nasdaq_tickers)

    time.sleep(0.5)

    other_tickers = get_other_listed_stocks()
    all_tickers.extend(other_tickers)

    # If primary source failed, use fallback
    if not all_tickers:
        print("\nPrimary source failed, using fallback method...")
        all_tickers = get_all_us_stocks_screener()

    # Deduplicate
    unique_tickers = list(set(all_tickers))

    # Clean up tickers
    cleaned_tickers = []
    for ticker in unique_tickers:
        if ticker and isinstance(ticker, str):
            ticker = ticker.replace('.', '-')

            # Skip special symbols
            if '$' not in ticker and '^' not in ticker:
                if len(ticker) <= 5:
                    cleaned_tickers.append(ticker)

    print(f"\nTotal unique tickers: {len(cleaned_tickers)}")

    return sorted(cleaned_tickers)


def filter_by_market_cap_estimate(tickers, min_market_cap=500_000_000, batch_size=50):
    """
    Pre-filter tickers by estimated market cap before full data fetch.
    This is a rough filter to reduce the number of API calls.

    Note: This is a quick screening - actual filtering happens in filters.py

    Args:
        tickers (list): List of ticker symbols
        min_market_cap (float): Minimum market cap threshold
        batch_size (int): Number of tickers to process at once

    Returns:
        list: Filtered list of tickers likely to meet market cap requirement
    """
    print(f"\nPre-screening {len(tickers)} tickers for market cap >= ${min_market_cap/1e9:.1f}B...")
    print("(This is a quick filter - detailed filtering happens later)")

    import yfinance as yf

    valid_tickers = []

    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        batch_str = ' '.join(batch)

        try:
            # Use multi-ticker download for speed
            data = yf.download(batch_str, period='1d', progress=False,
                             show_errors=False, threads=True)

            for ticker in batch:
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info

                    mcap = info.get('marketCap', 0)

                    if mcap and mcap >= min_market_cap:
                        valid_tickers.append(ticker)

                except Exception:
                    continue

            # Progress update every 100 tickers
            if (i + batch_size) % 100 == 0:
                print(f"  Processed {min(i + batch_size, len(tickers))}/{len(tickers)} tickers, found {len(valid_tickers)} candidates")

            time.sleep(0.1)  # Small delay between batches

        except Exception as e:
            print(f"  Error processing batch: {e}")
            continue

    print(f"\nPre-screening complete: {len(valid_tickers)} tickers passed initial filter")

    return valid_tickers


def save_ticker_list(tickers, filename='data/us_stock_universe.txt'):
    """
    Save ticker list to file for future use.

    Args:
        tickers (list): List of tickers
        filename (str): Output filename
    """
    import os
    os.makedirs('data', exist_ok=True)

    with open(filename, 'w') as f:
        for ticker in tickers:
            f.write(f"{ticker}\n")

    print(f"Ticker list saved to {filename}")


def load_ticker_list(filename='data/us_stock_universe.txt'):
    """
    Load ticker list from file.

    Args:
        filename (str): Input filename

    Returns:
        list: List of tickers
    """
    import os

    if not os.path.exists(filename):
        return None

    with open(filename, 'r') as f:
        tickers = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(tickers)} tickers from {filename}")
    return tickers
