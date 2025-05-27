from shiny import ui
from utils.methods import get_image_base64
from utils.layout import panel_with_banner

def topological_data_analysis_panel():
    def image_block(filename, caption):
        return ui.div(
            ui.tags.img(
                src=get_image_base64(f"www/{filename}.jpg"),
                style="width: 200px; height: auto; display: block; margin: 0 auto;"
            ),
            ui.p(caption, style="font-size: 0.85em; font-style: italic; text-align: center; margin-top: 8px;"),
            style="text-align: center;"
        )

    def legend_img(filename):
        return ui.div(
            ui.tags.img(
                src=get_image_base64(f"www/{filename}.jpg"),
                style="width: 200px; height: auto; display: block; margin: auto;"
            )
        )

    captions = {
        "a": "A) Collaborations coloured by K-means clusters",
        "b": "B) k-NN links (k=5) coloured by K-means clusters",
        "c": "C) Collaborations coloured by dominant project category",
        "d": "D) k-NN links coloured by dominant project category"
    }

    def image_row(prefix):
        return ui.div(
            # Links: grotere legenda 1
            legend_img("Legende1"),

            # Midden: TDA afbeeldingen
            ui.div(
                *[image_block(f"{prefix}{l}", captions[l]) for l in "abcd"],
                style="display: flex; justify-content: center; flex-wrap: wrap; gap: 25px; flex: 1;"
            ),

            # Rechts: grotere legenda 2
            legend_img("Legende2"),

            style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 50px;"
        )

    return panel_with_banner(
        "Topological Data Analysis",
        ui.h3("Topological Data Analysis: Horizon 2020 vs Horizon Europe"),
        ui.h4("Horizon 2020"),
        image_row("TDA2020"),
        ui.h4("Horizon Europe", style="margin-top: 40px;"),
        image_row("TDAeuro")
    )




