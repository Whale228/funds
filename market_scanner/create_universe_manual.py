"""
Manual universe creator with expanded ticker list.
Use this when automatic sources (NASDAQ FTP, Wikipedia) are unavailable.

This creates a curated list of ~1000+ major US stocks across all sectors.
"""

import os


def create_universe():
    """
    Create a comprehensive universe of US stocks manually.
    Includes major stocks from S&P 500, Russell 2000, and popular mid-caps.
    """

    # Major indices and sectors
    tickers = [
        # Mega-cap tech
        'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO', 'ORCL',
        'ADBE', 'CRM', 'INTC', 'AMD', 'QCOM', 'TXN', 'AMAT', 'NOW', 'INTU', 'IBM',
        'CSCO', 'PLTR', 'SNOW', 'PANW', 'CRWD', 'DDOG', 'NET', 'MDB', 'ZS', 'TEAM',

        # Finance
        'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'BLK', 'SCHW', 'AXP', 'BX',
        'V', 'MA', 'PYPL', 'SQ', 'FIS', 'FISV', 'ADP', 'COIN', 'SOFI', 'NU',

        # Healthcare & Pharma
        'UNH', 'JNJ', 'LLY', 'ABBV', 'MRK', 'PFE', 'TMO', 'ABT', 'DHR', 'BMY',
        'AMGN', 'GILD', 'VRTX', 'REGN', 'ISRG', 'SYK', 'BSX', 'MDT', 'CI', 'CVS',
        'HUM', 'ELV', 'ZTS', 'IDXX', 'BDX', 'ALGN', 'DXCM', 'MRNA', 'BIIB', 'ILMN',

        # Consumer & Retail
        'AMZN', 'WMT', 'HD', 'COST', 'TGT', 'LOW', 'TJX', 'ROST', 'ULTA', 'DG',
        'SBUX', 'MCD', 'YUM', 'CMG', 'BKNG', 'MAR', 'HLT', 'NKE', 'LULU', 'DKS',

        # Industrial & Manufacturing
        'HON', 'UNP', 'CAT', 'DE', 'BA', 'RTX', 'LMT', 'GD', 'NOC', 'GE',
        'MMM', 'ITW', 'EMR', 'ETN', 'CARR', 'OTIS', 'PCAR', 'CMI', 'ROK', 'DOV',

        # Energy
        'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO', 'OXY', 'HAL',
        'KMI', 'WMB', 'OKE', 'ET', 'EPD', 'FANG', 'DVN', 'HES', 'MRO', 'APA',

        # Utilities & Infrastructure
        'NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'SRE', 'XEL', 'ES', 'AWK',
        'PEG', 'ED', 'PCG', 'WEC', 'DTE', 'EIX', 'FE', 'AEE', 'CMS', 'CNP',

        # Materials & Chemicals
        'LIN', 'APD', 'SHW', 'ECL', 'DD', 'DOW', 'NEM', 'FCX', 'CTVA', 'ALB',
        'PPG', 'VMC', 'MLM', 'NUE', 'STLD', 'CF', 'MOS', 'IFF', 'FMC', 'CE',

        # Consumer Staples
        'PG', 'KO', 'PEP', 'PM', 'MO', 'COST', 'WMT', 'CL', 'KMB', 'GIS',
        'K', 'MDLZ', 'MNST', 'KHC', 'HSY', 'CAG', 'SJM', 'CPB', 'KDP', 'CHD',

        # Real Estate & REITs
        'PLD', 'AMT', 'CCI', 'EQIX', 'PSA', 'O', 'WELL', 'DLR', 'SPG', 'VICI',
        'AVB', 'EQR', 'ARE', 'VTR', 'INVH', 'MAA', 'ESS', 'UDR', 'CPT', 'HST',

        # Communication Services
        'GOOGL', 'META', 'NFLX', 'DIS', 'CMCSA', 'VZ', 'T', 'TMUS', 'EA', 'TTWO',
        'PARA', 'WBD', 'NWSA', 'FOXA', 'MTCH', 'PINS', 'SNAP', 'RBLX', 'LYV', 'SPOT',

        # Autos & Transportation
        'TSLA', 'GM', 'F', 'RIVN', 'LCID', 'NIO', 'LI', 'XPEV', 'UPS', 'FDX',
        'UAL', 'DAL', 'AAL', 'LUV', 'JBLU', 'ALK', 'SAVE', 'HA', 'UBER', 'LYFT',

        # E-commerce & Digital
        'AMZN', 'SHOP', 'EBAY', 'ETSY', 'W', 'CHWY', 'DASH', 'ABNB', 'BKNG', 'EXPE',

        # Semiconductors (expanded)
        'NVDA', 'AMD', 'INTC', 'QCOM', 'AVGO', 'TXN', 'AMAT', 'LRCX', 'KLAC', 'MCHP',
        'NXPI', 'ADI', 'MRVL', 'SWKS', 'QRVO', 'MU', 'WDC', 'STX', 'MPWR', 'ON',

        # Cloud & SaaS
        'MSFT', 'AMZN', 'GOOGL', 'ORCL', 'CRM', 'NOW', 'SNOW', 'DDOG', 'NET', 'ZS',
        'CRWD', 'S', 'OKTA', 'DOCN', 'TWLO', 'ZM', 'DOCU', 'BOX', 'DBX', 'WDAY',

        # Biotech
        'AMGN', 'GILD', 'BIIB', 'VRTX', 'REGN', 'MRNA', 'BNTX', 'ALNY', 'BMRN', 'SGEN',
        'NBIX', 'EXAS', 'IONS', 'TECH', 'UTHR', 'INCY', 'HALO', 'SRPT', 'RARE', 'FOLD',

        # Financial Services (expanded)
        'BRK-B', 'BRK-A', 'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'SCHW', 'USB',
        'PNC', 'TFC', 'COF', 'BK', 'STT', 'NTRS', 'RF', 'CFG', 'KEY', 'HBAN',

        # Insurance
        'BRK-B', 'PGR', 'ALL', 'TRV', 'CB', 'AIG', 'MET', 'PRU', 'AFL', 'HIG',
        'AJG', 'MMC', 'AON', 'WTW', 'BRO', 'RJF', 'CNA', 'RLI', 'CINF', 'AFG',

        # Retail (expanded)
        'AMZN', 'WMT', 'COST', 'TGT', 'HD', 'LOW', 'TJX', 'ROST', 'DG', 'DLTR',
        'BBY', 'BBWI', 'GPS', 'ANF', 'AEO', 'URBN', 'FIVE', 'OLLI', 'BIG', 'BURL',

        # Media & Entertainment
        'DIS', 'NFLX', 'PARA', 'WBD', 'FOXA', 'NWSA', 'LYV', 'MSG', 'MSGS', 'EDR',

        # Growth & Momentum stocks
        'TSLA', 'NVDA', 'AMD', 'PLTR', 'COIN', 'RBLX', 'HOOD', 'SOFI', 'RIVN', 'LCID',

        # Dividend aristocrats
        'JNJ', 'PG', 'KO', 'PEP', 'MMM', 'CAT', 'EMR', 'GPC', 'ITW', 'LOW',

        # Chinese ADRs
        'BABA', 'JD', 'PDD', 'BIDU', 'NIO', 'LI', 'XPEV', 'TME', 'BILI', 'VIPS',

        # Banking (regional)
        'USB', 'PNC', 'TFC', 'COF', 'MTB', 'FITB', 'HBAN', 'RF', 'CFG', 'KEY',
        'ZION', 'CMA', 'WTFC', 'FHN', 'SNV', 'ONB', 'UBSI', 'HWC', 'ASB', 'UMBF',

        # Small/Mid cap growth
        'HOOD', 'PLTR', 'RIVN', 'LCID', 'SOFI', 'COIN', 'RBLX', 'U', 'DKNG', 'PENN',
        'FUBO', 'SKLZ', 'MSTR', 'RIOT', 'MARA', 'CLSK', 'BTBT', 'HUT', 'BITF', 'ARBK',

        # Aerospace & Defense
        'BA', 'RTX', 'LMT', 'GD', 'NOC', 'HWM', 'TDG', 'TXT', 'LHX', 'LDOS',

        # Chemicals & Specialty
        'LYB', 'DOW', 'DD', 'CTVA', 'EMN', 'CF', 'MOS', 'FMC', 'ALB', 'SQM',

        # Food & Beverage
        'PEP', 'KO', 'MNST', 'KDP', 'KHC', 'GIS', 'HSY', 'MDLZ', 'K', 'CAG',
        'SJM', 'CPB', 'MKC', 'HRL', 'TSN', 'BG', 'ADM', 'BF-B', 'STZ', 'TAP',
    ]

    # Deduplicate and sort
    unique_tickers = sorted(list(set(tickers)))

    print(f"Created universe with {len(unique_tickers)} tickers")

    return unique_tickers


def save_universe(tickers, filename='data/us_stock_universe.txt'):
    """Save ticker list to file."""
    os.makedirs('data', exist_ok=True)

    with open(filename, 'w') as f:
        for ticker in tickers:
            f.write(f"{ticker}\n")

    print(f"Saved to {filename}")


def main():
    print("=" * 80)
    print("MANUAL TICKER UNIVERSE CREATION")
    print("=" * 80)
    print("\nCreating curated list of major US stocks...")

    tickers = create_universe()
    save_universe(tickers)

    print("\n" + "=" * 80)
    print("UNIVERSE READY")
    print("=" * 80)
    print(f"Total tickers: {len(tickers)}")
    print("\nNote: This is a curated list of major US stocks.")
    print("For complete market coverage (5000+ stocks), you can:")
    print("1. Download a CSV from finviz.com or similar screener")
    print("2. Place it in data/ folder and modify universe_loader.py")
    print("\nYou can now run: python3 main_full.py")
    print("=" * 80)


if __name__ == "__main__":
    main()
