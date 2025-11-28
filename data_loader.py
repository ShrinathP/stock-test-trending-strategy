from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_price_history(csv_path: Path) -> pd.DataFrame:
    """Load daily OHLC data and ensure datetime index."""
    df = pd.read_csv(csv_path)
    date_col = next((c for c in ("Date", "date", "realtime") if c in df.columns), None)
    if not date_col:
        raise ValueError("CSV must include a Date/realtime column.")
    df = df.rename(columns={date_col: "Date"})
    if "Close" not in df.columns:
        raise ValueError("CSV must include a Close column.")
    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d")
    return df.set_index("Date")

