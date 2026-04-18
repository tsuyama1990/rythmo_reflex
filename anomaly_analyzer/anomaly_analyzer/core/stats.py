from typing import Any

import polars as pl
from scipy import stats
from statsmodels.stats.multitest import multipletests


def run_stats_test(df: pl.DataFrame, anomaly_type: str) -> dict[str, Any]:
    """Run ANOVA to test for statistical significance of the anomaly.

    Args:
        df: Polars DataFrame with returns and features.
        anomaly_type: "day_of_week" or "month_end".

    Returns:
        Dictionary containing F-statistic, p-value, and corrected p-values.
    """
    if df.is_empty():
        return {}

    pdf = df.to_pandas().dropna(subset=["Return_Intraday", "Return_Daily"])

    results = {}

    if anomaly_type == "day_of_week":
        # Group Intraday returns by DayOfWeek
        groups = [group["Return_Intraday"].values for name, group in pdf.groupby("DayOfWeek") if len(group) > 0]

        if len(groups) > 1:
            f_stat, p_val = stats.f_oneway(*groups)
            results["F-Value"] = float(f_stat)
            results["P-Value (Raw)"] = float(p_val)

            # Since we're just testing the days against each other,
            # if we were to do multiple comparisons (e.g., across many stocks),
            # we'd use multipletests. Here we just demonstrate its usage on one p-val.
            reject, pvals_corrected, _, _ = multipletests([p_val], alpha=0.05, method='holm')
            results["P-Value (Holm)"] = float(pvals_corrected[0])
            results["Significant (α=0.05)"] = bool(reject[0])

    elif anomaly_type == "month_end":
        # Group Daily returns by Is_MonthEnd
        groups = [group["Return_Daily"].values for name, group in pdf.groupby("Is_MonthEnd") if len(group) > 0]

        if len(groups) > 1:
            f_stat, p_val = stats.f_oneway(*groups)
            results["F-Value"] = float(f_stat)
            results["P-Value (Raw)"] = float(p_val)

            reject, pvals_corrected, _, _ = multipletests([p_val], alpha=0.05, method='holm')
            results["P-Value (Holm)"] = float(pvals_corrected[0])
            results["Significant (α=0.05)"] = bool(reject[0])

    return results
