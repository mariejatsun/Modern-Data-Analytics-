from shiny import ui, render
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.layout import panel_with_banner

def explanatory_data_panel(categories):
    return panel_with_banner(
        "Explanatory Data",
        ui.h4("Histograms"),
        ui.output_plot("histograms"),
        ui.h4("Correlation Heatmap"),
        ui.output_plot("correlation"),
        ui.h4("General Regression Line"),
        ui.output_plot("regression_general"),
        ui.h4("Regression Lines per Research Category"),
        ui.input_select("category_exp", "Category", {c: c for c in categories}),
        ui.output_plot("regression_category"),
        ui.h4("All Categories: Regression Lines"),
        ui.output_plot("regression_all_categories")
    )

def register_explanatory_data_server(output, input, data):
    df = data['df_regression'].copy()

    @output
    @render.plot
    def histograms():
        fig, axes = plt.subplots(1, 3, figsize=(18, 4))
        sns.histplot(df['log_ecContribution'], bins=30, ax=axes[0], kde=True)
        axes[0].set_title('Distribution of log_ecContribution')
        axes[0].set_xlabel('log_ecContribution')

        sns.histplot(df['years_since_publication'], bins=30, ax=axes[1], kde=True)
        axes[1].set_title('Distribution of Years Since Publication')
        axes[1].set_xlabel('years_since_publication')

        sns.histplot(df['log_total_citations'], bins=30, ax=axes[2], kde=True)
        axes[2].set_title('Distribution of log Total Citations')
        axes[2].set_xlabel('log_total_citations')

        plt.tight_layout()
        return fig

    @output
    @render.plot
    def correlation():
        corr = df[['log_ecContribution', 'years_since_publication', 'total_citations']].corr()
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
        ax.set_title('Correlation Matrix')
        plt.tight_layout()
        return fig

    @output
    @render.plot
    def regression_general():
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.scatterplot(x='log_ecContribution', y='log_total_citations', data=df, alpha=0.5, ax=ax)
        sns.regplot(x='log_ecContribution', y='log_total_citations', data=df, scatter=False, color='red', ax=ax)
        ax.set_title('log Total Citations per Project vs log Funding')
        ax.set_xlabel('log Funding (ecContribution)')
        ax.set_ylabel('log Total Citations')
        plt.tight_layout()
        return fig

    @output
    @render.plot
    def regression_category():
        selected_cat = input.category_exp()
        subset = df[df['category'] == selected_cat]
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.scatterplot(x='log_ecContribution', y='log_total_citations', data=subset, alpha=0.6, ax=ax)
        if not subset.empty:
            sns.regplot(
                x='log_ecContribution',
                y='log_total_citations',
                data=subset,
                scatter=False,
                color='red',
                ax=ax,
                label='Regression line'
            )
        ax.set_title(f'log Total Citations vs log Funding\nCategory: {selected_cat}')
        ax.set_xlabel('log Funding (ecContribution)')
        ax.set_ylabel('log Total Citations')
        plt.tight_layout()
        return fig

    @output
    @render.plot
    def regression_all_categories():
        category_options = sorted(df['category'].dropna().unique())
        palette = sns.color_palette("tab10", n_colors=len(category_options))
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(
            x='log_ecContribution',
            y='log_total_citations',
            hue='category',
            data=df,
            alpha=0.4,
            palette=palette,
            legend='full',
            ax=ax
        )
        for i, cat in enumerate(category_options):
            subset = df[df['category'] == cat]
            if len(subset) > 1:
                x = subset['log_ecContribution']
                y = subset['log_total_citations']
                coef = np.polyfit(x, y, 1)
                x_vals = np.linspace(x.min(), x.max(), 100)
                y_vals = coef[0] * x_vals + coef[1]
                ax.plot(x_vals, y_vals, color=palette[i], label=f"{cat} (regression)")
        ax.set_title('log Total Citations vs log Funding\nRegression Lines per Research Category')
        ax.set_xlabel('log Funding (ecContribution)')
        ax.set_ylabel('log Total Citations')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        return fig