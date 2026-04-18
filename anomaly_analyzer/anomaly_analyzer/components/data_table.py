import reflex as rx

from anomaly_analyzer.state import AppState
from anomaly_analyzer.style import pixel_box


def render_results_tables() -> rx.Component:
    """Render Backtest and Stats results."""

    return rx.vstack(
        # Backtest Results
        rx.box(
            rx.heading("Backtest Results", size="5", margin_bottom="1rem"),
            rx.cond(
                AppState.backtest_results,
                rx.vstack(
                    rx.hstack(rx.text("Win Rate:", font_weight="bold"), rx.text(AppState.backtest_results["Win Rate [%]"].to_string() + " %")),
                    rx.hstack(rx.text("Profit Factor:", font_weight="bold"), rx.text(AppState.backtest_results["Profit Factor"].to_string())),
                    rx.hstack(rx.text("Total Return:", font_weight="bold"), rx.text(AppState.backtest_results["Total Return [%]"].to_string() + " %")),
                    rx.hstack(rx.text("Sharpe Ratio:", font_weight="bold"), rx.text(AppState.backtest_results["Sharpe Ratio"].to_string())),
                    rx.hstack(rx.text("Max Drawdown:", font_weight="bold"), rx.text(AppState.backtest_results["Max Drawdown [%]"].to_string() + " %")),
                    align_items="start"
                ),
                rx.text("No results yet.")
            ),
            style=pixel_box,
            width="100%"
        ),

        # Stats Results
        rx.box(
            rx.heading("Statistical Significance", size="5", margin_bottom="1rem"),
            rx.cond(
                AppState.stats_results,
                rx.vstack(
                    rx.hstack(rx.text("F-Value:", font_weight="bold"), rx.text(AppState.stats_results["F-Value"].to_string())),
                    rx.hstack(rx.text("P-Value (Raw):", font_weight="bold"), rx.text(AppState.stats_results["P-Value (Raw)"].to_string())),
                    rx.hstack(rx.text("P-Value (Holm Corrected):", font_weight="bold"), rx.text(AppState.stats_results["P-Value (Holm)"].to_string())),
                    rx.hstack(rx.text("Significant (α=0.05):", font_weight="bold"), rx.text(AppState.stats_results["Significant (α=0.05)"].to_string())),
                    align_items="start"
                ),
                rx.text("No stats available.")
            ),
            style=pixel_box,
            width="100%"
        ),
        width="100%"
    )
