import reflex as rx

from anomaly_analyzer.state import AppState
from anomaly_analyzer.style import pixel_box


def render_equity_chart() -> rx.Component:
    """Renders the equity curve chart."""
    # We use selected_tickers to generate the lines dynamically
    lines = rx.foreach(
        AppState.selected_tickers,
        lambda ticker: rx.recharts.line(
            data_key=ticker, stroke_width=2, dot=False, active_dot=True
        ),
    )

    return rx.box(
        rx.cond(
            AppState.chart_data.length() > 0,  # type: ignore
            rx.recharts.line_chart(
                lines,
                rx.recharts.x_axis(data_key="Date"),
                rx.recharts.y_axis(domain=["auto", "auto"]),
                rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                rx.recharts.graphing_tooltip(),
                rx.recharts.legend(),
                data=AppState.chart_data,
                width="100%",
                height=400,
            ),
            rx.center(
                rx.text("No chart data available. Run analysis first."), height="400px"
            ),
        ),
        style=pixel_box,
        width="100%",
    )
