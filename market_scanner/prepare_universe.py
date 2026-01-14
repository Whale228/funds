"""
Utility script to prepare the ticker universe.
Run this first to download and cache the list of all US stocks.
This is a one-time operation that takes ~1 minute.
"""

from universe_loader import (
    get_all_us_stocks,
    save_ticker_list,
    load_ticker_list
)
import os


def main():
    print("=" * 80)
    print("TICKER UNIVERSE PREPARATION")
    print("=" * 80)
    print("\nThis script will download the list of all stocks from US exchanges")
    print("(NASDAQ, NYSE, AMEX) and save it for future use.\n")

    cache_file = 'data/us_stock_universe.txt'

    # Check if we already have a cached list
    if os.path.exists(cache_file):
        print(f"Found existing ticker list: {cache_file}")
        existing = load_ticker_list(cache_file)

        response = input(f"\nRefresh ticker list? (y/n): ").lower()
        if response != 'y':
            print(f"\nUsing existing list of {len(existing)} tickers.")
            return

    # Fetch fresh list
    print("\nFetching ticker list from exchanges...")
    tickers = get_all_us_stocks()

    if not tickers:
        print("ERROR: Failed to fetch ticker list")
        return

    # Save to file
    save_ticker_list(tickers, cache_file)

    print("\n" + "=" * 80)
    print("TICKER LIST READY")
    print("=" * 80)
    print(f"Total tickers: {len(tickers)}")
    print(f"Saved to: {cache_file}")
    print("\nYou can now run: python3 main_full.py")
    print("=" * 80)


if __name__ == "__main__":
    main()
