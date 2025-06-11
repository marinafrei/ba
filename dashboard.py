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

spitaeler_namelist_all = df_spitaeler["Spitalname"].values.tolist()
spitaeler_namelist_current = spitaeler_namelist_all[:7]



app.layout = html.Div([
    dbc.Row([
        dbc.Col([html.H1("Räumliche Erreichbarkeit geburtshilflicher Versorgungsangebote im Kanton Graubünden", style={"font-size":"1.8rem", "margin-bottom":"1rem"})], width=12)
    ]),
    dbc.Row([
        dbc.Col(["Um die Schliessung einer Geburtsabteilung zu simulieren, entfernen Sie das entsprechende Spital in der Auwahl des Dropdown-Menüs.", 
                 dcc.Dropdown(spitaeler_namelist_all, spitaeler_namelist_current, id="spitaeler_dropdown", multi=True)])
    ]),
    dbc.Row([
        dbc.Col([dcc.Graph(id="graph-map")], width=8),
        dbc.Col([dcc.Graph(id="graph-hist")], width=4)
    ], style={"margin-top":"1rem"})
    ], style={"margin":".5rem 1rem"}) #Endtag html.DIV



@callback(Output("graph-map", "figure"),
          Input("spitaeler_dropdown", "value"))

def create_df_for_map(gewaehlte_spitaeler):
    df_results_filtered = df_results[df_results["Spitalname"].isin(gewaehlte_spitaeler)]
    min_fahrzeiten = df_results_filtered.groupby("GDENAME")["Fahrzeit in min"].min().reset_index()
    min_fahrzeiten.columns = ["GDENAME", "MinFahrzeit"]

    df_gemeinden_subset = df_gemeinden[["GDEHISTID", "GDENAME"]]
    df_min_fahrzeit = df_gemeinden_subset.merge(min_fahrzeiten, on="GDENAME", how="inner")


    fig = px.choropleth(
        df_min_fahrzeit,
        geojson=gemeinden,
        locations="GDEHISTID",
        featureidkey="properties.HIST_NR",
        color="MinFahrzeit",
        hover_name="GDENAME",
        color_continuous_scale="Viridis",
        title="Minimale Fahrzeit zur Geburtshilfe pro Gemeinde"
    )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
    return fig

if __name__ == '__main__':
    app.run(debug=True)
