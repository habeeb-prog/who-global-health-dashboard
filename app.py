import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from pathlib import Path

# ── data ──────────────────────────────────────────────────────────────
df = pd.read_csv("data/processed/health_clean.csv")
trends = pd.read_csv("data/processed/trends.csv")
anomalies = pd.read_csv("data/processed/anomalies.csv")
correlations = pd.read_csv("data/processed/correlations.csv", index_col=0)
benchmarks = pd.read_csv("data/processed/benchmarks.csv")

# ── constants ─────────────────────────────────────────────────────────
INDICATORS = [
    "life_expectancy", "adult_mortality", "alcohol",
    "hepatitis_b", "bmi", "polio", "total_expenditure",
    "diphtheria", "gdp_per_capita", "thinness_1_19_years",
    "income_composition_of_resources", "schooling"
]

INDICATOR_LABELS = {
    "life_expectancy": "Life Expectancy",
    "adult_mortality": "Adult Mortality",
    "alcohol": "Alcohol Consumption",
    "hepatitis_b": "Hepatitis B Immunisation",
    "bmi": "BMI",
    "polio": "Polio Immunisation",
    "total_expenditure": "Health Expenditure %",
    "diphtheria": "Diphtheria Immunisation",
    "gdp_per_capita": "GDP per Capita",
    "thinness_1_19_years": "Thinness (1-19 years)",
    "income_composition_of_resources": "Income Composition",
    "schooling": "Schooling Years"
}

COUNTRIES = sorted(df["country"].unique().tolist())
YEARS = sorted([int(y) for y in df["year"].unique()])

# ── app ───────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True
)
server = app.server
# ── layout ────────────────────────────────────────────────────────────
app.layout = dbc.Container([

    dbc.Row([
        dbc.Col([
            html.H2("WHO Global Health Dashboard", className="text-white mt-3 mb-0"),
            html.P("190+ countries · 16 years · 12 health indicators",
                   className="text-white-50 mb-3")
        ])
    ], className="bg-primary mb-4"),

    dbc.Row([
        dbc.Col([
            dbc.Tabs(id="tabs", active_tab="tab-overview", children=[
                dbc.Tab(label="Global Overview", tab_id="tab-overview"),
                dbc.Tab(label="Country Deep Dive", tab_id="tab-country"),
                dbc.Tab(label="Regional Comparison", tab_id="tab-regional"),
                dbc.Tab(label="Anomaly Alerts", tab_id="tab-anomaly"),
                dbc.Tab(label="Correlation Explorer", tab_id="tab-correlation"),
            ])
        ])
    ], className="mb-3"),

    html.Div(id="tab-content")

], fluid=True)


# ── tab router ────────────────────────────────────────────────────────
@app.callback(Output("tab-content", "children"), Input("tabs", "active_tab"))
def render_tab(tab):
    if tab == "tab-overview":
        return overview_layout()
    elif tab == "tab-country":
        return country_layout()
    elif tab == "tab-regional":
        return regional_layout()
    elif tab == "tab-anomaly":
        return anomaly_layout()
    elif tab == "tab-correlation":
        return correlation_layout()


# ── page 1: global overview ───────────────────────────────────────────
def overview_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Label("Select Indicator"),
                dcc.Dropdown(
                    id="overview-indicator",
                    options=[{"label": v, "value": k} for k, v in INDICATOR_LABELS.items()],
                    value="life_expectancy",
                    clearable=False
                )
            ], width=4),
            dbc.Col([
                html.Label("Select Year"),
                dcc.Slider(
                    id="overview-year",
                    min=YEARS[0],
                    max=YEARS[-1],
                    step=1,
                    value=YEARS[-1],
                    marks={y: str(y) for y in YEARS[::2]}
                )
            ], width=8)
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dbc.Card(id="kpi-global-avg", className="text-center p-3"), width=3),
            dbc.Col(dbc.Card(id="kpi-highest", className="text-center p-3"), width=3),
            dbc.Col(dbc.Card(id="kpi-lowest", className="text-center p-3"), width=3),
            dbc.Col(dbc.Card(id="kpi-countries", className="text-center p-3"), width=3),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dcc.Graph(id="overview-map"), width=8),
            dbc.Col(dcc.Graph(id="overview-bar"), width=4),
        ])
    ], fluid=True)


# ── page 2: country deep dive ─────────────────────────────────────────
def country_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Label("Select Country"),
                dcc.Dropdown(
                    id="country-select",
                    options=[{"label": c, "value": c} for c in COUNTRIES],
                    value="United Kingdom",
                    clearable=False
                )
            ], width=4)
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dcc.Graph(id="country-trends"), width=8),
            dbc.Col(html.Div(id="country-trend-table"), width=4)
        ])
    ], fluid=True)


