"""Pixel art style definitions for the application."""

# Global fonts can be injected via rx.App(stylesheets=[...]) in main.py
STYLESHEETS = [
    "https://fonts.googleapis.com/css2?family=DotGothic16&display=swap",
]

# Base colors
COLORS = {
    "bg": "#f0f0f0",
    "primary": "#4a90e2", # Bright blue
    "secondary": "#f8e71c", # Pastel yellow
    "accent1": "#ff007f", # Vivid pink
    "accent2": "#7ed321", # Vivid green
    "text": "#000000",
    "border": "#000000",
    "error_bg": "#ffcccc",
}

# Common style dictionaries
pixel_box = {
    "border": f"4px solid {COLORS['border']}",
    "box_shadow": f"4px 4px 0px 0px {COLORS['border']}",
    "background_color": "white",
    "padding": "1rem",
    "margin": "0.5rem",
    "border_radius": "0px", # Force sharp corners for pixel look
}

pixel_button = {
    **pixel_box,
    "background_color": COLORS["primary"],
    "color": "white",
    "font_weight": "bold",
    "font_family": "'DotGothic16', sans-serif",
    "cursor": "pointer",
    "_hover": {
        "background_color": COLORS["accent1"],
        "transform": "translate(2px, 2px)",
        "box_shadow": f"2px 2px 0px 0px {COLORS['border']}",
    },
    "_active": {
         "transform": "translate(4px, 4px)",
         "box_shadow": "none",
    }
}

secondary_button = {
    **pixel_button,
    "background_color": COLORS["secondary"],
    "color": COLORS["text"],
    "_hover": {
        "background_color": COLORS["accent2"],
        "transform": "translate(2px, 2px)",
        "box_shadow": f"2px 2px 0px 0px {COLORS['border']}",
    }
}

pixel_input = {
    "border": f"4px solid {COLORS['border']}",
    "padding": "0.5rem",
    "font_family": "'DotGothic16', sans-serif",
    "border_radius": "0px",
    "background_color": "white",
    "color": "black",
    "outline": "none",
    "_placeholder": {
        "color": "#444444",
    },
    "_focus": {
        "border_color": COLORS["accent1"]
    }
}

error_callout = {
    **pixel_box,
    "background_color": COLORS["error_bg"],
    "color": "red",
    "font_weight": "bold",
}

base_style = {
    "font_family": "'DotGothic16', sans-serif",
    "background_color": COLORS["bg"],
    "color": COLORS["text"],
}
