from shiny import ui
from utils.methods import get_image_base64

def introduction_panel():
    return ui.nav_panel(
        "Introduction",
        ui.div(
            {"style": "display: flex; justify-content: space-around; margin-top: 30px;"},
            *[
                ui.div(
                    ui.tags.img(
                        src=get_image_base64(f"www/{naam}.jpg"),
                        style="width: 150px; height: auto; border-radius: 50%;"
                    ),
                    ui.p(naam, style="text-align: center; font-weight: bold;"),
                    ui.p(opleiding, style="text-align: center; font-size: 14px;")
                )
                for naam, opleiding in [
                    ("Sebastian", "2nd master civil engineering"),
                    ("Marie", "2nd master bio-engineering"),
                    ("Lin", "2nd master bio-engineering"),
                    ("Jana", "2nd master bio-engineering"),
                ]
            ]
        ),
        ui.hr(),
        ui.div(
            ui.p(
                "Welcome to our Horizon analysis web app. This web application presents an interactive analysis of EU-funded"
                "research projects under the Horizon 2020 and Horizon Europe programmes. By comparing data from both initiatives,"
                "this platform highlights evolving research priorities, funding distribution, international collaborations and scientific impact."
                "Use the navigation tabs above to explore the data through dynamic visualisations."
            ),
            style="margin: 30px auto; max-width: 700px; text-align: center; font-size: 15px;"
        )
    )