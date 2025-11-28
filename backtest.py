#!/usr/bin/env python3
# pyright: reportMissingImports=false
"""
Simple 50 / 200 day moving-average crossover backtester.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd

from data_loader import load_price_history
from strategy import run_strategy


@dataclass
class BacktestStats:
    total_return: float
    cagr: float
    max_drawdown: float
    sharpe: float
    trades: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Backtest a simple moving-average crossover strategy."
    )
    parser.add_argument(
        "--data",
        type=Path,
        required=True,
        help="Path to daily history CSV (must contain a Close column).",
    )
    parser.add_argument("--short", type=int, default=50, help="Short SMA window.")
    parser.add_argument("--long", type=int, default=200, help="Long SMA window.")
    parser.add_argument(
        "--adx-window",
        type=int,
        default=14,
        help="ADX calculation window (baseline trend strength).",
    )
    parser.add_argument(
        "--capital", type=float, default=100_000, help="Starting capital."
    )
    parser.add_argument(
        "--trade-size",
        type=float,
        default=1.0,
        help="Fraction of capital allocated when in the market (0-1).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional path to save the equity curve to CSV.",
    )
    args = parser.parse_args()
    if args.short <= 0 or args.long <= 0:
        parser.error("Moving-average windows must be positive.")
    if args.short >= args.long:
        parser.error("Short window must be smaller than long window.")
    if not 0 < args.trade_size <= 1:
        parser.error("trade-size must be within (0, 1].")
    if args.adx_window <= 0:
        parser.error("ADX window must be positive.")
    if args.capital <= 0:
        parser.error("Starting capital must be positive.")
    return args


def summarize_performance(df: pd.DataFrame) -> BacktestStats:
    equity = df["equity_curve"]
    total_return = equity.iloc[-1] / equity.iloc[0] - 1.0
    years = (df.index[-1] - df.index[0]).days / 365.25
    cagr = (equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1 if years > 0 else 0.0
    rolling_max = equity.cummax()
    drawdowns = equity / rolling_max - 1.0
    max_drawdown = drawdowns.min()
    daily_std = df["strategy_return"].std()
    sharpe = (
        np.sqrt(252) * df["strategy_return"].mean() / daily_std if daily_std else 0.0
    )
    trades = int((df["trade_change"].abs() > 0).sum())
    return BacktestStats(
        total_return=total_return,
        cagr=cagr,
        max_drawdown=max_drawdown,
        sharpe=sharpe,
        trades=trades,
    )


def save_equity_curve(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df[["equity_curve", "strategy_return", "position"]].to_csv(path)


def main() -> None:
    args = parse_args()
    df = load_price_history(args.data)
    results = run_strategy(
        df, args.short, args.long, args.trade_size, args.adx_window, args.capital
    )
    stats = summarize_performance(results)
    print(
        "\n".join(
            [
                f"Total Return: {stats.total_return:.2%}",
                f"CAGR: {stats.cagr:.2%}",
                f"Max Drawdown: {stats.max_drawdown:.2%}",
                f"Sharpe (daily->annualized): {stats.sharpe:.2f}",
                f"Trades: {stats.trades}",
                f"Final Equity: {results['equity_curve'].iloc[-1]:,.2f}",
            ]
        )
    )
    if args.out:
        save_equity_curve(results, args.out)
        print(f"\nSaved equity curve to {args.out}")


if __name__ == "__main__":
    main()

