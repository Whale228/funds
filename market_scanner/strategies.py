"""
Trading strategies module.
Contains logic for classifying stocks into Strong Trend, Panic, and Euphoria categories.
"""

import pandas as pd
import config


def calculate_price_changes(price_history):
    """
    Calculate price changes over different time periods.

    Args:
        price_history (DataFrame): DataFrame with OHLCV data

    Returns:
        dict: Dictionary with price change metrics:
            - change_1d: 1-day price change (%)
            - change_3d: 3-day price change (%)
            - change_5d: 5-day price change (%)
            - change_3d_consecutive: Boolean if 3 consecutive days of gains
            - daily_changes: List of daily percentage changes
            - avg_daily_change_5d: Average daily change over 5 days
    """
    closes = price_history['Close']

    if len(closes) < 2:
        return None

    # Calculate percentage changes
    change_1d = ((closes.iloc[-1] / closes.iloc[-2]) - 1) * 100 if len(closes) >= 2 else 0
    change_3d = ((closes.iloc[-1] / closes.iloc[-4]) - 1) * 100 if len(closes) >= 4 else 0
    change_5d = ((closes.iloc[-1] / closes.iloc[-6]) - 1) * 100 if len(closes) >= 6 else 0

    # Check for 3 consecutive days of gains
    consecutive_gains = False
    if len(closes) >= 4:
        day1_gain = (closes.iloc[-1] / closes.iloc[-2]) - 1
        day2_gain = (closes.iloc[-2] / closes.iloc[-3]) - 1
        day3_gain = (closes.iloc[-3] / closes.iloc[-4]) - 1

        consecutive_gains = (day1_gain >= config.STRONG_TREND_MIN_GAIN / 100 and
                           day2_gain >= config.STRONG_TREND_MIN_GAIN / 100 and
                           day3_gain >= config.STRONG_TREND_MIN_GAIN / 100)

    # Calculate daily changes for last 5 days
    daily_changes = []
    if len(closes) >= 6:
        for i in range(-5, 0):
            daily_change = ((closes.iloc[i] / closes.iloc[i-1]) - 1) * 100
            daily_changes.append(daily_change)

        avg_daily_change_5d = sum(daily_changes) / len(daily_changes)
    else:
        avg_daily_change_5d = 0

    return {
        'change_1d': change_1d,
        'change_3d': change_3d,
        'change_5d': change_5d,
        'change_3d_consecutive': consecutive_gains,
        'daily_changes': daily_changes,
        'avg_daily_change_5d': avg_daily_change_5d
    }


def classify_strong_trend(stock_data, price_changes):
    """
    Classify if stock shows strong upward trend.

    Conditions:
    - Gain >= 5% for each of last 3 consecutive days
    - OR total gain >= 15% over 3 days with positive momentum

    Args:
        stock_data (dict): Stock data dictionary
        price_changes (dict): Price change metrics

    Returns:
        tuple: (is_strong_trend: bool, reason: str)
    """
    if not price_changes:
        return False, ""

    # Check for 3 consecutive days of 5%+ gains
    if price_changes['change_3d_consecutive']:
        return True, f"3 consecutive days with {config.STRONG_TREND_MIN_GAIN}%+ gains each"

    # Check for 15%+ total gain over 3 days with positive momentum
    if price_changes['change_3d'] >= config.STRONG_TREND_3DAY_TOTAL:
        if price_changes['change_1d'] > 0:  # Positive momentum
            return True, f"{price_changes['change_3d']:.1f}% gain over 3 days with positive momentum"

    return False, ""


def classify_panic(stock_data, price_changes):
    """
    Classify if stock is in panic mode.

    Conditions:
    - Drop >= 8% in last day
    - OR drop >= 15% over last 3 days
    - Additional confirmation: current volume > 1.5x average volume

    Args:
        stock_data (dict): Stock data dictionary
        price_changes (dict): Price change metrics

    Returns:
        tuple: (is_panic: bool, reason: str)
    """
    if not price_changes:
        return False, ""

    # Check for single-day panic drop
    if price_changes['change_1d'] <= -config.PANIC_1DAY_DROP:
        # Verify with volume spike
        volume_history = stock_data['volume_history']
        avg_volume = stock_data['avg_volume_20d']

        if len(volume_history) > 0:
            current_volume = volume_history[-1]
            volume_spike = current_volume > (avg_volume * config.PANIC_VOLUME_MULTIPLIER)

            if volume_spike:
                return True, f"{abs(price_changes['change_1d']):.1f}% drop in 1 day with {current_volume/avg_volume:.1f}x volume spike"
            else:
                return True, f"{abs(price_changes['change_1d']):.1f}% drop in 1 day"

    # Check for 3-day panic drop
    if price_changes['change_3d'] <= -config.PANIC_3DAY_DROP:
        return True, f"{abs(price_changes['change_3d']):.1f}% drop over 3 days"

    return False, ""


def classify_euphoria(stock_data, price_changes):
    """
    Classify if stock is in euphoria mode.

    Conditions:
    - Gain >= 8% in last day
    - OR gain >= 20% over last 5 days
    - Additional check: last day gain > average daily gain over 5 days (acceleration)

    Args:
        stock_data (dict): Stock data dictionary
        price_changes (dict): Price change metrics

    Returns:
        tuple: (is_euphoria: bool, reason: str)
    """
    if not price_changes:
        return False, ""

    # Check for single-day euphoria
    if price_changes['change_1d'] >= config.EUPHORIA_1DAY_GAIN:
        # Check for acceleration
        if price_changes['avg_daily_change_5d'] > 0:
            if price_changes['change_1d'] > price_changes['avg_daily_change_5d']:
                return True, f"{price_changes['change_1d']:.1f}% gain in 1 day with acceleration (avg: {price_changes['avg_daily_change_5d']:.1f}%)"
            else:
                return True, f"{price_changes['change_1d']:.1f}% gain in 1 day"
        else:
            return True, f"{price_changes['change_1d']:.1f}% gain in 1 day"

    # Check for 5-day euphoria
    if price_changes['change_5d'] >= config.EUPHORIA_5DAY_GAIN:
        return True, f"{price_changes['change_5d']:.1f}% gain over 5 days"

    return False, ""


def classify_stock(stock_data):
    """
    Classify a stock into one of the strategy categories.

    Priority order:
    1. Strong Trend
    2. Panic
    3. Euphoria

    Excludes stocks that match both Panic AND Euphoria (noise).

    Args:
        stock_data (dict): Stock data dictionary

    Returns:
        dict: Classification result with 'strategy' and 'reason' keys, or None
    """
    # Calculate price changes
    price_changes = calculate_price_changes(stock_data['price_history'])

    if not price_changes:
        return None

    # Enrich stock_data with price changes for easy access
    stock_data.update(price_changes)

    # Check each strategy
    is_strong_trend, trend_reason = classify_strong_trend(stock_data, price_changes)
    is_panic, panic_reason = classify_panic(stock_data, price_changes)
    is_euphoria, euphoria_reason = classify_euphoria(stock_data, price_changes)

    # Filter out noise: stocks that are both panic and euphoria
    if is_panic and is_euphoria:
        return None

    # Apply priority order
    if is_strong_trend:
        return {
            'strategy': 'strong_trend',
            'reason': trend_reason
        }

    if is_panic:
        return {
            'strategy': 'panic',
            'reason': panic_reason
        }

    if is_euphoria:
        return {
            'strategy': 'euphoria',
            'reason': euphoria_reason
        }

    return None
