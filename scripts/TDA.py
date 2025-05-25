import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import json
import os

# --- Paths ---
matrix_path = "landen_samenwerking_matrix2020.csv"
category_path = "category_per_year"
project_path = "./cordis-h2020projects-csv/project.csv"
euro_path = "./cordis-h2020projects-csv/euroSciVoc.csv"
organization_path = "./cordis-h2020projects-csv/organization.csv"
output_path = "/Users/mariejatsun/Downloads/country_network_2020.json"

# --- 1. Laad samenwerking matrix ---
matrix = pd.read_csv(matrix_path, index_col=0)

# --- 2. KMeans clustering (2 clusters) ---
kmeans = KMeans(n_clusters=2, n_init="auto", random_state=42)
clusters = kmeans.fit_predict(matrix.values)
country_list = matrix.index.tolist()
country_cluster = dict(zip(country_list, clusters))

# --- 3. Meest voorkomende research category per land ---
df_project = pd.read_csv(project_path, delimiter=";", on_bad_lines="skip", low_memory=False)
df_euro = pd.read_csv(euro_path, delimiter=";", on_bad_lines="skip", low_memory=False)
df_org = pd.read_csv(organization_path, delimiter=";", on_bad_lines="skip", low_memory=False)

df_org = df_org[['projectID', 'country']].drop_duplicates()
df_euro = df_euro[['projectID', 'euroSciVocPath']].dropna()
df_euro['category'] = df_euro['euroSciVocPath'].str.split('/').str[1]
df_proj_country = df_org.merge(df_euro, on='projectID', how='inner')

country_category = (
    df_proj_country.groupby(['country', 'category'])
    .size()
    .reset_index(name='count')
    .sort_values(['country', 'count'], ascending=[True, False])
    .drop_duplicates('country')
    .set_index('country')['category']
    .to_dict()
)

# --- 4. Nodes: maak mapping van country naar id ---
nodes = []
country_to_id = {}
for idx, country in enumerate(country_list, start=1):
    country_to_id[country] = idx
    nodes.append({
        "id": idx,
        "label": country,
        "cluster": int(country_cluster.get(country, -1)),
        "category": country_category.get(country, None)
    })

# --- 5. Edges: gebruik id's als source/target ---
edges = []
for i, c1 in enumerate(country_list):
    for j, c2 in enumerate(country_list):
        if j <= i:
            continue
        weight = int(matrix.iloc[i, j])
        if weight > 0:
            edges.append({
                "source": country_to_id[c1],
                "target": country_to_id[c2]
            })

# --- 6. Combineer en exporteer ---
network = {
    "nodes": nodes,
    "links": edges
}

with open(output_path, "w") as f:
    json.dump(network, f, indent=2)

print(f"JSON opgeslagen als: {output_path}")