# ── page 3: regional comparison ───────────────────────────────────────
def regional_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Label("Select Indicator"),
                dcc.Dropdown(
                    id="regional-indicator",
                    options=[{"label": v, "value": k} for k, v in INDICATOR_LABELS.items()],
                    value="life_expectancy",
                    clearable=False
                )
            ], width=4)
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dcc.Graph(id="regional-trend"), width=12)
        ]),

        dbc.Row([
            dbc.Col(dcc.Graph(id="regional-bar"), width=12)
        ])
    ], fluid=True)


# ── page 4: anomaly alerts ────────────────────────────────────────────
def anomaly_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Label("Minimum Z-Score (severity)"),
                dcc.Slider(
                    id="anomaly-threshold",
                    min=2, max=5, step=0.5, value=3,
                    marks={i: str(i) for i in range(2, 6)}
                )
            ], width=6),
            dbc.Col([
                html.Label("Filter by Status"),
                dcc.Dropdown(
                    id="anomaly-status",
                    options=[
                        {"label": "All", "value": "All"},
                        {"label": "Developed", "value": "Developed"},
                        {"label": "Developing", "value": "Developing"}
                    ],
                    value="All",
                    clearable=False
                )
            ], width=3)
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dcc.Graph(id="anomaly-map"), width=8),
            dbc.Col(html.Div(id="anomaly-table"), width=4)
        ])
    ], fluid=True)


# ── page 5: correlation explorer ──────────────────────────────────────
def correlation_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col(dcc.Graph(id="correlation-heatmap"), width=7),
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        html.Label("X Axis"),
                        dcc.Dropdown(
                            id="scatter-x",
                            options=[{"label": v, "value": k} for k, v in INDICATOR_LABELS.items()],
                            value="gdp_per_capita",
                            clearable=False
                        )
                    ]),
                    dbc.Col([
                        html.Label("Y Axis"),
                        dcc.Dropdown(
                            id="scatter-y",
                            options=[{"label": v, "value": k} for k, v in INDICATOR_LABELS.items()],
                            value="life_expectancy",
                            clearable=False
                        )
                    ])
                ], className="mb-3"),
                dcc.Graph(id="scatter-plot")
            ], width=5)
        ])
    ], fluid=True)


# ── callbacks: global overview ────────────────────────────────────────
@app.callback(
    Output("kpi-global-avg", "children"),
    Output("kpi-highest", "children"),
    Output("kpi-lowest", "children"),
    Output("kpi-countries", "children"),
    Output("overview-map", "figure"),
    Output("overview-bar", "figure"),
    Input("overview-indicator", "value"),
    Input("overview-year", "value")
)
def update_overview(indicator, year):
    filtered = df[df["year"] == year][["country", indicator]].dropna()
    label = INDICATOR_LABELS.get(indicator, indicator)

    avg = round(float(filtered[indicator].mean()), 2)
    highest = filtered.loc[filtered[indicator].idxmax()]
    lowest = filtered.loc[filtered[indicator].idxmin()]
    n_countries = len(filtered)

    kpi_avg = [html.H5(f"{avg}"), html.P(f"Global Avg {label}")]
    kpi_high = [html.H5(highest["country"]), html.P(f"Highest: {round(float(highest[indicator]), 2)}")]
    kpi_low = [html.H5(lowest["country"]), html.P(f"Lowest: {round(float(lowest[indicator]), 2)}")]
    kpi_n = [html.H5(f"{n_countries}"), html.P("Countries with data")]

    map_fig = px.choropleth(
        filtered,
        locations="country",
        locationmode="country names",
        color=indicator,
        color_continuous_scale="RdYlGn",
        title=f"{label} by Country ({year})",
        labels={indicator: label}
    )
    map_fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))

    top10 = filtered.nlargest(10, indicator)
    bot10 = filtered.nsmallest(10, indicator)
    bar_df = pd.concat([top10, bot10])

    bar_fig = px.bar(
        bar_df.sort_values(indicator),
        x=indicator,
        y="country",
        orientation="h",
        title="Top & Bottom 10 Countries",
        labels={indicator: label, "country": ""},
        color=indicator,
        color_continuous_scale="RdYlGn"
    )
    bar_fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=40, b=0))

    return kpi_avg, kpi_high, kpi_low, kpi_n, map_fig, bar_fig


