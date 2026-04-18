import warnings
from typing import Any

import pandas as pd
import polars as pl
import vectorbt as vbt


def run_backtest(df: pl.DataFrame, anomaly_type: str, slippage_pct: float) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Run vectorbt backtest based on anomaly signals.

    Args:
        df: Polars DataFrame with processed quotes and features.
        anomaly_type: Type of anomaly ("day_of_week" or "month_end").
        slippage_pct: Slippage in percentage (e.g., 0.1 for 0.1%).

    Returns:
        Tuple of (metrics_dict, equity_curve_list)
    """
    if df.is_empty():
        return {}, []

    # Convert to pandas for vectorbt
    pdf = df.to_pandas()

    # Pivot data so rows are Dates and columns are Codes
    # We will need Open and Close prices for intraday signals
    open_prices = pdf.pivot(index='Date', columns='Code', values='Open')
    close_prices = pdf.pivot(index='Date', columns='Code', values='Close')

    # Fill missing values (if any remain)
    open_prices = open_prices.ffill()
    close_prices = close_prices.ffill()

    # Generate signals
    entries = pd.DataFrame(False, index=open_prices.index, columns=open_prices.columns)
    exits = pd.DataFrame(False, index=open_prices.index, columns=open_prices.columns)

    if anomaly_type == "day_of_week":
        # Example: Buy Tuesday Open, Sell Tuesday Close (intraday)
        # In Polars dt.weekday(): 1=Mon, 2=Tue, etc.
        # We need the day of week as a DataFrame matching the shape of prices
        dow = pdf.pivot(index='Date', columns='Code', values='DayOfWeek')
        entries = (dow == 2)
        exits = (dow == 2)

        # Since it's intraday, entry price is Open, exit price is Close
        price_in = open_prices

    elif anomaly_type == "month_end":
        # Example: Buy at Month End Close, Sell next day Close
        is_month_end = pdf.pivot(index='Date', columns='Code', values='Is_MonthEnd')
        # Fill missing boolean values with False
        is_month_end = is_month_end.fillna(False)

        entries = is_month_end.astype(bool)
        # Exit on the next day (shift entries by 1)
        exits = entries.shift(1).fillna(False)

        # Daily holding, use Close prices
        price_in = close_prices
    else:
        msg = f"Unknown anomaly type: {anomaly_type}"
        raise ValueError(msg)

    # Set up portfolio
    # Using vbt.Portfolio.from_signals
    # We specify price for entries and exits to handle intraday
    pf = vbt.Portfolio.from_signals(
        close=price_in, # default price
        entries=entries,
        exits=exits,
        price=price_in, # entry price
        tp_stop=1.0, # vectorbt from_signals doesnt have stop_price parameter, will use exit signals # exit price for this specific case where exits might happen same day or next day close
        slippage=slippage_pct / 100.0,
        fees=0.0,
        freq='1D'
    )

    # Calculate metrics
    # If multiple columns (Codes), we get a DataFrame of metrics. Let's aggregate or take mean.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        stats = pf.stats()

    # Handle single vs multiple assets in stats
    if isinstance(stats, pd.DataFrame):
         # Take mean of the stats across all assets for the summary
         mean_stats = stats.mean(numeric_only=True)

         # Convert to dict
         metrics = {
             "Win Rate [%]": float(mean_stats.get("Win Rate [%]", 0.0)),
             "Profit Factor": float(mean_stats.get("Profit Factor", 0.0)),
             "Total Return [%]": float(mean_stats.get("Total Return [%]", 0.0)),
             "Sharpe Ratio": float(mean_stats.get("Sharpe Ratio", 0.0)),
             "Max Drawdown [%]": float(mean_stats.get("Max Drawdown [%]", 0.0)),
         }
    else:
         metrics = {
             "Win Rate [%]": float(stats.get("Win Rate [%]", 0.0)),
             "Profit Factor": float(stats.get("Profit Factor", 0.0)),
             "Total Return [%]": float(stats.get("Total Return [%]", 0.0)),
             "Sharpe Ratio": float(stats.get("Sharpe Ratio", 0.0)),
             "Max Drawdown [%]": float(stats.get("Max Drawdown [%]", 0.0)),
         }

    # Extract equity curve (aggregate sum across all assets for total portfolio value)
    # vbt default initial capital is 100 per asset usually, so sum is total equity
    value = pf.value()
    total_value = value.sum(axis=1) if isinstance(value, pd.DataFrame) else value

    # Convert index (Dates) to string format for JSON serialization
    equity_curve = [
        {"Date": date.strftime("%Y-%m-%d"), "Equity": float(val)}
        for date, val in total_value.items()
    ]

    return metrics, equity_curve
