#!/usr/bin/env python3
"""
fetch_markets.py
================

This script retrieves a handful of market indicators and writes them to
`data/markets.json`.  The indicators include energy prices (Brent and WTI
crude, natural gas), defence and shipping equities, a broad commodity index
and a volatility index.  The data is pulled using the `yfinance` package
which provides access to Yahoo Finance without requiring an API key.

If `yfinance` is not installed, the script will exit with an informative
message.  You can install it with `pip install yfinance`.

"""
import datetime
import json
import sys
from pathlib import Path

try:
    import yfinance as yf  # type: ignore
except ImportError:
    print(
        "The yfinance library is required to fetch market data."
        " Please install it with 'pip install yfinance'.",
        file=sys.stderr,
    )
    sys.exit(1)


TICKERS: dict[str, str] = {
    "Brent Crude": "BZ=F",      # ICE Brent Crude futures
    "WTI Crude": "CL=F",        # NYMEX WTI Crude futures
    "Natural Gas": "NG=F",      # Henry Hub Natural Gas futures
    "Defense ETF": "ITA",       # iShares U.S. Aerospace & Defense ETF
    "Shipping ETF": "SEA",      # Breakwave Sea shipping ETF
    "Commodity Index": "GSG",   # iShares S&P GSCI Commodity-Indexed Trust
    "Volatility Index": "^VIX", # CBOE Volatility Index
}


def fetch_price(symbol: str) -> float | None:
    """Return the latest closing price for the given ticker symbol."""
    try:
        ticker = yf.Ticker(symbol)
        # Request the most recent trading day; use "1d" period with daily interval
        hist = ticker.history(period="2d", interval="1d")
        # Use the last non‑NaN close
        if not hist.empty:
            close = hist["Close"].dropna()
            if not close.empty:
                return float(close.iloc[-1])
    except Exception:
        pass
    return None


def main() -> None:
    repo_dir = Path(__file__).resolve().parents[1]
    data_dir = repo_dir / "data"
    data_dir.mkdir(exist_ok=True)
    items: list[dict] = []
    timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    for name, symbol in TICKERS.items():
        price = fetch_price(symbol)
        if price is None:
            continue
        items.append(
            {
                "timestamp": timestamp,
                "symbol": symbol,
                "name": name,
                "price": price,
            }
        )
    # Write markets.json
    markets_path = data_dir / "markets.json"
    with open(markets_path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()