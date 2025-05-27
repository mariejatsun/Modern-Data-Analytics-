from shiny import ui, render
import plotly.express as px

def research_impact_panel(categories, years):
    return ui.nav_panel(
        "Research Impact",
        ui.input_select("impact_category", "Select Category", {cat: cat for cat in categories}),
        ui.input_select("impact_year", "Select Year", {str(y): str(y) for y in years}),
        ui.output_ui("impact_plot"),
        ui.output_ui("impact_pie")
    )

def register_research_impact_server(output, input, data):
    category_year_stats = data["category_year_stats"]
    citations_per_topic_year = data["citations_per_topic_year"]

    @output
    @render.ui
    def impact_plot():
        selected_cat = input.impact_category()
        if not selected_cat:
            return ui.HTML("<p>No category selected.</p>")
        data_ = category_year_stats[category_year_stats['category'] == selected_cat]
        if data_.empty:
            return ui.HTML("<p>No data for this category.</p>")
        fig = px.line(
            data_,
            x='Year',
            y='publication_count',
            markers=True,
            title=f'{selected_cat.capitalize()} Publications Over Time',
            labels={'publication_count': 'Number of Publications'}
        )
        fig.add_bar(
            x=data_['Year'],
            y=data_['total_citations'],
            name='Total Citations',
            yaxis='y2',
            marker_color='orange',
            opacity=0.5
        )
        fig.update_layout(
            height=500,
            margin={"r": 0, "t": 50, "l": 0, "b": 0},
            yaxis=dict(title='Number of Publications'),
            yaxis2=dict(
                title='Total Citations',
                overlaying='y',
                side='right'
            ),
            legend=dict(x=0.01, y=0.99)
        )
        return ui.HTML(fig.to_html(include_plotlyjs='cdn'))

    @output
    @render.ui
    def impact_pie():
        year = input.impact_year()
        if not year:
            return ui.HTML("<p>No year selected.</p>")
        data_ = citations_per_topic_year[citations_per_topic_year['Year'] == int(year)]
        if data_.empty:
            return ui.HTML("<p>No data for this year.</p>")
        fig = px.pie(
            data_,
            names='category',
            values='total_citations',
            title=f'Citations by Research Topic in {year}',
            hole=0.3
        )
        fig.update_traces(textinfo='percent+label')
        return ui.HTML(fig.to_html(include_plotlyjs='cdn'))