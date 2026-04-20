from typing import Any

import polars as pl
import pytest

from anomaly_analyzer.core.backtest import run_backtest
from anomaly_analyzer.core.etl import process_quotes
from anomaly_analyzer.core.stats import run_stats_test


@pytest.fixture  # type: ignore
def sample_quotes() -> list[dict[str, Any]]:
    return [
        {
            "Date": "2023-01-01",
            "Code": "72030",
            "Open": 100,
            "High": 105,
            "Low": 95,
            "Close": 102,
            "Volume": 1000,
        },
        {
            "Date": "2023-01-02",
            "Code": "72030",
            "Open": 102,
            "High": 110,
            "Low": 100,
            "Close": 108,
            "Volume": 1200,
        },
        {
            "Date": "2023-01-03",
            "Code": "72030",
            "Open": 108,
            "High": 109,
            "Low": 105,
            "Close": 106,
            "Volume": 1100,
        },
        {
            "Date": "2023-01-04",
            "Code": "72030",
            "Open": 106,
            "High": 112,
            "Low": 104,
            "Close": 110,
            "Volume": 1500,
        },
    ]


def test_process_quotes_empty() -> None:
    df = process_quotes([])
    assert df.is_empty()


def test_process_quotes_calculates_returns(sample_quotes: list[dict[str, Any]]) -> None:
    df = process_quotes(sample_quotes)

    # Check that returns are calculated correctly
    assert "Return_Daily" in df.columns
    assert "Return_Intraday" in df.columns
    assert "Return_Overnight" in df.columns

    # Check forward fill and shift logic (first row should be dropped due to nulls)
    assert len(df) == 3

    # Check specific calculation for 2023-01-02
    row = df.filter(pl.col("Date") == pl.datetime(2023, 1, 2).cast(pl.Date)).to_dicts()[
        0
    ]
    assert row["Return_Intraday"] == pytest.approx((108 - 102) / 102)
    assert row["Return_Daily"] == pytest.approx((108 - 102) / 102)
    assert row["Return_Overnight"] == pytest.approx((102 - 102) / 102)


def test_run_backtest_empty() -> None:
    metrics, chart = run_backtest(pl.DataFrame(), "day_of_week", "daily", 0.0)
    assert metrics == {}
    assert chart == []


def test_run_backtest_logic(sample_quotes: list[dict[str, Any]]) -> None:
    df = process_quotes(sample_quotes)
    metrics, chart = run_backtest(df, "day_of_week", "intraday", 0.1)

    # 2023-01-02 is a Monday (1), 01-03 is Tuesday (2).
    # Trade_Return should be applied on Tuesday
    assert isinstance(metrics, dict)
    assert "72030" in metrics
    assert "Win Rate [%]" in metrics["72030"]
    assert len(chart) == 3


def test_run_stats_test_empty() -> None:
    res = run_stats_test(pl.DataFrame(), "day_of_week", "daily")
    assert res == {}


def test_run_stats_test_logic(sample_quotes: list[dict[str, Any]]) -> None:
    df = process_quotes(sample_quotes)
    res = run_stats_test(df, "day_of_week", "intraday")

    assert "72030" in res
    assert "F-Value" in res["72030"]
    assert "P-Value (Raw)" in res["72030"]
    assert "P-Value (Holm)" in res["72030"]
