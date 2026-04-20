from typing import Any

import numpy as np
import polars as pl


def run_backtest(
    df: pl.DataFrame, anomaly_type: str, trade_duration: str, slippage_pct: float
) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    """Run backtest based on anomaly signals using manual calculations for multiple tickers.

    Args:
        df: Polars DataFrame with processed quotes and features.
        anomaly_type: Type of anomaly ("day_of_week" or "month_end").
        trade_duration: Duration of the trade ("daily", "intraday", "overnight").
        slippage_pct: Slippage in percentage (e.g., 0.1 for 0.1%).

    Returns:
        Tuple of (metrics_dict_by_ticker, equity_curve_list)
        metrics_dict_by_ticker is keyed by ticker code.
    """
    if df.is_empty():
        return {}, []

    # Convert to pandas for easier manipulation of time series
    pdf = df.to_pandas()
    pdf = pdf.sort_values(["Code", "Date"])

    # Determine which return column to use based on trade_duration
    if trade_duration == "daily":
        return_col = "Return_Daily"
    elif trade_duration == "intraday":
        return_col = "Return_Intraday"
    elif trade_duration == "overnight":
        return_col = "Return_Overnight"
    else:
        msg = f"Unknown trade duration: {trade_duration}"
        raise ValueError(msg)

    # Calculate trade returns based on anomaly
    pdf["Trade_Return"] = 0.0
    # Apply slippage (twice: once for entry, once for exit)
    slippage = (slippage_pct / 100.0) * 2

    if anomaly_type == "day_of_week":
        # E.g. Buy Tuesday Open, Sell Tuesday Close (if intraday), or Tuesday Close to Wed Close (daily)
        # We will apply the selected return on Tuesday (DayOfWeek == 2)
        mask = pdf["DayOfWeek"] == 2
        pdf.loc[mask, "Trade_Return"] = pdf.loc[mask, return_col] - slippage

    elif anomaly_type == "month_end":
        # The anomaly usually triggers at the end of the month.
        # If trade_duration is "daily", we buy at Month End Close, sell next day Close.
        # If trade_duration is "intraday", we buy next day Open, sell next day Close.
        # If trade_duration is "overnight", we buy at Month End Close, sell next day Open.
        # In all cases, the return is realized on the day AFTER Month End.
        is_after_month_end = (
            pdf.groupby("Code")["Is_MonthEnd"].shift(1).fillna(False).astype(bool)
        )
        pdf.loc[is_after_month_end, "Trade_Return"] = (
            pdf.loc[is_after_month_end, return_col] - slippage
        )
    else:
        msg = f"Unknown anomaly type: {anomaly_type}"
        raise ValueError(msg)

    metrics_by_ticker = {}

    # Initialize Equity column
    pdf["Equity"] = 100.0

    # Calculate metrics per ticker
    for code, group in pdf.groupby("Code"):
        # Only consider days where trades actually happened (non-zero returns)
        active_returns = group["Trade_Return"][group["Trade_Return"] != 0]

        # Calculate Equity Curve for this ticker
        # Using compounding: (1 + r).cumprod()
        # For dates with no trades, return is 0, so equity stays same.
        equity_series = (1 + group["Trade_Return"]).cumprod() * 100
        pdf.loc[group.index, "Equity"] = equity_series

        if len(active_returns) > 0:
            win_rate = (active_returns > 0).mean() * 100
            total_return = equity_series.iloc[-1] - 100.0

            pos_returns = active_returns[active_returns > 0].sum()
            neg_returns = abs(active_returns[active_returns < 0].sum())
            profit_factor = (
                pos_returns / neg_returns if neg_returns > 0 else float("inf")
            )

            sharpe = (
                (active_returns.mean() / active_returns.std() * np.sqrt(252))
                if active_returns.std() > 0
                else 0.0
            )

            # Max Drawdown
            rolling_max = equity_series.cummax()
            drawdown = (equity_series - rolling_max) / rolling_max
            max_drawdown = drawdown.min() * 100
        else:
            win_rate = 0.0
            total_return = 0.0
            profit_factor = 0.0
            sharpe = 0.0
            max_drawdown = 0.0

        metrics_by_ticker[code] = {
            "Win Rate [%]": float(win_rate),
            "Profit Factor": float(profit_factor),
            "Total Return [%]": float(total_return),
            "Sharpe Ratio": float(sharpe),
            "Max Drawdown [%]": float(max_drawdown),
        }

    # Calculate Multi-line Equity Curve Chart Data
    # 1. Pivot equity values: Rows=Date, Cols=Code
    # Fill NA with 100 as the starting base, then forward fill in case some tickers start later or end earlier.

    # Create a DataFrame with Date and Equity for each ticker
    equity_df = pdf.pivot(index="Date", columns="Code", values="Equity")

    # Forward fill to maintain equity value on non-trading days
    equity_df = equity_df.ffill()

    # Fill remaining NaNs (before first trade) with 100.0
    equity_df = equity_df.fillna(100.0)

    # Convert to list of dicts for Reflex chart
    # [{"Date": "2023-01-01", "6599": 100, "7713": 100}, ...]
    equity_curve: list[dict[str, Any]] = []
    for date, row in equity_df.iterrows():
        # Ensure date is properly formatted as a string
        date_str = date.strftime("%Y-%m-%d") if hasattr(date, "strftime") else str(date)
        point: dict[str, Any] = {"Date": date_str}
        for code_val, val in row.items():
            point[str(code_val)] = float(val)
        equity_curve.append(point)

    return metrics_by_ticker, equity_curve
