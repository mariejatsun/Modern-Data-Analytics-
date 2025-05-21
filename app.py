from shiny import App, render, ui
import pandas as pd
import plotly.express as px
import seaborn as sns
import numpy as np
from shinywidgets import render_widget, output_widget
import base64
import pycountry

#data inladen 
category_per_year = pd.read_csv("category_per_year")
category_per_year['Year'] = category_per_year['Year'].astype(int)
category_per_year['project_count'] = category_per_year['project_count'].astype(int)
categories = sorted(category_per_year['category'].dropna().unique())

merged_funding = pd.read_csv("merged_funding.csv")

# voor landencodes
def convert_iso2_to_iso3(iso2_code):
    try:
        return pycountry.countries.get(alpha_2=iso2_code).alpha_3
    except:
        return None

#afbeelding
def get_image_base64(path):
    with open(path, "rb") as f: 
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/jpg;base64,{encoded}"  # of png

# UI
app_ui = ui.page_fluid(
    ui.tags.img(
        src=get_image_base64("www/banner3.jpg"),
        style="width: auto; height: auto; max-width: 50%; display: block; margin: auto;"
    ),
    ui.navset_tab(
        ui.nav_panel(
            "Amount of projects over time",
            ui.input_select("category", "Select a category",
                            {cat: cat for cat in categories},
                            selected="engineering and technology"),
            ui.output_ui("category_plot")
        ),
        ui.nav_panel(
            "Funding levels map",
            ui.input_radio_buttons("map_year", "Select Horizon programme", 
                                   ["Horizon 2020", "Horizon Europe"], 
                                   selected="Horizon 2020"),
            ui.output_ui("funding_map")
        )
    )
)

# Server 
def server(input, output, session):
    @output
    @render.ui
    def category_plot():
        selected_cat = input.category()
        data = category_per_year[category_per_year['category'] == selected_cat]
        fig = px.line(
            data,
            x='Year',
            y='project_count',
            markers=True,
            title=f'{selected_cat.capitalize()} Projects Over Time',
            labels={'project_count': 'Aantal projecten'}
        )
        fig.update_layout(height=500, margin={"r": 0, "t": 50, "l": 0, "b": 0})
        return ui.HTML(fig.to_html(include_plotlyjs='cdn'))

    @output
    @render.ui
    def funding_map():
        year = input.map_year()
        col = 'ecContribution_2020' if year == 'Horizon 2020' else 'ecContribution_2024'

        data = merged_funding
        data["iso_alpha"] = data["country"].apply(convert_iso2_to_iso3)
        fig = px.scatter_geo(
            data,
            locations="iso_alpha",
            locationmode="ISO-3",
            size=col,
            hover_name="country",
            projection="natural earth",
            title=f"Funding Levels in {year}",
            size_max=50
        )
        fig.update_geos(showcountries=True, countrycolor="LightGray", showcoastlines=True, coastlinecolor="LightGray")
        fig.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0}, height=600)

        return ui.HTML(fig.to_html(include_plotlyjs='cdn'))
    


# App maken
app = App(app_ui, server)
