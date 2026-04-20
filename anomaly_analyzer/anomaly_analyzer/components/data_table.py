from typing import Any

import reflex as rx

from anomaly_analyzer.state import AppState
from anomaly_analyzer.style import pixel_box


def _render_backtest_row(ticker_and_metrics: list[Any]) -> rx.Component:
    ticker = ticker_and_metrics[0]
    metrics = ticker_and_metrics[1]
    return rx.table.row(
        rx.table.cell(ticker),
        rx.table.cell(metrics["Win Rate [%]"].to_string() + " %"),
        rx.table.cell(metrics["Profit Factor"].to_string()),
        rx.table.cell(metrics["Sharpe Ratio"].to_string()),
        rx.table.cell(metrics["Total Return [%]"].to_string() + " %"),
        rx.table.cell(metrics["Max Drawdown [%]"].to_string() + " %"),
    )


def _render_stats_row(ticker_and_metrics: list[Any]) -> rx.Component:
    ticker = ticker_and_metrics[0]
    metrics = ticker_and_metrics[1]
    return rx.table.row(
        rx.table.cell(ticker),
        rx.table.cell(metrics["F-Value"].to_string()),
        rx.table.cell(metrics["P-Value (Raw)"].to_string()),
        rx.table.cell(metrics["P-Value (Holm)"].to_string()),
        rx.table.cell(metrics["Significant (α=0.05)"].to_string()),
    )


def render_results_tables() -> rx.Component:
    """Render Backtest and Stats results."""
    return rx.vstack(
        # Backtest Results
        rx.box(
            rx.heading("Backtest Results", size="5", margin_bottom="1rem"),
            rx.cond(
                AppState.backtest_results,
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Ticker"),
                            rx.table.column_header_cell("Win Rate"),
                            rx.table.column_header_cell("Profit Factor"),
                            rx.table.column_header_cell("Sharpe Ratio"),
                            rx.table.column_header_cell("Total Return"),
                            rx.table.column_header_cell("Max Drawdown"),
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(
                            AppState.backtest_results.items(),
                            _render_backtest_row,
                        )
                    ),
                ),
                rx.text("No results yet."),
            ),
            style=pixel_box,
            width="100%",
            overflow_x="auto",
        ),
        # Stats Results
        rx.box(
            rx.heading("Statistical Significance", size="5", margin_bottom="1rem"),
            rx.cond(
                AppState.stats_results,
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Ticker"),
                            rx.table.column_header_cell("F-Value"),
                            rx.table.column_header_cell("P-Value (Raw)"),
                            rx.table.column_header_cell("P-Value (Holm)"),
                            rx.table.column_header_cell("Significant (α=0.05)"),
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(
                            AppState.stats_results.items(),
                            _render_stats_row,
                        )
                    ),
                ),
                rx.text("No stats available."),
            ),
            style=pixel_box,
            width="100%",
            overflow_x="auto",
        ),
        width="100%",
    )
