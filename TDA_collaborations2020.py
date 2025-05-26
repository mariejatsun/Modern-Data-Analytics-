import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import json
import os

# paths 
matrix_path = "../MDA/data/landen_samenwerking_matrix2020.csv"
category_path = "category_per_year"
project_path = "../MDA/data/cordis-h2020projects-csv/project.csv"
euro_path = "../MDA/data/cordis-h2020projects-csv/euroSciVoc.csv"
organization_path = "../MDA/data/cordis-h2020projects-csv/organization.csv"
output_path = "/Users/mariejatsun/Downloads/country_network_2020.json"

# load collaboration matrix 
matrix = pd.read_csv(matrix_path, index_col=0)

# KMeans clustering : for labels 
kmeans = KMeans(n_clusters=5, n_init="auto", random_state=42)
clusters = kmeans.fit_predict(matrix.values)
country_list = matrix.index.tolist()
country_cluster = dict(zip(country_list, clusters))

# most common research category per country
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

# create nodes 
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

# create edges 
edges = []
for i, c1 in enumerate(country_list):
    for j, c2 in enumerate(country_list):
        if j <= i:
            continue
        weight = int(matrix.iloc[i, j])
        if weight > 0:
            for _ in range(weight):
                edges.append({
                    "source": country_to_id[c1],
                    "target": country_to_id[c2]
                })

# combina + export 
network = {
    "nodes": nodes,
    "links": edges
}

with open(output_path, "w") as f:
    json.dump(network, f, indent=2)

print(f"JSON opgeslagen als: {output_path}")







 # print number of countries 

# count total collaborations per country
country_total_collab = matrix.sum(axis=1)

# select countries with at least 10 collaborations
landen_10plus = set(country_total_collab[country_total_collab >= 10].index)

print(f"\nAantal landen met minstens 10 samenwerkingen: {len(landen_10plus)}")
print(f"Landen: {sorted(landen_10plus)}")

# determine most common category for these countries
categorie_per_land = {}
for land in landen_10plus:
    cat = country_category.get(land, None)
    if cat is not None:
        categorie_per_land[land] = cat

# count how often each category occurs as 'most common' for these countries
from collections import Counter
categorie_count = Counter(categorie_per_land.values())

print("\nAantal landen per meest voorkomende categorie (voor landen met >=10 samenwerkingen):")
for cat, count in categorie_count.items():
    print(f"{cat}: {count}")