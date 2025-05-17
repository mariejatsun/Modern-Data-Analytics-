from shiny import App, render, ui
import pandas as pd
import plotly.express as px
import seaborn as sns
import numpy as np
from shinywidgets import render_widget, output_widget
import base64

#data inladen 
category_per_year = pd.read_csv("category_per_year")
category_per_year['Year'] = category_per_year['Year'].astype(int)
category_per_year['project_count'] = category_per_year['project_count'].astype(int)
categories = sorted(category_per_year['category'].dropna().unique())

#afbeelding
def get_image_base64(path):
    with open(path, "rb") as f: 
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/jpg;base64,{encoded}"  # of png

# Define UI
app_ui = ui.page_fluid(
    ui.tags.img(
        src=get_image_base64("www/banner3.jpg"),  # pas pad aan indien nodig
        style="width: auto; height: auto; max-width: 50%; display: block; margin: auto;"
    ),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_select("category", "Select a category", 
                {cat: cat for cat in categories}, 
                selected="engineering and technology"),
        ),
        ui.navset_tab(
            ui.nav_panel("Amount of projects over time", ui.output_ui("category_plot"))
        )
    )
)

# Define Server
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
        fig.update_layout(height=500, margin={"r":0,"t":50,"l":0,"b":0})
        return ui.HTML(fig.to_html(include_plotlyjs='cdn'))
    
# Create app
app = App(app_ui, server)