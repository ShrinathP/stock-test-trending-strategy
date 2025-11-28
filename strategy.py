from __future__ import annotations

import numpy as np
import pandas as pd

from indicators import add_indicators


def run_strategy(
    df: pd.DataFrame,
    short_window: int,
    long_window: int,
    trade_size: float,
    adx_window: int,
    initial_capital: float,
) -> pd.DataFrame:
    """Decorate price history with indicators and compute equity curve."""
    df = df.copy()
    df = add_indicators(df, short_window, long_window, adx_window)
    df["signal"] = np.where(
        df[f"SMA_{short_window}"] > df[f"SMA_{long_window}"], 1.0, 0.0
    )
    df["position"] = (df["signal"].shift(1).fillna(0.0)) * trade_size
    df["return"] = df["Close"].pct_change().fillna(0.0)
    df["strategy_return"] = df["position"] * df["return"]
    df["equity_curve"] = initial_capital * (1.0 + df["strategy_return"]).cumprod()
    df["trade_change"] = df["position"].diff().fillna(0.0)
    return df.dropna(subset=[f"SMA_{long_window}"])

