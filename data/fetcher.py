"""
fetcher.py — Live stock data retrieval with in-memory caching.
"""

from __future__ import annotations

import time
from datetime import datetime
from typing import Dict, Tuple

import pandas as pd
import yfinance as yf


class StockDataFetcher:
    """
    Fetches OHLCV data from Yahoo Finance via yfinance with time-based caching
    to avoid redundant API calls during an active dashboard session.
    """

    def __init__(self, cache_ttl_minutes: int = 5) -> None:
        self._cache: Dict[str, Tuple[pd.DataFrame, float]] = {}
        self._ttl = cache_ttl_minutes * 60

    def _cache_key(self, ticker: str, start: str, end: str) -> str:
        return f"{ticker}|{start}|{end}"

    def fetch(self, ticker: str, start: str, end: str) -> pd.DataFrame:
        """
        Download daily OHLCV data for the given ticker and date range.

        Args:
            ticker: Stock ticker symbol (e.g. "AAPL").
            start:  Start date as ISO string "YYYY-MM-DD".
            end:    End date as ISO string "YYYY-MM-DD".

        Returns:
            DataFrame with columns: Open, High, Low, Close, Adj Close, Volume.
        """
        key = self._cache_key(ticker, start, end)

        if key in self._cache:
            df, ts = self._cache[key]
            if time.time() - ts < self._ttl:
                return df.copy()

        df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)

        if df.empty:
            raise ValueError(f"No data found for ticker '{ticker}' in range {start} to {end}.")

        # Flatten multi-level columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df.index = pd.to_datetime(df.index)
        df = df.sort_index()

        self._cache[key] = (df, time.time())
        return df.copy()

    def fetch_info(self, ticker: str) -> dict:
        """Return company info dict from yfinance."""
        return yf.Ticker(ticker).info
