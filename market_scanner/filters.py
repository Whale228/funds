"""
Universe filtering module.
Applies filters based on market cap, price, and volume criteria.
"""

import config


def filter_universe(stock_data_list):
    """
    Filter stocks based on universe criteria.

    Filters applied:
    1. Market capitalization >= MIN_MARKET_CAP
    2. Current price >= MIN_PRICE
    3. Average daily dollar volume >= MIN_AVG_VOLUME

    Args:
        stock_data_list (list): List of stock data dictionaries

    Returns:
        list: Filtered list of stock data dictionaries
    """
    filtered = []
    initial_count = len(stock_data_list)

    print(f"\nApplying universe filters to {initial_count} stocks...")
    print(f"  Market cap >= ${config.MIN_MARKET_CAP/1e6:.0f}M")
    print(f"  Price >= ${config.MIN_PRICE:.2f}")
    print(f"  Avg daily volume >= ${config.MIN_AVG_VOLUME/1e6:.0f}M")

    for stock in stock_data_list:
        ticker = stock['ticker']
        market_cap = stock['market_cap']
        price = stock['current_price']
        avg_volume = stock['avg_volume_20d']

        # Calculate average daily dollar volume (price × volume)
        avg_dollar_volume = price * avg_volume

        # Apply filters
        if market_cap < config.MIN_MARKET_CAP:
            print(f"  {ticker}: Filtered out (market cap ${market_cap/1e9:.2f}B < ${config.MIN_MARKET_CAP/1e9:.2f}B)")
            continue

        if price < config.MIN_PRICE:
            print(f"  {ticker}: Filtered out (price ${price:.2f} < ${config.MIN_PRICE:.2f})")
            continue

        if avg_dollar_volume < config.MIN_AVG_VOLUME:
            print(f"  {ticker}: Filtered out (avg volume ${avg_dollar_volume/1e6:.1f}M < ${config.MIN_AVG_VOLUME/1e6:.0f}M)")
            continue

        # Stock passes all filters
        filtered.append(stock)

    filtered_out = initial_count - len(filtered)
    print(f"\nFiltering complete: {len(filtered)} stocks passed, {filtered_out} filtered out")

    return filtered


def rank_by_market_cap(stock_data_list):
    """
    Sort stocks by market capitalization in descending order.

    Args:
        stock_data_list (list): List of stock data dictionaries

    Returns:
        list: Sorted list of stock data dictionaries
    """
    return sorted(stock_data_list, key=lambda x: x['market_cap'], reverse=True)


def get_filter_stats(stock_data_list):
    """
    Get statistics about the filtered universe.

    Args:
        stock_data_list (list): List of stock data dictionaries

    Returns:
        dict: Statistics including counts, averages, and ranges
    """
    if not stock_data_list:
        return {
            'count': 0,
            'avg_market_cap': 0,
            'avg_price': 0,
            'avg_volume': 0
        }

    market_caps = [s['market_cap'] for s in stock_data_list]
    prices = [s['current_price'] for s in stock_data_list]
    volumes = [s['avg_volume_20d'] for s in stock_data_list]

    return {
        'count': len(stock_data_list),
        'avg_market_cap': sum(market_caps) / len(market_caps),
        'min_market_cap': min(market_caps),
        'max_market_cap': max(market_caps),
        'avg_price': sum(prices) / len(prices),
        'min_price': min(prices),
        'max_price': max(prices),
        'avg_volume': sum(volumes) / len(volumes)
    }
