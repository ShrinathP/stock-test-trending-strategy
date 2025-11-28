# stock-test-trending-strategy

Simple Python backtester for a 50 / 200 day moving-average crossover strategy.

## Prerequisites

- Python 3.10+
- TA-Lib native binaries installed on your system (macOS: `brew install ta-lib`)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> macOS typically exposes Python via `python3` instead of `python`. If `python` is not found, use `python3` for all commands (including running the backtester: `python3 backtest.py ...`), or create an alias if you prefer.

## Usage

```bash
python backtest.py \
  --data /Users/shrinath.potul/Documents/Shrinath/strategy/nifty_daily_history.csv \
  --short 50 \
  --long 200 \
  --adx-window 14 \
  --capital 100000 \
  --trade-size 1.0 \
  --out equity_curve.csv
```

- `--short` / `--long`: moving-average windows (in trading days)
- `--trade-size`: fraction of capital allocated on long signals (0-1)
- `--adx-window`: ADX / +/-DI lookback for baseline trend strength
- `--out`: optional path to dump equity curve + strategy returns

## Output

The script prints summary stats (total return, CAGR, drawdown, Sharpe, trades). If `--out` is provided, the resulting CSV also contains `ADX_<window>`, `ADX_<window>_slope`, `+DI_<window>`, `-DI_<window>`, and `SMA_<window>_slope` columns for additional analysis or filtering. Slope columns represent the percentage change over the prior observation (two-session lookback, expressed in %/day), so negative values still indicate downward momentum.
