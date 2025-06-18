from dash import Dash, dcc, html, Input, Output, callback
import json
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

app = Dash (__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

with open("./Kartendaten/transformiert/Kartendaten_Gemeinden.geojson") as f:
    gemeinden = json.load(f)

df_results = pd.read_excel("results.xlsx")
df_gemeinden = pd.read_excel("Gemeinden_Graubünden.xlsx")
df_spitaeler = pd.read_excel("Spitalliste_bereinigt_fuer_Dashboard.xlsx")
df_population = pd.read_excel("Bevölkerung_Kanton_Graubünden.xlsx", usecols="A,AA,AB,AC", header=1)

spitaeler_namelist_all = df_spitaeler["Spitalname"].values.tolist()
spitaeler_namelist_current = spitaeler_namelist_all[:7]



app.layout = html.Div([
    dbc.Row([
        dbc.Col([html.H1("Räumliche Erreichbarkeit geburtshilflicher Versorgungsangebote im Kanton Graubünden", style={"font-size":"1.8rem", "margin-bottom":"1rem"})], width=12)
    ]),
    dbc.Row([
        dbc.Col(["Um die Schliessung einer Geburtsabteilung zu simulieren, entfernen Sie das entsprechende Spital in der Auwahl des Dropdown-Menüs.", 
                 dcc.Dropdown(spitaeler_namelist_all, spitaeler_namelist_current, id="spitaeler_dropdown", multi=True),
                 html.Button("Zurücksetzen des Dropdowns auf den aktuellen IST-Zustand der Geburtsabteilungen", id="reset-dropdown", n_clicks=0)], width=9),
        dbc.Col(["Wählen Sie die Einheit für die Darstellung in den Diagrammen",
                 dcc.RadioItems(["Fahrzeit in min", "Distanz in km"], "Fahrzeit in min", id="radioitems_unit")], width=3)
    ]),
    dbc.Row([
        dbc.Col([dcc.Graph(id="graph-map")], width=8),
        dbc.Col([dcc.Graph(id="graph-bar")], width=4)
    ], style={"margin-top":"1rem"})
    ], style={"margin":".5rem 1rem"}) #Endtag html.DIV

@app.callback(
    Output("spitaeler_dropdown", "value"),
    Input("reset-dropdown", "n_clicks"),
    prevent_initial_call=True)

def reset_dropdown(n_clicks):
    return spitaeler_namelist_current


@callback([Output("graph-map", "figure"),
          Output("graph-bar", "figure")],
          Input("spitaeler_dropdown", "value"),
          Input("radioitems_unit", "value"))

def create_figures(gewaehlte_spitaeler, gewaehlte_einheit):
    df_results_filtered = df_results[df_results["Spitalname"].isin(gewaehlte_spitaeler)]
    min = df_results_filtered.groupby("GDENAME")[gewaehlte_einheit].min().reset_index()
    min.columns = ["GDENAME", gewaehlte_einheit]

    df_gemeinden_subset = df_gemeinden[["GDEHISTID", "GDENAME"]]
    df_min = df_gemeinden_subset.merge(min, on="GDENAME", how="inner")
    df_population_subset = df_population[["GDENAME", "Alle betroffenen Personen"]]
    df_min = df_min.merge(df_population_subset, on="GDENAME", how="inner")

    fig_map = px.choropleth(
        df_min,
        geojson=gemeinden,
        locations="GDEHISTID",
        featureidkey="properties.HIST_NR",
        color=gewaehlte_einheit,
        hover_name="GDENAME",
        color_continuous_scale="ylorbr",
        range_color=(0,100),
        title=f"Minimale {gewaehlte_einheit} zur Geburtshilfe pro Gemeinde"
    )

    fig_map.update_geos(fitbounds="locations", visible=False)
    fig_map.update_layout(margin={"r":0,"t":30,"l":0,"b":0})

    bins = list(range(0, 120, 10)) + [120, 260]
    if gewaehlte_einheit == "Fahrzeit in min":
        labels = [f"{i}-{i+9} Min" for i in bins[:-2]] + ["120+ Min"]
    else:
        labels = [f"{i}-{i+9} km" for i in bins[:-2]] + ["120+ Min"]
    df_min["Klasse"] = pd.cut(df_min[gewaehlte_einheit], bins=bins, labels=labels, right=False)
    df_min = df_min.sort_values(by="Klasse")
    df_grouped = df_min.groupby("Klasse", as_index=False, observed=False)["Alle betroffenen Personen"].sum()
        
    fig_bar = px.bar(
        df_grouped,
        x="Klasse",
        y="Alle betroffenen Personen",
        title="Fahrzeitverteilung"
    )

    fig_bar.update_layout(xaxis_title=gewaehlte_einheit, yaxis_title="Anzahl betroffene Personen")

    df_min.to_excel("df_min.xlsx")
    df_grouped.to_excel("df_grouped.xlsx")

    return fig_map, fig_bar

if __name__ == '__main__':
    app.run(debug=True)
