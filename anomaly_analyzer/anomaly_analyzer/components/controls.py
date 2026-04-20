import reflex as rx

from anomaly_analyzer.state import AppState
from anomaly_analyzer.style import (
    pixel_box,
    pixel_button,
    pixel_input,
    secondary_button,
)


def sidebar_controls() -> rx.Component:
    """Sidebar component containing controls."""
    return rx.vstack(
        rx.heading("Japan Stock Anomaly Analyzer", size="7", margin_bottom="1rem"),
        rx.box(
            rx.vstack(
                rx.text("Add Tickers:", font_weight="bold"),
                rx.hstack(
                    rx.input(
                        value=AppState.target_tickers_input,
                        on_change=AppState.update_tickers,
                        placeholder="e.g. 6599, 7713",
                        style=pixel_input,
                        width="70%",
                    ),
                    rx.button(
                        "Fetch",
                        on_click=AppState.fetch_data,
                        style=secondary_button,
                        width="30%",
                    ),
                    width="100%",
                ),
                rx.text("Target Tickers:", font_weight="bold", margin_top="1rem"),
                rx.cond(
                    AppState.search_history.length() > 0,  # type: ignore
                    rx.vstack(
                        rx.foreach(
                            AppState.search_history,
                            lambda t: rx.checkbox(
                                t,
                                checked=AppState.selected_tickers.contains(t),  # type: ignore
                                on_change=lambda checked: AppState.toggle_ticker(
                                    t, checked
                                ),  # type: ignore
                            ),
                        ),
                        spacing="2",
                        align_items="start",
                    ),
                    rx.text(
                        "No tickers fetched yet.", font_size="0.8rem", color="gray"
                    ),
                ),
                rx.text("Anomaly Type:", font_weight="bold", margin_top="1rem"),
                rx.select(
                    ["day_of_week", "month_end"],
                    value=AppState.target_anomaly,
                    on_change=AppState.update_anomaly,
                    style=pixel_input,
                    width="100%",
                ),
                rx.text("Trade Duration:", font_weight="bold", margin_top="1rem"),
                rx.select(
                    ["daily", "intraday", "overnight"],
                    value=AppState.trade_duration,
                    on_change=AppState.update_trade_duration,
                    style=pixel_input,
                    width="100%",
                ),
                rx.text(
                    f"Slippage: {AppState.slippage_pct}%",
                    font_weight="bold",
                    margin_top="1rem",
                ),
                rx.slider(
                    value=[AppState.slippage_pct],
                    on_change=lambda val: AppState.update_slippage(val[0]),  # type: ignore
                    min=0.0,
                    max=0.5,
                    step=0.05,
                    width="100%",
                ),
                rx.vstack(
                    rx.button(
                        "START ANALYSIS",
                        on_click=AppState.run_analysis,
                        style=pixel_button,
                        width="100%",
                    ),
                    width="100%",
                    margin_top="1.5rem",
                    spacing="2",
                ),
            ),
            style=pixel_box,
            width="100%",
        ),
        rx.box(
            rx.vstack(
                rx.text("Status Info", font_weight="bold"),
                rx.text(
                    f"Available Dates: {AppState.available_dates[0]} to {AppState.available_dates[1]}"
                ),
            ),
            style=pixel_box,
            width="100%",
            margin_top="1rem",
        ),
        width="100%",
        max_width="400px",
        padding="1rem",
    )
