from typing import Any

import polars as pl
from scipy import stats
from statsmodels.stats.multitest import multipletests


def run_stats_test(
    df: pl.DataFrame, anomaly_type: str, trade_duration: str
) -> dict[str, dict[str, Any]]:
    """Run ANOVA to test for statistical significance of the anomaly.

    Args:
        df: Polars DataFrame with returns and features.
        anomaly_type: "day_of_week" or "month_end".
        trade_duration: "daily", "intraday", or "overnight".

    Returns:
        Dictionary containing F-statistic, p-value, and corrected p-values, keyed by ticker.
    """
    if df.is_empty():
        return {}

    pdf = df.to_pandas().dropna(
        subset=["Return_Intraday", "Return_Daily", "Return_Overnight"]
    )

    if trade_duration == "daily":
        return_col = "Return_Daily"
    elif trade_duration == "intraday":
        return_col = "Return_Intraday"
    elif trade_duration == "overnight":
        return_col = "Return_Overnight"
    else:
        msg = f"Unknown trade duration: {trade_duration}"
        raise ValueError(msg)

    results_by_ticker = {}

    for code, group_df in pdf.groupby("Code"):
        results = {
            "F-Value": 0.0,
            "P-Value (Raw)": 1.0,
            "P-Value (Holm)": 1.0,
            "Significant (α=0.05)": False,
        }

        if anomaly_type == "day_of_week":
            # Group returns by DayOfWeek
            groups = [
                g[return_col].values
                for name, g in group_df.groupby("DayOfWeek")
                if len(g) > 0
            ]

            if len(groups) > 1:
                f_stat, p_val = stats.f_oneway(*groups)
                results["F-Value"] = (
                    float(f_stat) if not pl.Series([f_stat]).is_nan().item() else 0.0
                )
                results["P-Value (Raw)"] = (
                    float(p_val) if not pl.Series([p_val]).is_nan().item() else 1.0
                )

        elif anomaly_type == "month_end":
            # Group Daily returns by Is_MonthEnd
            # For month_end, we actually want to test the return of the day *after* month end against other days.
            # Create a shifted mask
            group_df["Is_After_MonthEnd"] = (
                group_df["Is_MonthEnd"].shift(1).fillna(False).astype(bool)
            )
            groups = [
                g[return_col].values
                for name, g in group_df.groupby("Is_After_MonthEnd")
                if len(g) > 0
            ]

            if len(groups) > 1:
                f_stat, p_val = stats.f_oneway(*groups)
                results["F-Value"] = (
                    float(f_stat) if not pl.Series([f_stat]).is_nan().item() else 0.0
                )
                results["P-Value (Raw)"] = (
                    float(p_val) if not pl.Series([p_val]).is_nan().item() else 1.0
                )

        results_by_ticker[code] = results

    # Apply multiple testing correction (Holm-Bonferroni) across all tickers' p-values
    tickers = list(results_by_ticker.keys())
    p_values = [results_by_ticker[t]["P-Value (Raw)"] for t in tickers]

    if p_values:
        reject, pvals_corrected, _, _ = multipletests(
            p_values, alpha=0.05, method="holm"
        )

        for i, ticker in enumerate(tickers):
            results_by_ticker[ticker]["P-Value (Holm)"] = float(pvals_corrected[i])
            results_by_ticker[ticker]["Significant (α=0.05)"] = bool(reject[i])

    return results_by_ticker
