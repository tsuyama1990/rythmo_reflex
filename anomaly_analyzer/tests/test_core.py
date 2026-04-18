from datetime import datetime

import polars as pl

from anomaly_analyzer.core.backtest import run_backtest
from anomaly_analyzer.core.etl import process_quotes
from anomaly_analyzer.core.stats import run_stats_test


def test_process_quotes_empty() -> None:
    df = process_quotes([])
    assert df.is_empty()

def test_process_quotes_valid() -> None:
    data = [
        {"Date": "2023-01-01", "Code": "1111", "Open": 100.0, "High": 110.0, "Low": 90.0, "Close": 105.0, "Volume": 1000},
        {"Date": "2023-01-02", "Code": "1111", "Open": 105.0, "High": 115.0, "Low": 100.0, "Close": 110.0, "Volume": 1200},
        {"Date": "2023-01-03", "Code": "1111", "Open": 110.0, "High": 120.0, "Low": 105.0, "Close": 115.0, "Volume": 1500},
    ]
    df = process_quotes(data)

    assert not df.is_empty()
    assert "Return_Daily" in df.columns
    assert "Return_Intraday" in df.columns
    assert "Return_Overnight" in df.columns
    assert "DayOfWeek" in df.columns
    assert "Is_MonthEnd" in df.columns

    # Check returns for 2023-01-02
    row = df.filter(pl.col("Date") == datetime(2023, 1, 2)).to_dicts()[0]
    assert abs(row["Return_Daily"] - ((110.0 - 105.0) / 105.0)) < 1e-6
    assert abs(row["Return_Intraday"] - ((110.0 - 105.0) / 105.0)) < 1e-6
    assert abs(row["Return_Overnight"] - ((105.0 - 105.0) / 105.0)) < 1e-6

def test_run_backtest() -> None:
    # Construct a dummy DataFrame
    df = pl.DataFrame({
        "Date": [datetime(2023, 1, 1), datetime(2023, 1, 2), datetime(2023, 1, 3)],
        "Code": ["1111", "1111", "1111"],
        "Open": [100.0, 105.0, 110.0],
        "Close": [105.0, 110.0, 115.0],
        "DayOfWeek": [1, 2, 3],
        "Is_MonthEnd": [False, False, True]
    })

    metrics, curve = run_backtest(df, "day_of_week", 0.0)
    assert isinstance(metrics, dict)
    assert isinstance(curve, list)

def test_run_stats_test() -> None:
    df = pl.DataFrame({
        "Date": [datetime(2023, 1, 1), datetime(2023, 1, 2), datetime(2023, 1, 3), datetime(2023, 1, 4)],
        "Code": ["1111", "1111", "1111", "1111"],
        "Return_Intraday": [0.01, -0.02, 0.03, -0.01],
        "Return_Daily": [0.01, -0.02, 0.03, -0.01],
        "DayOfWeek": [1, 2, 1, 2],
        "Is_MonthEnd": [False, False, True, False]
    })

    res = run_stats_test(df, "day_of_week")
    assert isinstance(res, dict)
    # The groups will be small, so we just check it doesn't crash and returns expected keys
    if res:
        assert "F-Value" in res
        assert "P-Value (Raw)" in res
