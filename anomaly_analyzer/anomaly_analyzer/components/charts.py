import reflex as rx
from ..state import AppState
from ..style import pixel_box
from typing import List, Dict, Any

def render_equity_chart() -> rx.Component:
    """Renders the equity curve chart."""

    return rx.box(
         rx.cond(
             len(AppState.chart_data) > 0,
             rx.recharts.line_chart(
                rx.recharts.line(
                    data_key="Equity",
                    stroke="#ff007f",
                    stroke_width=3,
                    dot=False,
                    active_dot=True
                ),
                rx.recharts.x_axis(data_key="Date"),
                rx.recharts.y_axis(domain=['auto', 'auto']),
                rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                rx.recharts.graphing_tooltip(),
                data=AppState.chart_data,
                width="100%",
                height=400,
            ),
            rx.center(
                rx.text("No chart data available. Run analysis first."),
                height="400px"
            )
         ),
         style=pixel_box,
         width="100%",
    )
