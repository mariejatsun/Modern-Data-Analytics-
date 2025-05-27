from shiny import ui, render
import plotly.express as px
import pandas as pd
from utils.layout import panel_with_banner

def funding_map_panel(years):
    return panel_with_banner(
        "Funding Map",
        ui.input_slider("funding_year_start", "Start Year", min(years), max(years), min(years)),
        ui.input_slider("funding_year_end", "End Year", min(years), max(years), max(years)),
        ui.output_ui("funding_map")
    )

def register_funding_map_server(output, input, data):
    merged_funding = data["merged_funding"]
    df_organization = data["df_organization"]
    df_project = data["df_project"]

    # Helper: ISO2 to ISO3
    import pycountry
    def convert_iso2_to_iso3(iso2_code):
        try:
            return pycountry.countries.get(alpha_2=iso2_code).alpha_3
        except Exception:
            return None

    @output
    @render.ui
    def funding_map():
        start_year = input.funding_year_start()
        end_year = input.funding_year_end()
        # Filter organizations by project start year
        df_project['startYear'] = pd.to_datetime(df_project['startDate'], errors='coerce').dt.year
        orgs = df_organization.copy()
        orgs['year'] = orgs['projectID'].map(df_project.set_index('id')['startYear'])
        orgs = orgs[(orgs['year'] >= start_year) & (orgs['year'] <= end_year)]

        # Group by country and sum contributions
        funding = orgs.groupby('country')['netEcContribution'].sum().reset_index()
        funding['iso_alpha'] = funding['country'].apply(convert_iso2_to_iso3)
        funding = funding.dropna(subset=['iso_alpha'])

        if funding.empty:
            return ui.HTML("<p>No data for selected period.</p>")

        fig = px.scatter_geo(
            funding,
            locations="iso_alpha",
            locationmode="ISO-3",
            size="netEcContribution",
            hover_name="country",
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
        return ui.HTML(fig.to_html(include_plotlyjs='cdn'))