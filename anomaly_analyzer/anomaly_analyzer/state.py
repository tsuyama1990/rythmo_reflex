import logging
from typing import Any

import reflex as rx

# Import core modules
from .core.api_client import JQuantsAPIClient
from .core.backtest import run_backtest
from .core.db import load_quotes, save_quotes
from .core.etl import process_quotes
from .core.stats import run_stats_test

logger = logging.getLogger(__name__)

class AppState(rx.State):
    """Global state for the Anomaly Analyzer application."""

    is_loading: bool = False
    error_message: str = ""

    target_tickers_input: str = "6599, 7713"
    target_tickers: list[str] = ["6599", "7713"]

    slippage_pct: float = 0.1
    target_anomaly: str = "day_of_week"  # "day_of_week" or "month_end"

    available_dates: tuple[str, str] = ("", "")

    backtest_results: dict[str, Any] = {}
    chart_data: list[dict[str, Any]] = []
    stats_results: dict[str, Any] = {}

    def update_tickers(self, value: str) -> None:
        self.target_tickers_input = value
        self.target_tickers = [t.strip() for t in value.split(",") if t.strip()]

    def update_slippage(self, value: float) -> None:
        self.slippage_pct = float(value)

    def update_anomaly(self, value: str) -> None:
        self.target_anomaly = value

    def clear_error(self) -> None:
        self.error_message = ""

    @rx.background  # type: ignore
    async def fetch_data(self) -> None:
        """Fetch data from J-Quants API and save to local parquet."""
        async with self:
            self.is_loading = True
            self.error_message = ""
            tickers = self.target_tickers

        client = JQuantsAPIClient()

        try:
            for ticker in tickers:
                logger.info(f"Fetching data for {ticker}...")
                quotes = await client.fetch_daily_quotes(ticker)

                if quotes:
                    # Process and save
                    df = process_quotes(quotes)
                    save_quotes(df)
                    logger.info(f"Saved {len(quotes)} records for {ticker}.")
                else:
                    logger.warning(f"No data returned for {ticker}.")

            async with self:
                # Update available dates
                df_all = load_quotes(tickers)
                if not df_all.is_empty():
                    min_date = df_all.select("Date").min().item()
                    max_date = df_all.select("Date").max().item()

                    if min_date and max_date:
                        self.available_dates = (min_date.strftime("%Y-%m-%d"), max_date.strftime("%Y-%m-%d"))

        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            async with self:
                self.error_message = f"Failed to fetch data: {e!s}"
        finally:
            await client.close()
            async with self:
                self.is_loading = False

    @rx.background  # type: ignore
    async def run_analysis(self) -> None:
        """Run backtest and stats tests on local data."""
        async with self:
            self.is_loading = True
            self.error_message = ""
            tickers = self.target_tickers
            anomaly = self.target_anomaly
            slippage = self.slippage_pct

        try:
            # Load and process data
            df = load_quotes(tickers)
            if df.is_empty():
                raise ValueError("No data available for the selected tickers. Please fetch data first.")

            # Run Backtest
            bt_metrics, bt_chart = run_backtest(df, anomaly, slippage)

            # Run Stats
            st_metrics = run_stats_test(df, anomaly)

            async with self:
                self.backtest_results = bt_metrics
                self.chart_data = bt_chart
                self.stats_results = st_metrics

                # Update available dates
                min_date = df.select("Date").min().item()
                max_date = df.select("Date").max().item()
                if min_date and max_date:
                    self.available_dates = (min_date.strftime("%Y-%m-%d"), max_date.strftime("%Y-%m-%d"))

        except Exception as e:
            logger.error(f"Error running analysis: {e}")
            async with self:
                self.error_message = f"Analysis failed: {e!s}"
        finally:
            async with self:
                self.is_loading = False
