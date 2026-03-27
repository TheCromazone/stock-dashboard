"""
indicators.py — Technical indicator calculations using pandas and the `ta` library.
"""

from __future__ import annotations
import pandas as pd
import numpy as np


class TechnicalIndicators:
    """
    Static methods to compute common technical analysis indicators.
    All methods accept and return a copy of the OHLCV DataFrame.
    """

    @staticmethod
    def sma(df: pd.DataFrame, window: int) -> pd.Series:
        return df["Close"].rolling(window=window).mean()

    @staticmethod
    def ema(df: pd.DataFrame, span: int) -> pd.Series:
        return df["Close"].ewm(span=span, adjust=False).mean()

    @staticmethod
    def bollinger_bands(df: pd.DataFrame, window: int = 20, num_std: float = 2.0):
        sma = df["Close"].rolling(window).mean()
        std = df["Close"].rolling(window).std()
        return sma + num_std * std, sma, sma - num_std * std  # upper, mid, lower

    @staticmethod
    def rsi(df: pd.DataFrame, window: int = 14) -> pd.Series:
        delta = df["Close"].diff()
        gain = delta.clip(lower=0).rolling(window).mean()
        loss = (-delta.clip(upper=0)).rolling(window).mean()
        rs = gain / loss.replace(0, np.nan)
        return 100 - (100 / (1 + rs))

    @staticmethod
    def macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9):
        ema_fast = df["Close"].ewm(span=fast, adjust=False).mean()
        ema_slow = df["Close"].ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    @staticmethod
    def atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
        high_low = df["High"] - df["Low"]
        high_close = (df["High"] - df["Close"].shift()).abs()
        low_close = (df["Low"] - df["Close"].shift()).abs()
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return true_range.rolling(window).mean()

    @classmethod
    def add_all(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Compute and attach all indicators to the DataFrame."""
        df = df.copy()
        df["sma20"] = cls.sma(df, 20)
        df["sma50"] = cls.sma(df, 50)
        df["sma200"] = cls.sma(df, 200)
        df["ema12"] = cls.ema(df, 12)
        df["ema26"] = cls.ema(df, 26)
        df["bb_upper"], df["bb_mid"], df["bb_lower"] = cls.bollinger_bands(df)
        df["rsi"] = cls.rsi(df)
        df["macd"], df["macd_signal"], df["macd_hist"] = cls.macd(df)
        df["atr"] = cls.atr(df)
        return df
