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
df_organization = pd.read_csv("df_organization.csv", low_memory=False)
df_project = pd.read_csv("df_project.csv")

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
        ui.nav_panel("Network analysis", 
            ui.input_slider("cluster_years", "Select year range", min=min(years), max=max(years), value=(2014, 2020), step=1),
            ui.input_numeric("n_visible_clusters", "Number of clusters to display (from 5 total)", value=5, min=1, max=5),
            ui.output_ui("network_map"),
        ),
        ui.nav_panel("Research impact - citations"),
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
    def network_map():
        start_year, end_year = input.cluster_years()
        n_visible = input.n_visible_clusters()

        project_ids = df_project[(df_project['startYear'] >= start_year) & (df_project['startYear'] <= end_year)]['id']
        df_filtered_org = df_organization[df_organization['projectID'].isin(project_ids)]

        if df_filtered_org.empty:
            return ui.HTML("<p>No data for selected period.</p>")

        from definitions import country_network_matrices, cluster_dataframe

        network_df, dissimilarity_df = country_network_matrices(df_filtered_org)
        clusters_df = cluster_dataframe(dissimilarity_df, AgglomerativeClustering(n_clusters=5, metric="precomputed", linkage="average"), "Agglomerative")
        clusters_df.reset_index(drop=True, inplace=True)
        clusters_df['cluster'] = clusters_df['cluster'].astype(int)

        coords = {}
        for c in clusters_df['country']:
            latlon = get_lat_lon_from_iso2(c)
            if latlon and latlon[0] is not None:
                coords[c] = latlon

        filtered_df = clusters_df[clusters_df['cluster'] < n_visible].copy()

        lines = []
        max_weight = 0
        for i, c1 in enumerate(filtered_df['country']):
            for j, c2 in enumerate(filtered_df['country']):
                if j <= i or c1 not in coords or c2 not in coords:
                    continue
                try:
                    weight = network_df.loc[c1, c2]
                except KeyError:
                    continue
                if weight > 0:
                    max_weight = max(max_weight, weight)
                    lines.append({
                        'from': c1,
                        'to': c2,
                        'weight': weight,
                        'from_lat': coords[c1][0],
                        'from_lon': coords[c1][1],
                        'to_lat': coords[c2][0],
                        'to_lon': coords[c2][1],
                    })

        fig = go.Figure()
        for link in lines:
            width = max(1, link['weight'] / max_weight * 10)
            fig.add_trace(go.Scattergeo(
                lon=[link['from_lon'], link['to_lon']],
                lat=[link['from_lat'], link['to_lat']],
                mode='lines',
                line=dict(width=width, color='orange'),
                opacity=0.7,
                showlegend=False,
                hoverinfo='skip'
            ))

        filtered_df['lat'] = filtered_df['country'].apply(lambda c: coords[c][0] if c in coords else None)
        filtered_df['lon'] = filtered_df['country'].apply(lambda c: coords[c][1] if c in coords else None)

        fig.add_trace(go.Scattergeo(
            lon=filtered_df['lon'],
            lat=filtered_df['lat'],
            text=filtered_df['country'],
            mode='markers+text',
            marker=dict(size=10, color=filtered_df['cluster'], colorscale='Viridis'),
            textposition="top center",
            hoverinfo='text'
        ))

        fig.update_geos(showcountries=True, countrycolor="LightGray", showcoastlines=True, coastlinecolor="Gray", projection_type="natural earth")
        fig.update_layout(
            title=f"Country Clusters and Collaboration Links ({start_year}-{end_year})",
            height=600,
            margin=dict(r=0, l=0, t=50, b=0)
        )

        return ui.HTML(fig.to_html(include_plotlyjs="cdn"))

# App maken
app = App(app_ui, server)





