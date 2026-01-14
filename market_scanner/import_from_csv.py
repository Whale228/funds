"""
Import ticker universe from CSV file.
Useful for importing screener results from sites like:
- FinViz.com
- TradingView
- Yahoo Finance Screener
- Or any custom CSV with a 'Ticker' or 'Symbol' column
"""

import pandas as pd
import sys
import os


def import_from_csv(csv_file, ticker_column='Ticker'):
    """
    Import tickers from a CSV file.

    Args:
        csv_file (str): Path to CSV file
        ticker_column (str): Name of the column containing tickers

    Returns:
        list: List of ticker symbols
    """
    try:
        # Try different encodings
        for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
            try:
                df = pd.read_csv(csv_file, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            print(f"ERROR: Could not decode {csv_file}")
            return []

        # Find ticker column (case-insensitive)
        ticker_col = None
        for col in df.columns:
            if col.lower() in ['ticker', 'symbol', 'tickers', 'symbols', 'stock']:
                ticker_col = col
                break

        if not ticker_col:
            print(f"\nAvailable columns: {list(df.columns)}")
            ticker_col = input("\nEnter column name containing tickers: ")

        if ticker_col not in df.columns:
            print(f"ERROR: Column '{ticker_col}' not found in CSV")
            return []

        # Extract tickers
        tickers = df[ticker_col].dropna().astype(str).tolist()

        # Clean up tickers
        cleaned_tickers = []
        for ticker in tickers:
            ticker = ticker.strip().upper()
            # Replace dots with dashes for Yahoo Finance
            ticker = ticker.replace('.', '-')

            # Skip empty or invalid tickers
            if ticker and len(ticker) <= 5 and ticker.isalpha() or '-' in ticker:
                # Skip special symbols
                if '$' not in ticker and '^' not in ticker:
                    cleaned_tickers.append(ticker)

        # Remove duplicates
        unique_tickers = sorted(list(set(cleaned_tickers)))

        print(f"\nImported {len(unique_tickers)} unique tickers from {csv_file}")
        print(f"Sample: {unique_tickers[:10]}")

        return unique_tickers

    except Exception as e:
        print(f"ERROR importing CSV: {e}")
        return []


def save_tickers(tickers, filename='data/us_stock_universe.txt'):
    """Save ticker list to file."""
    os.makedirs('data', exist_ok=True)

    with open(filename, 'w') as f:
        for ticker in tickers:
            f.write(f"{ticker}\n")

    print(f"\nSaved {len(tickers)} tickers to {filename}")


def main():
    print("=" * 80)
    print("CSV TICKER IMPORT")
    print("=" * 80)

    if len(sys.argv) < 2:
        print("\nUsage: python3 import_from_csv.py <path_to_csv>")
        print("\nExample:")
        print("  python3 import_from_csv.py data/finviz_export.csv")
        print("\nTo get a CSV with 5000+ US stocks:")
        print("  1. Go to finviz.com/screener.ashx")
        print("  2. Set filters: Market Cap > 500M, Country = USA")
        print("  3. Click 'Export' to download CSV")
        print("  4. Run this script with the downloaded file")
        return

    csv_file = sys.argv[1]

    if not os.path.exists(csv_file):
        print(f"\nERROR: File not found: {csv_file}")
        return

    print(f"\nImporting from: {csv_file}")

    tickers = import_from_csv(csv_file)

    if not tickers:
        print("\nNo tickers imported. Check CSV format.")
        return

    # Ask to merge with existing
    existing_file = 'data/us_stock_universe.txt'
    if os.path.exists(existing_file):
        response = input(f"\nMerge with existing {existing_file}? (y/n): ").lower()
        if response == 'y':
            with open(existing_file, 'r') as f:
                existing = [line.strip() for line in f if line.strip()]
            tickers = sorted(list(set(tickers + existing)))
            print(f"Merged with {len(existing)} existing tickers")

    save_tickers(tickers)

    print("\n" + "=" * 80)
    print("IMPORT COMPLETE")
    print("=" * 80)
    print(f"Total tickers in universe: {len(tickers)}")
    print("\nYou can now run: python3 main_full.py")
    print("=" * 80)


if __name__ == "__main__":
    main()