# ── callbacks: country deep dive ──────────────────────────────────────
@app.callback(
    Output("country-trends", "figure"),
    Output("country-trend-table", "children"),
    Input("country-select", "value")
)
def update_country(country):
    country_df = df[df["country"] == country].sort_values("year")

    fig = go.Figure()
    for indicator in INDICATORS:
        if indicator in country_df.columns:
            fig.add_trace(go.Scatter(
                x=country_df["year"].tolist(),
                y=country_df[indicator].tolist(),
                name=INDICATOR_LABELS.get(indicator, indicator),
                mode="lines+markers"
            ))
    fig.update_layout(
        title=f"{country} — All Indicators Over Time",
        xaxis_title="Year",
        yaxis_title="Value",
        legend=dict(orientation="h", y=-0.3)
    )

    country_trends_df = trends[trends["country"] == country][
        ["indicator", "slope", "r_squared", "direction", "latest_value"]
    ].copy()
    country_trends_df["indicator"] = country_trends_df["indicator"].map(
        lambda x: INDICATOR_LABELS.get(x, x)
    )
    country_trends_df.columns = ["Indicator", "Slope", "R²", "Direction", "Latest"]
    country_trends_df = country_trends_df.round(3)

    table = dbc.Table.from_dataframe(
        country_trends_df,
        striped=True,
        bordered=True,
        hover=True,
        size="sm"
    )

    return fig, table


# ── callbacks: regional comparison ────────────────────────────────────
@app.callback(
    Output("regional-trend", "figure"),
    Output("regional-bar", "figure"),
    Input("regional-indicator", "value")
)
def update_regional(indicator):
    label = INDICATOR_LABELS.get(indicator, indicator)

    regional_df = df.groupby(["year", "status"])[indicator].mean().reset_index()

    trend_fig = px.line(
        regional_df,
        x="year",
        y=indicator,
        color="status",
        title=f"{label} — Developed vs Developing Over Time",
        labels={indicator: label, "year": "Year", "status": "Status"}
    )

    latest_year = int(df["year"].max())
    bar_df = df[df["year"] == latest_year].groupby("status")[indicator].mean().reset_index()

    bar_fig = px.bar(
        bar_df,
        x="status",
        y=indicator,
        color="status",
        title=f"{label} by Status ({latest_year})",
        labels={indicator: label, "status": "Status"}
    )

    return trend_fig, bar_fig


# ── callbacks: anomaly alerts ─────────────────────────────────────────
@app.callback(
    Output("anomaly-map", "figure"),
    Output("anomaly-table", "children"),
    Input("anomaly-threshold", "value"),
    Input("anomaly-status", "value")
)
def update_anomaly(threshold, status):
    filtered = anomalies[anomalies["z_score"].abs() >= threshold].copy()

    if status != "All":
        filtered = filtered[filtered["status"] == status]

    filtered["severity"] = filtered["z_score"].abs().round(2)
    filtered = filtered.sort_values("severity", ascending=False)

    map_fig = px.choropleth(
        filtered,
        locations="country",
        locationmode="country names",
        color="severity",
        color_continuous_scale="Reds",
        title=f"Countries with Anomalous Health Changes (Z ≥ {threshold})",
        hover_data=["indicator", "year", "z_score"]
    )
    map_fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))

    table_df = filtered[["country", "year", "indicator", "z_score"]].head(20).copy()
    table_df["z_score"] = table_df["z_score"].round(3)
    table_df.columns = ["Country", "Year", "Indicator", "Z-Score"]

    table = dbc.Table.from_dataframe(
        table_df,
        striped=True,
        bordered=True,
        hover=True,
        size="sm"
    )

    return map_fig, table


# ── callbacks: correlation explorer ───────────────────────────────────
@app.callback(
    Output("correlation-heatmap", "figure"),
    Output("scatter-plot", "figure"),
    Input("scatter-x", "value"),
    Input("scatter-y", "value")
)
def update_correlation(x_col, y_col):
    heatmap_fig = go.Figure(data=go.Heatmap(
        z=correlations.values.tolist(),
        x=[INDICATOR_LABELS.get(c, c) for c in correlations.columns],
        y=[INDICATOR_LABELS.get(c, c) for c in correlations.index],
        colorscale="RdBu",
        zmid=0,
        text=correlations.values.round(2).tolist(),
        texttemplate="%{text}",
        showscale=True
    ))
    heatmap_fig.update_layout(
        title="Correlation Matrix — All Indicators",
        margin=dict(l=0, r=0, t=40, b=0)
    )

    scatter_df = df[[x_col, y_col, "status", "country", "year"]].dropna()
    x_label = INDICATOR_LABELS.get(x_col, x_col)
    y_label = INDICATOR_LABELS.get(y_col, y_col)

    scatter_fig = px.scatter(
        scatter_df,
        x=x_col,
        y=y_col,
        color="status",
        hover_data=["country", "year"],
        trendline="ols",
        title=f"{x_label} vs {y_label}",
        labels={x_col: x_label, y_col: y_label}
    )

    return heatmap_fig, scatter_fig


if __name__ == "__main__":
    app.run(debug=True)