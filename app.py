from shiny import App, render, ui
import pandas as pd
import plotly.express as px
import seaborn as sns
import numpy as np
from shinywidgets import render_widget, output_widget

#data inladen 
category_per_year = pd.read_csv("category_per_year")
category_per_year['Year'] = category_per_year['Year'].astype(int)
category_per_year['project_count'] = category_per_year['project_count'].astype(int)
categories = sorted(category_per_year['category'].dropna().unique())


# Define UI
app_ui = ui.page_fluid(
    ui.tags.img(src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Flag_of_Europe.svg/320px-Flag_of_Europe.svg.png", style="width:100%; max-height:200px; object-fit:cover;"),
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