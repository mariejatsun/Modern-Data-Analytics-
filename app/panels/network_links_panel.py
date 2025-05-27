from shiny import ui, render
import plotly.graph_objects as go
from ipywidgets import IntRangeSlider
from sklearn.cluster import KMeans
from utils.methods import get_lat_lon_from_iso2
from utils.layout import panel_with_banner

def network_links_panel(clusters, years):
    return panel_with_banner(
        "Collaboration Network",
        ui.div(
            ui.input_select("network_year_range", "Select a year", 
                            {f"{y}": f"{y}" for y in years}, 
                            selected=f"{years[0]}"),
            ui.input_select("network_cluster", "Select cluster", 
                            {str(c): str(c) for c in clusters}),
            ui.output_ui("network_links_plot"),
            style="margin-left: 40px; margin-right: 40px;"  # Add your desired margin here
        )
    )

def register_network_links_server(output, input, data):
    df_project = data["df_project"]
    df_organization = data["df_organization"]
    years = data["years"]
    clusters_df = data["clusters_df"]
    network_df = data["network_df"]

    @output
    @render.ui
    def network_links_plot():
        # Get selected year range and cluster
        start_year, end_year = map(int, input.network_year_range().split('-')) if '-' in input.network_year_range() else (int(input.network_year_range()), int(input.network_year_range()))
        selected_cluster = input.network_cluster()

        # Filter data
        project_ids = df_project[(df_project['startYear'] >= start_year) & (df_project['startYear'] <= end_year)]['id']
        df_filtered_org = df_organization[df_organization['projectID'].isin(project_ids)]

        if df_filtered_org.empty:
            return ui.HTML("<p>No data for selected period.</p>")
        countries = clusters_df[clusters_df['cluster'].astype(str) == str(selected_cluster)]['country'].tolist()        
        if len(countries) < 2:
            return ui.HTML("<p>Not enough countries in this cluster to show links.</p>")

        coords = {}
        for c in countries:
            lat, lon = get_lat_lon_from_iso2(c)
            if lat is not None and lon is not None:
                coords[c] = (lat, lon)
        valid_countries = [c for c in countries if c in coords]

        lines = []
        weights = []
        for i, c1 in enumerate(valid_countries):
            for j, c2 in enumerate(valid_countries):
                if j <= i:
                    continue
                weight = network_df.loc[c1, c2]
                if weight > 0:
                    lines.append({
                        'from': c1,
                        'to': c2,
                        'weight': weight,
                        'from_lat': coords[c1][0],
                        'from_lon': coords[c1][1],
                        'to_lat': coords[c2][0],
                        'to_lon': coords[c2][1],
                    })
                    weights.append(weight)

        lats = [coords[c][0] for c in valid_countries]
        lons = [coords[c][1] for c in valid_countries]
        names = [c for c in valid_countries]

        fig = go.Figure()

        # Color lines by weight using red with varying alpha (transparency)
        if lines:
            min_w, max_w = min(weights), max(weights)

            def get_rgba(val):
                if max_w == min_w:
                    t = 1.0
                else:
                    t = (val - min_w) / (max_w - min_w)
                alpha = 0.1 + 0.9 * t
                return f'rgba(220, 20, 60, {alpha:.2f})'  

            for link in lines:
                color = get_rgba(link['weight'])
                fig.add_trace(go.Scattergeo(
                    lon=[link['from_lon'], link['to_lon']],
                    lat=[link['from_lat'], link['to_lat']],
                    mode='lines',
                    line=dict(width=3, color=color),
                    opacity=1.0,  
                    showlegend=False,
                    hoverinfo='text',
                    text=f"{link['from']}–{link['to']}: {link['weight']}"
                ))

        fig.add_trace(go.Scattergeo(
            lon=lons,
            lat=lats,
            mode='markers+text',
            marker=dict(size=10, color='blue'),
            text=names,
            textposition="top center",
            hoverinfo='text'
        ))
        fig.update_geos(
            showcountries=True,
            countrycolor="LightGray",
            showcoastlines=True,
            coastlinecolor="Gray",
            projection_type="natural earth"
        )
        fig.update_layout(
            title=f"Collaboration Links in Cluster {selected_cluster} ({start_year}-{end_year})",
            height=600,
            margin=dict(r=0, l=0, t=50, b=0)
        )
        return ui.HTML(fig.to_html(include_plotlyjs='cdn'))