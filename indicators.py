from __future__ import annotations

# pyright: reportMissingImports=false

import numpy as np
import pandas as pd
import talib


def add_indicators(
    df: pd.DataFrame, short_window: int, long_window: int, adx_window: int
) -> pd.DataFrame:
    """Append SMA/ADX indicators, slopes, and DI components."""
    prices = df["Close"].astype(float).to_numpy(copy=False)
    short_col = f"SMA_{short_window}"
    long_col = f"SMA_{long_window}"
    df[short_col] = talib.SMA(prices, timeperiod=short_window)
    df[long_col] = talib.SMA(prices, timeperiod=long_window)
    df[f"{short_col}_slope"] = (
        df[short_col].diff(2) / df[short_col].shift(2)
    ).replace([np.inf, -np.inf], np.nan) * 100.0
    df[f"{long_col}_slope"] = (
        df[long_col].diff(2) / df[long_col].shift(2)
    ).replace([np.inf, -np.inf], np.nan) * 100.0
    if not {"High", "Low"}.issubset(df.columns):
        raise ValueError("CSV must include High and Low columns for ADX calculation.")
    high = df["High"].astype(float).to_numpy(copy=False)
    low = df["Low"].astype(float).to_numpy(copy=False)
    adx_col = f"ADX_{adx_window}"
    df[adx_col] = talib.ADX(high, low, prices, timeperiod=adx_window)
    df[f"{adx_col}_slope"] = (
        df[adx_col].diff(2) / df[adx_col].shift(2)
    ).replace([np.inf, -np.inf], np.nan) * 100.0
    df[f"+DI_{adx_window}"] = talib.PLUS_DI(high, low, prices, timeperiod=adx_window)
    df[f"-DI_{adx_window}"] = talib.MINUS_DI(high, low, prices, timeperiod=adx_window)
    df.to_csv("nifty_daily_history_input.csv")
    return df

