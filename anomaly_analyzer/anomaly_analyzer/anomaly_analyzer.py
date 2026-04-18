import reflex as rx
from .pages.index import index
from .style import STYLESHEETS, base_style

# Initialize the app with the custom stylesheets and base theme
app = rx.App(
    stylesheets=STYLESHEETS,
    style=base_style, # type: ignore
    theme=rx.theme(
        has_background=True,
        radius="none",
        accent_color="blue",
    )
)

app.add_page(index, title="Japan Stock Anomaly Analyzer")
