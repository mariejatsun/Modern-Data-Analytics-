from shiny import App, render, ui
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import numpy as np
import base64
import pycountry
from sklearn.cluster import AgglomerativeClustering
import countryinfo

# Data inladen 
category_per_year = pd.read_csv("category_per_year")
category_per_year['Year'] = category_per_year['Year'].astype(int)
category_per_year['project_count'] = category_per_year['project_count'].astype(int)
categories = sorted(category_per_year['category'].dropna().unique())
merged_funding = pd.read_csv("merged_funding.csv")
category_counts = pd.read_csv("category_counts.csv")  
years = sorted(category_counts['startYear'].dropna().unique())
df_organization= pd.read_csv("df_organization.csv", low_memory=False)
df_project= pd.read_csv("df_project.csv")
category_year_stats = pd.read_csv("category_year_stats.csv")
citations_per_topic_year = pd.read_csv("citations_per_topic_year.csv")

# Voor landencodes
def convert_iso2_to_iso3(iso2_code):
    try:
        return pycountry.countries.get(alpha_2=iso2_code).alpha_3
    except:
        return None

def iso3_to_name(iso3):
    try:
        return pycountry.countries.get(alpha_3=iso3).name
    except:
        return iso3 

# Afbeelding
def get_image_base64(path):
    with open(path, "rb") as f: 
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/jpg;base64,{encoded}"

def get_lat_lon_from_iso2(iso2):
    try:
        info = countryinfo.CountryInfo(iso2)
        latlng = info.latlng()
        if latlng and len(latlng) == 2:
            return latlng[0], latlng[1]
    except Exception:
        pass
    return None, None

# UI
app_ui = ui.page_fluid(
    ui.tags.img(
        src=get_image_base64("www/banner3.jpg"),
        style="width: auto; height: auto; max-width: 50%; display: block; margin: auto;"
    ),
    ui.navset_tab(
        ui.nav_panel("Introduction"),
        ui.nav_panel(
            "Analyse of research projects",
            ui.input_select("category", "Select a category",
                            {cat: cat for cat in categories},
                            selected="engineering and technology"),
            ui.output_ui("category_plot"),
            ui.input_select("pie_year", "Select year for pie chart", {str(y): str(y) for y in years}),
            ui.output_ui("pie_chart")
        ),
        ui.nav_panel(
            "Funding levels map",
            ui.input_slider(
                "map_years",
                "Select year range",
                min=int(min(years)),
                max=int(max(years)),
                value=(int(min(years)), int(max(years))),
                step=1,
            ),
            ui.output_ui("funding_map")
        ), 
        ui.nav_panel("Clustering"),
        ui.nav_panel("Network analysis"),
        ui.nav_panel("Research impact - citations", ui.input_select("citation_category", "Select a category",
                    {cat: cat for cat in categories},
                    selected=categories[0] if categories else None),
    ui.output_ui("citation_plot"), ui.input_select("citation_year", "Select year", {str(y): str(y) for y in years}),
    ui.output_ui("citation_pie")
),
        ui.nav_panel("Exploratory data analysis")
    )
)


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
    def pie_chart():
        year = input.pie_year()
        if not year:
            return ui.HTML("<p>No year selected.</p>")
        data = category_counts[category_counts['startYear'] == int(year)]
        if data.empty:
            return ui.HTML("<p>No data for this year.</p>")
        fig = px.pie(
            data,
            names='category',
            values='project_count',
            title=f'Project Distribution by Research Category ({year})',
            hole=0.3
        )
        fig.update_traces(textinfo='percent+label')
        fig.update_layout(height=500)
        return ui.HTML(fig.to_html(include_plotlyjs='cdn'))
    
    @output
    @render.ui
    def funding_map():
        start_year, end_year = input.map_years()
        contrib_type = "netEcContribution"

        orgs = df_organization[
            (df_organization["year"] >= start_year) &
            (df_organization["year"] <= end_year)
        ]

        if orgs.empty:
            return ui.HTML("<p>No data for selected period.</p>")

        funding = orgs.groupby("country")[contrib_type].sum().reset_index()
        funding.columns = ["country", "funding_sum"]
        funding["iso_alpha"] = funding["country"].apply(convert_iso2_to_iso3)

        funding["country_name"] = funding["iso_alpha"].apply(iso3_to_name)
        funding["hover_text"] = funding.apply(
            lambda row: f"{row['country_name']}<br>Total sum of funding is €{row['funding_sum']:,.0f}", axis=1
        )

        fig = px.scatter_geo(
            funding,
            locations="iso_alpha",
            locationmode="ISO-3",
            size="funding_sum",
            hover_name="country_name",
            custom_data=["hover_text"],
            projection="natural earth",
            title=f"Net EC Contribution ({start_year}–{end_year})",
            size_max=50
     )

        fig.update_traces(hovertemplate="%{customdata[0]}")
        fig.update_geos(showcountries=True, countrycolor="LightGray", showcoastlines=True, coastlinecolor="LightGray")
        fig.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0}, height=600)

        return ui.HTML(fig.to_html(include_plotlyjs="cdn"))
    
    @output
    @render.ui
    def citation_plot():
        selected_cat = input.citation_category()
        data = category_year_stats[category_year_stats['category'] == selected_cat]

        if data.empty:
            return ui.HTML("<p>No data available for this category.</p>")

        fig = px.line(
            data,
            x='Year',
            y='publication_count',
            markers=True,
            title=f'{selected_cat.capitalize()} Publications Over Time',
            labels={'publication_count': 'Number of Publications'}
        )
        fig.add_bar(
            x=data['Year'],
            y=data['total_citations'],
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
        return ui.HTML(fig.to_html(include_plotlyjs="cdn"))
    
    @output
    @render.ui
    def citation_pie():
        selected_year = int(input.citation_year())
        data = citations_per_topic_year[citations_per_topic_year['Year'] == selected_year]
        if data.empty:
            return ui.HTML("<p>No data for this year.</p>")

        fig = px.pie(
            data,
            names='category',
            values='total_citations',
            title=f'Citations by Research Topic in {selected_year}',
            hole=0.3
        )
        fig.update_traces(textinfo='percent+label')
        fig.update_layout(height=500)
        return ui.HTML(fig.to_html(include_plotlyjs='cdn'))

# App maken
app = App(app_ui, server) 

