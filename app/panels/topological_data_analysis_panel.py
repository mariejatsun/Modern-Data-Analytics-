from shiny import ui
from utils.methods import get_image_base64
from utils.layout import panel_with_banner

def topological_data_analysis_panel():
    def big_image(filename, title):
        return ui.div(
            ui.h4(title, style="text-align: center; margin-top: 30px;"),
            ui.tags.img(
                src=get_image_base64(f"www/{filename}.jpg"),
                style="width: 90%; height: auto; display: block; margin: 0 auto; margin-bottom: 40px;"
            )
        )

    return panel_with_banner(
        "Topological Data Analysis",
        ui.h3("Topological Data Analysis: Horizon 2020 vs Horizon Europe"),
        big_image("TDA2020", "Horizon 2020"),
        big_image("TDAEur", "Horizon Europe")
    )




