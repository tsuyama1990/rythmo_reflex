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
                rx.text("Target Tickers (comma separated):", font_weight="bold"),
                rx.input(
                    value=AppState.target_tickers_input,
                    on_change=AppState.update_tickers,
                    placeholder="e.g. 6599, 7713",
                    style=pixel_input,
                    width="100%"
                ),

                rx.text("Anomaly Type:", font_weight="bold", margin_top="1rem"),
                rx.select(
                    ["day_of_week", "month_end"],
                    value=AppState.target_anomaly,
                    on_change=AppState.update_anomaly,
                    style=pixel_input,
                    width="100%"
                ),

                rx.text(f"Slippage: {AppState.slippage_pct}%", font_weight="bold", margin_top="1rem"),
                rx.slider(
                    value=[AppState.slippage_pct],
                    on_change=lambda val: AppState.update_slippage(val[0]), # type: ignore
                    min=0.0,
                    max=0.5,
                    step=0.05,
                    width="100%"
                ),

                rx.vstack(
                    rx.button(
                        "Fetch Data",
                        on_click=AppState.fetch_data,
                        style=secondary_button,
                        width="100%"
                    ),
                    rx.button(
                        "START ANALYSIS",
                        on_click=AppState.run_analysis,
                        style=pixel_button,
                        width="100%"
                    ),
                    width="100%",
                    margin_top="1.5rem",
                    spacing="2",
                )
            ),
            style=pixel_box,
            width="100%"
        ),

        rx.box(
            rx.vstack(
                rx.text("Status Info", font_weight="bold"),
                rx.text(f"Available Dates: {AppState.available_dates[0]} to {AppState.available_dates[1]}"),
            ),
            style=pixel_box,
            width="100%",
            margin_top="1rem"
        ),

        width="100%",
        max_width="400px",
        padding="1rem"
    )
