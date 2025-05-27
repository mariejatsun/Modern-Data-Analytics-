from shiny import ui, render
import plotly.express as px
from utils.layout import panel_with_banner

def categories_panel(categories, years):
    return panel_with_banner(
        "Research Categories",
        ui.div(
            ui.input_select("category", "Select a category",
                            {cat: cat for cat in categories},
                            selected="engineering and technology"),
            ui.output_ui("category_plot"),
            ui.input_select("pie_year", "Select year for pie chart", {str(y): str(y) for y in years}),
            ui.output_ui("pie_chart"),
            style="margin-left: 40px; margin-right: 40px;"  # Add your desired margin here
        )
    )

def register_categories_server(output, input, data):
    category_per_year = data["category_per_year"]
    category_counts = data["category_counts"]

    @output
    @render.ui
    def category_plot():
        selected_cat = input.category()
        data_ = category_per_year[category_per_year['category'] == selected_cat]
        fig = px.line(
            data_,
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
    def pie_chart():
        year = input.pie_year()
        if not year:
            return ui.HTML("<p>No year selected.</p>")
        data_ = category_counts[category_counts['startYear'] == int(year)]
        if data_.empty:
            return ui.HTML("<p>No data for this year.</p>")
        fig = px.pie(
            data_,
            names='category',
            values='project_count',
            title=f'Project Distribution by Research Category ({year})',
            hole=0.3
        )
        fig.update_traces(textinfo='percent+label')
        fig.update_layout(height=500)
        return ui.HTML(fig.to_html(include_plotlyjs='cdn'))