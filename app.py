from shiny import App, ui
import pandas as pd


# Import panel UI and server registration functions
from panels.analyse_panel import analyse_panel, register_analyse_server
from panels.funding_map_panel import funding_map_panel, register_funding_map_server
from panels.clustering_panel import clustering_panel, register_clustering_server
from panels.network_links_panel import network_links_panel, register_network_links_server
from panels.research_impact_panel import research_impact_panel, register_research_impact_server
from panels.explanatory_panel import explanatory_data_panel, register_explanatory_data_server
from panels.topological_data_analysis_panel import topological_data_analysis_panel

# Optionally: introduction_panel and its server, if you have them
from panels.introduction_panel import introduction_panel

# Data loading
category_per_year = pd.read_csv("./data/category_per_year.csv")
category_per_year['Year'] = category_per_year['Year'].astype(int)
category_per_year['project_count'] = category_per_year['project_count'].astype(int)
categories = sorted(category_per_year['category'].dropna().unique())
category_counts = pd.read_csv("./data/category_counts.csv")  
years = sorted(category_counts['startYear'].dropna().unique())
merged_funding = pd.read_csv("./data/merged_funding.csv")
df_organization = pd.read_csv("./data/df_organization.csv", low_memory=False)
df_project = pd.read_csv("./data/df_project.csv")
category_year_stats = pd.read_csv("./data/category_year_stats.csv")
citations_per_topic_year = pd.read_csv("./data/citations_per_topic_year.csv")
cluster_df = pd.read_csv("./data/clusters_df.csv")  # Assuming this is the clustering data
clusters = sorted(cluster_df['cluster'].dropna().unique())
network_df = pd.read_csv("./data/network_df.csv", index_col=0)  # Assuming this is the network data
df_regression = pd.read_csv("./data/regression_dataset.csv")  # Assuming this is the regression data


# UI
app_ui = ui.page_fluid(
    ui.navset_tab(
        introduction_panel(),
        analyse_panel(categories, years),
        funding_map_panel(years),
        clustering_panel(years, ["K-means", "Agglomerative", "HDBSCAN"]),
        topological_data_analysis_panel(), 
        network_links_panel(clusters, years),
        research_impact_panel(categories, years),
        explanatory_data_panel(categories)
    )
)

def server(input, output, session):
    # Shared data dictionary for all panels
    data = {
        "category_per_year": category_per_year,
        "category_counts": category_counts,
        "merged_funding": merged_funding,
        "df_organization": df_organization,
        "df_project": df_project,
        "category_year_stats": category_year_stats,
        "citations_per_topic_year": citations_per_topic_year,
        "clusters_df": cluster_df,
        "network_df": network_df,
        "years": years,
        "categories": categories,
        "df_regression": df_regression
    }
    register_analyse_server(output, input, data)
    register_funding_map_server(output, input, data)
    register_clustering_server(output, input, data)
    register_network_links_server(output, input, data)
    register_research_impact_server(output, input, data)
    register_explanatory_data_server(output, input, data)
    # If you have an introduction_panel server, call it here as well

# App creation
app = App(app_ui, server) 