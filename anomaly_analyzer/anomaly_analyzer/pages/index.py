import reflex as rx

from anomaly_analyzer.components.charts import render_equity_chart
from anomaly_analyzer.components.controls import sidebar_controls
from anomaly_analyzer.components.data_table import render_results_tables
from anomaly_analyzer.state import AppState
from anomaly_analyzer.style import error_callout


def index() -> rx.Component:
    return rx.container(
        rx.hstack(
            sidebar_controls(),

            rx.vstack(
                # Error Message
                rx.cond(
                    AppState.error_message != "",
                    rx.box(
                        rx.hstack(
                            rx.text(AppState.error_message),
                            rx.button("X", on_click=AppState.clear_error, bg="transparent", color="red")
                        ),
                        style=error_callout,
                        width="100%"
                    ),
                    rx.box()
                ),

                # Loading indicator
                rx.cond(
                    AppState.is_loading,
                    rx.center(
                        rx.spinner(size="3", color="red"),
                        rx.text(" Processing... Please wait.", font_weight="bold", margin_left="1rem"),
                        width="100%",
                        padding="2rem",
                    ),
                    rx.box()
                ),

                # Main content (Chart and Tables)
                render_equity_chart(),
                render_results_tables(),

                width="100%",
                padding="1rem"
            ),
            align_items="flex-start",
            width="100%"
        ),
        size="4",
        padding_y="2rem"
    )
