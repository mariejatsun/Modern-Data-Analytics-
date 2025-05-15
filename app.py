from shiny import App, render, ui
import pandas as pd
import plotly.express as px
import seaborn as sns
import numpy as npq
from shinywidgets import render_widget, output_widget

# Load the iris dataset
iris = sns.load_dataset("iris")

# Define UI
app_ui = ui.page_fluid(
    ui.panel_title("Nineth app ..."),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_select("var", "1. Select the quantitative variable:", 
                {"sepal_length": "sepal_length", "sepal_width": "sepal_width", "petal_length": "petal_length", "petal_width": "petal_width"}, 
                selected="petal_length"),
            ui.input_slider("bin", "2. Select the number of histogram BINs:", 5, 25, 15),
            ui.input_radio_buttons("colour", "3. Select the color of histogram", ["black", "yellow", "red"], selected="yellow")
        ),
        ui.navset_tab(
            ui.nav_panel("Panel 1", ui.output_text("text1"), output_widget("myhist")),
            ui.nav_panel("Panel 2", ui.output_data_frame("summary"))
        )
    )
)

# Define Server
def server(input, output, session):        
    @output
    @render.text
    def text1():
        colm = input.var()
        return f"The variable of interest is here: {colm}"

    @output
    @render_widget
    def myhist():
        colm = input.var()
        fig = px.histogram(iris, x=colm, nbins=input.bin(), color_discrete_sequence=[input.colour()])
        fig.update_layout(title="Histogram of Iris dataset",
                          xaxis_title=colm.replace("_", " ").title(),
                          yaxis_title="Count",
                          template="plotly_white")
        
        return fig
    
    @output
    @render.data_frame
    def summary():
        return iris.describe()

# Create app
app = App(app_ui, server)