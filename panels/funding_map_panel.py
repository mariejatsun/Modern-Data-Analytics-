from shiny import ui, render
import plotly.express as px
import pandas as pd
from utils.layout import panel_with_banner
from utils.methods import iso3_to_name, convert_iso2_to_iso3


def funding_map_panel(years):
    return panel_with_banner(
        "Funding Map",
        ui.input_slider("funding_year_range", "Select Year Range", min(years), max(years), value=(min(years), max(years))),
        ui.output_ui("funding_map")
    )

def register_funding_map_server(output, input, data):
    merged_funding = data["merged_funding"]
    df_organization = data["df_organization"]
    df_project = data["df_project"]

    @output
    @render.ui
    def funding_map():
        # Haal begin en eindjaar uit range slider
        start_year, end_year = input.funding_year_range()

        # 2. Bereken projectjaar per organisatie
        df_project['startYear'] = pd.to_datetime(df_project['startDate'], errors='coerce').dt.year
        orgs = df_organization.copy()
        orgs['year'] = orgs['projectID'].map(df_project.set_index('id')['startYear'])
        orgs = orgs[(orgs['year'] >= start_year) & (orgs['year'] <= end_year)]

        # 3. Som bijdragen op per land
        funding = orgs.groupby('country')['netEcContribution'].sum().reset_index()
        funding['iso_alpha'] = funding['country'].apply(convert_iso2_to_iso3)
        funding['country_name'] = funding['iso_alpha'].apply(iso3_to_name)  
        funding = funding.dropna(subset=['iso_alpha'])

        if funding.empty:
            return ui.HTML("<p>No data for selected period.</p>")

        #4. Tooltip aanpassen
        funding['hover'] = funding.apply(
        lambda row: f"{row['country_name']}<br>The EC Net contribution is €{row['netEcContribution']:,.2f}".replace(",", " "),
        axis=1
                )


        fig = px.scatter_geo(
            funding,
            locations="iso_alpha",
            locationmode="ISO-3",
            size="netEcContribution",
            hover_name="hover",
            projection="natural earth",
            title=f"Net EC Contribution {start_year}-{end_year}",
            size_max=50
        )
        fig.update_geos(
            showcountries=True,
            countrycolor="LightGray",
            showcoastlines=True,
            coastlinecolor="LightGray",
        )
        fig.update_layout(
            margin={"r": 0, "t": 50, "l": 0, "b": 0},
            height=600,
        )
        fig.update_traces(hovertemplate="%{hovertext}<extra></extra>")

        return ui.HTML(fig.to_html(include_plotlyjs='cdn'))
