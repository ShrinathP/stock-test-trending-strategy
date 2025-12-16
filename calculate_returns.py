from __future__ import annotations

import numpy as np
import pandas as pd


ACTIVE_SIGNALS = {1.0, 2.0, 3.0}


def calculate_returns(df: pd.DataFrame, initial_capital: float) -> pd.DataFrame:
    """
    Compute trade-based returns without re-reading CSV files.

    Buy when signal flips from -1.0 to {1.0, 2.0, 3.0}; sell when it returns to -1.0.
    """
    df = df.copy()
    signal = df["signal"].fillna(0.0)
    prev_signal = signal.shift(1).fillna(0.0)

    entry_mask = (prev_signal == -1.0) & (signal.isin([1.0, 2.0, 3.0]))
    exit_mask = (prev_signal.isin([1.0, 2.0, 3.0])) & (signal == -1.0)

    df["entry"] = entry_mask
    df["exit"] = exit_mask

    df["entry_price"] = df["Close"].where(entry_mask).ffill()
    in_trade = signal.isin(ACTIVE_SIGNALS)
    df["current_trade_return"] = np.where(
        in_trade, df["Close"] / df["entry_price"] - 1.0, 0.0
    )
    df.loc[exit_mask, "realized_return"] = (
        df.loc[exit_mask, "Close"] / df.loc[exit_mask, "entry_price"] - 1.0
    )
    cumulative = (1 + df["realized_return"].fillna(0.0)).cumprod()
    df["cumulative_return"] = cumulative - 1
    df["trade_equity_curve"] = initial_capital * cumulative
    df["equity_curve"] = df["trade_equity_curve"]
    df["strategy_return"] = df["equity_curve"].pct_change().fillna(0.0)

    return df

