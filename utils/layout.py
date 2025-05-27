from shiny import ui
from utils.methods import get_image_base64

def banner():
    return ui.div(
        ui.tags.img(
            src=get_image_base64("www/banner3.jpg"),
            style="max-width: 40%; height: auto;"
        ),
        style="text-align: center; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #ccc;"
    )

def panel_with_banner(title, *components):
    return ui.nav_panel(
        title,
        banner(),
        *components
    )
