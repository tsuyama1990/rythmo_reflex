import numpy as np
import pandas as pd
import polars as pl
from typing import Any


def run_backtest(df: pl.DataFrame, anomaly_type: str, slippage_pct: float) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Run backtest based on anomaly signals using manual calculations.

    Args:
        df: Polars DataFrame with processed quotes and features.
        anomaly_type: Type of anomaly ("day_of_week" or "month_end").
        slippage_pct: Slippage in percentage (e.g., 0.1 for 0.1%).

    Returns:
        Tuple of (metrics_dict, equity_curve_list)
    """
    if df.is_empty():
        return {}, []

    # Convert to pandas for easier manipulation of time series
    pdf = df.to_pandas()
    pdf = pdf.sort_values(['Code', 'Date'])

    # Calculate trade returns based on anomaly
    pdf['Trade_Return'] = 0.0
    # Apply slippage (twice: once for entry, once for exit)
    slippage = (slippage_pct / 100.0) * 2

    if anomaly_type == "day_of_week":
        # Buy Tuesday Open, Sell Tuesday Close (intraday)
        # return = (Close - Open) / Open - slippage
        # In Polars dt.weekday(): 1=Mon, 2=Tue, etc.
        mask = (pdf['DayOfWeek'] == 2)
        pdf.loc[mask, 'Trade_Return'] = (pdf.loc[mask, 'Close'] - pdf.loc[mask, 'Open']) / pdf.loc[mask, 'Open'] - slippage

    elif anomaly_type == "month_end":
        # Buy at Month End Close, Sell next day Close
        # Entry on Month End (Close), Exit on Next Day (Close)
        # The return is the Return_Daily of the day AFTER Month End
        is_after_month_end = pdf.groupby('Code')['Is_MonthEnd'].shift(1).fillna(False).astype(bool)
        pdf.loc[is_after_month_end, 'Trade_Return'] = pdf.loc[is_after_month_end, 'Return_Daily'] - slippage
    else:
        msg = f"Unknown anomaly type: {anomaly_type}"
        raise ValueError(msg)

    # Calculate Portfolio Equity Curve (Average return across all tickers for each day)
    # 1. Pivot trade returns: Rows=Date, Cols=Code
    daily_returns_df = pdf.pivot(index='Date', columns='Code', values='Trade_Return').fillna(0.0)
    
    # 2. Average daily return across all tickers
    avg_daily_return = daily_returns_df.mean(axis=1)
    
    # 3. Cumulative equity (starting from 100)
    # Using compounding: (1 + r).cumprod()
    equity_curve_series = (1 + avg_daily_return).cumprod() * 100
    
    # 4. Extract metrics
    # Only consider days where trades actually happened (non-zero returns)
    active_returns = avg_daily_return[avg_daily_return != 0]
    
    if len(active_returns) > 0:
        win_rate = (active_returns > 0).mean() * 100
        total_return = (equity_curve_series.iloc[-1] - 100.0)
        
        pos_returns = active_returns[active_returns > 0].sum()
        neg_returns = abs(active_returns[active_returns < 0].sum())
        profit_factor = pos_returns / neg_returns if neg_returns > 0 else float('inf')
        
        sharpe = (active_returns.mean() / active_returns.std() * np.sqrt(252)) if active_returns.std() > 0 else 0.0
        
        # Max Drawdown
        rolling_max = equity_curve_series.cummax()
        drawdown = (equity_curve_series - rolling_max) / rolling_max
        max_drawdown = drawdown.min() * 100
    else:
        win_rate = 0.0
        total_return = 0.0
        profit_factor = 0.0
        sharpe = 0.0
        max_drawdown = 0.0

    metrics = {
        "Win Rate [%]": float(win_rate),
        "Profit Factor": float(profit_factor),
        "Total Return [%]": float(total_return),
        "Sharpe Ratio": float(sharpe),
        "Max Drawdown [%]": float(max_drawdown),
    }

    # Convert equity curve to list of dicts for Reflex chart
    equity_curve = [
        {"Date": date.strftime("%Y-%m-%d"), "Equity": float(val)}
        for date, val in equity_curve_series.items()
    ]

    return metrics, equity_curve
