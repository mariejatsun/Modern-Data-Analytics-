from shiny import ui, render
import plotly.express as px
from sklearn.cluster import KMeans, AgglomerativeClustering
import hdbscan
import pandas as pd
from utils.layout import panel_with_banner

def clustering_panel(years, methods):
    return panel_with_banner(
        "Clustering",
        ui.input_select("clustering_year", "Select year", {str(y): str(y) for y in years}),
        ui.input_select("clustering_method", "Select method", {m: m for m in methods}),
        ui.output_ui("clustering_plot")
    )

def register_clustering_server(output, input, data):
    df_project = data["df_project"]
    df_organization = data["df_organization"]

    def iso2_to_iso3(code):
        import pycountry
        try:
            return pycountry.countries.get(alpha_2=code).alpha_3
        except:
            return None

    def country_network_matrices(df, id_col='projectID', country_col='country'):
        import numpy as np
        import pandas as pd
        incidence = (df[[id_col, country_col]]
                     .drop_duplicates()
                     .assign(val=1)
                     .pivot(index=id_col, columns=country_col, values='val')
                     .fillna(0)
                     .astype(int))
        network_df = incidence.T @ incidence
        np.fill_diagonal(network_df.values, 0)
        network_df = network_df.astype(int)
        INF = 1e3
        with np.errstate(divide='ignore', invalid='ignore'):
            distance_arr = 1 / network_df.values
            distance_arr[network_df.values == 0] = INF
        dissimilarity_df = pd.DataFrame(distance_arr, index=network_df.index, columns=network_df.columns)
        return network_df, dissimilarity_df

    def cluster_dataframe(dissimilarity_df, algo):
        if getattr(algo, "metric", None) == "precomputed" or getattr(algo, "affinity", "") == "precomputed":
            algo.fit(dissimilarity_df)
        else:
            algo.fit(dissimilarity_df.values)
        import pandas as pd
        return (
            pd.DataFrame({
                "country": dissimilarity_df.index,
                "cluster": algo.labels_.astype(str)
            })
            .assign(iso_alpha=lambda df: df["country"].map(iso2_to_iso3))
            .dropna(subset=["iso_alpha"])
        )

    def cluster_map(df, title):
        fig = px.choropleth(
            df,
            locations="iso_alpha",
            color="cluster",
            hover_name="country",
            color_discrete_sequence=px.colors.qualitative.Set3,
            projection="natural earth",
            title=title
        )
        fig.update_geos(showcountries=True, countrycolor="LightGray",
                        showcoastlines=True, coastlinecolor="Gray")
        fig.update_layout(
            margin=dict(r=0, l=0, t=50, b=0),
            height=400,   # Set desired height in px
            width=600     # Set desired width in px
        )
        return fig

    @output
    @render.ui
    def clustering_plot():
        year = int(input.clustering_year())
        method = input.clustering_method()
        df_project['startDate'] = pd.to_datetime(df_project['startDate'], errors='coerce')
        project_ids = df_project[df_project['startDate'].dt.year == year]['id']
        df_filtered_org = df_organization[df_organization['projectID'].isin(project_ids)]

        if df_filtered_org.empty:
            return ui.HTML("<p>No projects found for the selected year.</p>")

        _, dissimilarity_df = country_network_matrices(df_filtered_org)

        clusterers = {
            "K-means":   KMeans(n_clusters=5, n_init="auto", random_state=42),
            "HDBSCAN":   hdbscan.HDBSCAN(metric='precomputed', min_cluster_size=2),
            "Agglomerative": AgglomerativeClustering(n_clusters=5, metric="precomputed", linkage="single"),
        }

        print(f"Selected method: {method}")

        if method not in clusterers:
            return ui.HTML("<p>Unknown clustering method.</p>")

        algo = clusterers[method]
        input_matrix = dissimilarity_df
        print("Before clustering")
        df_clustered = cluster_dataframe(input_matrix, algo)
        print("After clustering")
        fig = cluster_map(df_clustered, f"{method} clustering — international cooperation ({year})")
        return ui.HTML(fig.to_html(include_plotlyjs='cdn'))