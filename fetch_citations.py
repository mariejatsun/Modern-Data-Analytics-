import pandas as pd
import pycountry
import plotly.express as px
import requests
from tqdm import tqdm  # For progress bar

csv_path2020_publication = "./cordis-h2020projects-csv/projectPublications2020.csv"
csv_path2024_publication = "./cordis-HORIZONprojects-csv/projectPublications2024.csv"

df2020_publication = pd.read_csv(csv_path2020_publication,delimiter=";", on_bad_lines="skip", low_memory=False)
df2020_publication.drop_duplicates(inplace=True)
df2020_publication.dropna(subset=["projectID", "doi"], inplace= True)

df2024_publication=pd.read_csv(csv_path2024_publication,  delimiter=";", on_bad_lines="skip", low_memory=False)
df2024_publication.drop_duplicates(inplace=True)
df2024_publication.dropna(subset=["projectID", "doi"], inplace= True)

# Function to fetch citation count from OpenAlex API
def fetch_citation_count(doi):
    try:
        # Format the DOI for the OpenAlex API
        doi = doi.strip().lower()
        url = f"https://api.openalex.org/works/https://doi.org/{doi}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get("cited_by_count", 0)  # Return citation count or 0 if not found
        else:
            return None  # Return None if the request fails
    except Exception as e:
        print(f"Error fetching data for DOI {doi}: {e}")
        return None
    
# Add a new column for citation counts
tqdm.pandas()  # Enable progress bar for pandas
#df2020_publication['citation_count'] = df2020_publication['doi'].progress_apply(fetch_citation_count)
df2024_publication['citation_count'] = df2024_publication['doi'].progress_apply(fetch_citation_count)
# Save the updated DataFrame to a new CSV file (optional)
#df2020_publication.to_csv("updated_publications_with_citations.csv", index=False)
df2024_publication.to_csv("updated_publications_with_citations_2024.csv", index=False)
# Display the updated DataFrame
#print(df2020_publication.head())
print(df2024_publication.head())