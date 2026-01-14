"""
Main entry point for market scanner application.
Orchestrates data loading, filtering, classification, and result presentation.
"""

import json
import os
from datetime import datetime
import pytz

import config
from data_loader import get_top_tickers, load_stocks_data
from filters import filter_universe
from strategies import classify_stock


def print_results(results):
    """
    Print classification results to console in a structured format.

    Args:
        results (dict): Dictionary with 'strong_trend', 'panic', and 'euphoria' keys
    """
    print("\n" + "=" * 80)
    print("MARKET SCANNER RESULTS")
    print("=" * 80)

    # Strong Trend
    strong_trend = results['strong_trend']
    print(f"\n=== STRONG TREND ({len(strong_trend)} stocks) ===")
    if strong_trend:
        for stock in strong_trend:
            print(f"{stock['ticker']:6} | ${stock['price']:8.2f} | "
                  f"{stock['change_1d']:+6.1f}% (1d) | {stock['change_3d']:+6.1f}% (3d) | "
                  f"{stock['reason']}")
    else:
        print("No stocks found")

    # Panic
    panic = results['panic']
    print(f"\n=== PANIC ({len(panic)} stocks) ===")
    if panic:
        for stock in panic:
            print(f"{stock['ticker']:6} | ${stock['price']:8.2f} | "
                  f"{stock['change_1d']:+6.1f}% (1d) | {stock['change_3d']:+6.1f}% (3d) | "
                  f"{stock['reason']}")
    else:
        print("No stocks found")

    # Euphoria
    euphoria = results['euphoria']
    print(f"\n=== EUPHORIA ({len(euphoria)} stocks) ===")
    if euphoria:
        for stock in euphoria:
            print(f"{stock['ticker']:6} | ${stock['price']:8.2f} | "
                  f"{stock['change_1d']:+6.1f}% (1d) | {stock['change_5d']:+6.1f}% (5d) | "
                  f"{stock['reason']}")
    else:
        print("No stocks found")

    print("\n" + "=" * 80)
    total_classified = len(strong_trend) + len(panic) + len(euphoria)
    print(f"Total classified stocks: {total_classified}")
    print("=" * 80 + "\n")


def save_results(results, timestamp):
    """
    Save results to JSON file.

    Args:
        results (dict): Classification results
        timestamp (str): Timestamp string for filename
    """
    # Ensure results directory exists
    os.makedirs('results', exist_ok=True)

    # Create filename with timestamp
    filename = f"results/scan_{timestamp}.json"

    # Prepare data for JSON serialization
    output = {
        'timestamp': timestamp,
        'analysis_date': datetime.now(pytz.timezone(config.TIMEZONE)).isoformat(),
        'config': {
            'min_market_cap': config.MIN_MARKET_CAP,
            'min_price': config.MIN_PRICE,
            'min_avg_volume': config.MIN_AVG_VOLUME,
            'top_n_stocks': config.TOP_N_STOCKS
        },
        'results': results,
        'summary': {
            'strong_trend_count': len(results['strong_trend']),
            'panic_count': len(results['panic']),
            'euphoria_count': len(results['euphoria']),
            'total_classified': (len(results['strong_trend']) +
                               len(results['panic']) +
                               len(results['euphoria']))
        }
    }

    # Save to file
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to {filename}")


def save_cache(all_data, timestamp):
    """
    Save loaded stock data to cache file.

    Args:
        all_data (list): List of stock data dictionaries
        timestamp (str): Timestamp string for filename
    """
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)

    filename = f"data/cache_{timestamp}.json"

    # Prepare data (convert DataFrames to dict)
    cache_data = []
    for stock in all_data:
        stock_copy = stock.copy()
        # Convert DataFrame to dict with string indices
        df = stock['price_history'].copy()
        df.index = df.index.astype(str)  # Convert Timestamp index to strings
        stock_copy['price_history'] = df.to_dict()
        cache_data.append(stock_copy)

    with open(filename, 'w') as f:
        json.dump(cache_data, f, indent=2)

    print(f"Cache saved to {filename}")


def main():
    """
    Main execution function.
    Orchestrates the entire market scanning workflow.
    """
    print("=" * 80)
    print("MARKET SCANNER - Stock Analysis Tool")
    print("=" * 80)
    print(f"Analyzing top {config.TOP_N_STOCKS} US stocks")
    print(f"Timestamp: {datetime.now(pytz.timezone(config.TIMEZONE))}")
    print("=" * 80)

    # Generate timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Step 1: Load ticker list
    print("\nStep 1: Loading ticker list...")
    tickers = get_top_tickers(config.TOP_N_STOCKS)
    print(f"Loaded {len(tickers)} tickers")

    # Step 2: Fetch stock data
    print("\nStep 2: Fetching stock data...")
    all_data = load_stocks_data(tickers)

    if not all_data:
        print("ERROR: No stock data loaded. Exiting.")
        return

    # Save cache
    save_cache(all_data, timestamp)

    # Step 3: Apply filters
    print("\nStep 3: Applying universe filters...")
    filtered_data = filter_universe(all_data)

    if not filtered_data:
        print("ERROR: No stocks passed filters. Exiting.")
        return

    # Step 4: Classify stocks
    print(f"\nStep 4: Classifying {len(filtered_data)} stocks...")
    results = {
        'strong_trend': [],
        'panic': [],
        'euphoria': []
    }

    for stock in filtered_data:
        classification = classify_stock(stock)

        if classification:
            strategy = classification['strategy']
            results[strategy].append({
                'ticker': stock['ticker'],
                'price': stock['current_price'],
                'change_1d': stock.get('change_1d', 0),
                'change_3d': stock.get('change_3d', 0),
                'change_5d': stock.get('change_5d', 0),
                'reason': classification['reason']
            })

    # Step 5: Print results
    print("\nStep 5: Generating results...")
    print_results(results)

    # Step 6: Save results
    print("\nStep 6: Saving results...")
    save_results(results, timestamp)

    print("\nAnalysis complete!")


if __name__ == "__main__":
    main()
