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
output_path = "/Users/mariejatsun/Downloads/country_network_2020_cutoff_10.json"

# --- 1. Laad samenwerking matrix ---
matrix = pd.read_csv(matrix_path, index_col=0)

# --- 2. KMeans clustering (2 clusters) ---
kmeans = KMeans(n_clusters=5, n_init="auto", random_state=42)
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

# --- 5. Edges: alleen als weight >= 10 ---
edges = []
for i, c1 in enumerate(country_list):
    for j, c2 in enumerate(country_list):
        if j <= i:
            continue
        weight = int(matrix.iloc[i, j])
        if weight >= 10:
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

# --- 7. Analyse landen met minstens 10 samenwerkingen (totaal) ---

# Bereken totaal aantal samenwerkingen per land (som over de rij)
country_total_collab = matrix.sum(axis=1)

# Selecteer landen met minstens 10 samenwerkingen
landen_10plus = set(country_total_collab[country_total_collab >= 10].index)

print(f"\nAantal landen met minstens 10 samenwerkingen: {len(landen_10plus)}")
print(f"Landen: {sorted(landen_10plus)}")

# Bepaal voor deze landen de meest voorkomende categorie
categorie_per_land = {}
for land in landen_10plus:
    cat = country_category.get(land, None)
    if cat is not None:
        categorie_per_land[land] = cat

# Tel hoe vaak elke categorie voorkomt als 'meest voorkomend' bij deze landen
from collections import Counter
categorie_count = Counter(categorie_per_land.values())

print("\nAantal landen per meest voorkomende categorie (voor landen met >=10 samenwerkingen):")
for cat, count in categorie_count.items():
    print(f"{cat}: {count}")