from __future__ import annotations

# pyright: reportMissingImports=false

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
    # Step 1: Add indicators to the dataframe
    df = add_indicators(df, short_window, long_window, adx_window)

    # Step 2: Generate signal when fast SMA is above long SMA
    df["signal"] = np.where(
        df[f"SMA_{short_window}"] > df[f"SMA_{long_window}"], 1.0, 0.0
    )

    # Step 3: Position strength equals fast SMA slope when signal is 1.0, otherwise 0.0
    fast_sma_slope_col = f"SMA_{short_window}_slope"
    df["pos_strength"] = df[fast_sma_slope_col].where(df["signal"] == 1.0, 0.0).fillna(
        0.0
    )

    # Step 4: If fast SMA slope is negative for 2 consecutive sessions, set signal to -1.0
    df["signal"] = np.where(
        (df["signal"] == 1.0) & prev_n_negative_slope(df, fast_sma_slope_col, 2), -1.0, df["signal"].fillna(0.0)
    )

    # Step 5: If slow SMA slope is greater than 0.2, set signal to 2.0
    slow_sma_slope_col = f"SMA_{long_window}_slope"
    df["signal"] = np.where(
        (df["signal"] == 1.0) & df[slow_sma_slope_col] >= 0.2, 2.0, df["signal"].fillna(0.0)
    )

    # Step 6: If slow SMA slope is greater than 0.2 and fast SMA slope is greater than 0.15, set signal to 3.0
    df["signal"] = np.where(
    (df["signal"] == 2.0)
    & (df[slow_sma_slope_col] >= 0.2)
    & (df[fast_sma_slope_col] >= 0.15),
    3.0,
    df["signal"].fillna(0.0),
    )

    # Step 7: If -ADX is greater than +ADX and ADX value is high and increasing then exit with -1
    
    adx_col = f"ADX_{adx_window}"
    di_plus_col = f"+DI_{adx_window}"
    di_minus_col = f"-DI_{adx_window}"
    df["signal"] = np.where(
    ((df["signal"] == 2.0) | (df["signal"] == 3.0) | (df["signal"] == 1.0))
    & (df[di_minus_col] > df[di_plus_col])
    & (df[adx_col] >= 25.0)
    & (df[adx_col] > df[adx_col].shift(2) + 0.5),
    -1.0,
    df["signal"].fillna(0.0),
    )


    # df["position"] = (df["signal"].shift(1).fillna(0.0)) * trade_size
    position = (df["signal"].shift(1).fillna(0.0)) * trade_size
    close_returns = df["Close"].pct_change().fillna(0.0)
    df["strategy_return"] = position * close_returns
    df["equity_curve"] = initial_capital * (1.0 + df["strategy_return"]).cumprod()
    df["trade_change"] = position.diff().fillna(0.0)
    
    # drop rows where SMA_long_window is not available
    df = df.dropna(subset=[f"SMA_{long_window}"])

    result = df
    column_order = ["signal", "pos_strength"] + [
        c for c in result.columns if c not in {"signal", "pos_strength"}
    ]
    result = result[column_order]
    result.to_csv("nifty_daily_history_output.csv")
    return result


def prev_n_negative_slope(df, col, n):
    shifted = df[col].shift(1)
    neg = shifted < 0
    # rolling sum must equal n for all negative
    return neg.rolling(n).sum() == n


