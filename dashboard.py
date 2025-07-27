from dash import Dash, dcc, html, Input, Output, callback
import json
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

app = Dash (__name__, external_stylesheets=[dbc.themes.FLATLY])

with open("./Kartendaten/transformiert/Kartendaten_Gemeinden.geojson") as f:
    gemeinden = json.load(f)

df_results = pd.read_excel("results_Fahrzeitanalyse.xlsx")
df_gemeinden = pd.read_excel("Geographische_Kennzahlen_Gemeinden.xlsx")
df_spitaeler = pd.read_excel("Spitalliste.xlsx")
df_population = pd.read_excel("Bevölkerung_Kanton_Graubünden.xlsx", usecols="A,AA", header=1)


spitaeler_namelist_all = df_spitaeler["Spitalname"].values.tolist()
spitaeler_namelist_current = spitaeler_namelist_all[:7]



app.layout = html.Div([
    dbc.Row([
        dbc.Col([html.H1("Räumliche Erreichbarkeit geburtshilflicher Versorgungsangebote im Kanton Graubünden", style={"font-size":"1.8rem", "margin-bottom":"1rem", "color":"#2176BC"})], width=11),
        dbc.Col([dbc.Button("i", id="info", style={'width': '30px', 'height': '30px', 'border-radius': '50%', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'backgroundColor': "#2176BC", 'border-color': 'white', 'border-width': '3px'}),
                 dbc.Modal([
                     dbc.ModalHeader(dbc.ModalTitle("Informationen zu Datenquellen")),
                     dbc.ModalBody([
                         html.Div([
                             "Das vorliegende Dashboard wurde im Rahmen einer Bachelorarbeit erstellt, welche die Veränderung der räumlichen Erreichbarkeit geburtshilflicher Versorgungsangebote für die Bevölkerung im Kanton Graubünden bei Schliessung von Standorten untersuchte.",
                             html.Br(),
                             html.Br(),
                             "Für die Erstellung des Kartendiagramms würde der Datensatz swissBOUNDARIES3D vom Bundesamt für Landestopografie verwendet:",
                             html.Br(),
                             html.A("https://www.swisstopo.admin.ch/de/landschaftsmodell-swissboundaries3d", href="https://www.swisstopo.admin.ch/de/landschaftsmodell-swissboundaries3d", target="_blank"),
                             html.Br(),
                             html.Br(),
                             "Für die Ermittlung der Distanzen sowie Fahrzeiten von den Gemeinden zu den Spitälern, wurde die Time-Distance Matrix API-Schnittstelle des Openrouteservice verwendet:",
                             html.Br(),
                             html.A("https://openrouteservice.org/services/", href="https://openrouteservice.org/services/", target="_blank"),
                             html.Br(),
                             html.Br(),
                             "Die Ermittlung der Koordinaten der Spitäler erfolgte auf Basis der auf den jeweiligen Spitalwebseiten angegebenen Adressen unter Zuhilfenahme eines digitalen Kartendienstes.",
                             html.Br(),
                             "Bezüglich der Koordinaten der Gemeinden wurde der Datensatz 'Geographische Kennzahlen Gemeinden' des Bundesamts für Statistik verwendet:",
                             html.Br(),
                             html.A("https://www.agvchapp.bfs.admin.ch/de/kennzahlen/results?SnapshotDate=06.04.2025&Unit=Communes&IncCentroid=True", href="https://www.agvchapp.bfs.admin.ch/de/kennzahlen/results?SnapshotDate=06.04.2025&Unit=Communes&IncCentroid=True", target="_blank"),
                             html.Br(),
                             "Der Datensatz enthält die Zentrumskoordinaten jeder Schweizer Gemeinde. Die Zentrumskoordinate entspricht dabei dem wichtigsten sozioökonomischen Zentrum der Gemeinde.",
                             html.Br(),
                             html.Br(),
                             "Der Anzeige der Anzahl der potenziell betroffenen Personen liegt der Datensatz 'Ständige Wohnbevölkerung nach Eckwerten, Gemeinden, 2010-2023' aus dem Jahr 2023 zugrunde:",
                             html.Br(),
                             html.A("https://www.gr.ch/DE/institutionen/verwaltung/dvs/awt/statistik/Bevoelkerung/Seiten/Bevoelkerungsstand_und_-struktur.aspx", href="https://www.gr.ch/DE/institutionen/verwaltung/dvs/awt/statistik/Bevoelkerung/Seiten/Bevoelkerungsstand_und_-struktur.aspx", target="_blank"),
                             html.Br(),
                             "Da dort allerdings eine geschlechtsspezifische Aufschlüsselung innerhalb der Alterskategorien nicht verfügbar ist, wurde der Anteil der Frauen in den Alerskategorien gemäss der Geschlechterverteilung in der Gesamtbevölkerung (50% Frauen, 50% Männer)  geschätzt."
                         ], style={"wordBreak": "break-word", "whiteSpace": "normal"})
                     ])
                 ], id="modal", is_open=False)
        ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}, width=1)
    ]),
    dbc.Row([
        dbc.Col([html.Div(["Um die Schliessung einer Geburtsabteilung zu simulieren, entfernen Sie das entsprechende Spital in der Auwahl des Dropdown-Menüs.", 
                 dcc.Dropdown(spitaeler_namelist_all, spitaeler_namelist_current, id="spitaeler_dropdown", multi=True),
                 dbc.Button("Zurücksetzen des Dropdowns auf den aktuellen IST-Zustand der Geburtsabteilungen", id="reset-dropdown", n_clicks=0, style={"margin": "5px 0"})], style={"backgroundColor":"#A0CCF0", "borderRadius":"10px", "margin-right":"5px", "padding":"0 12px"})
                 ], style={"padding":"0"}, width=9),
        dbc.Col(["Wählen Sie die Einheit für die Darstellung in den Diagrammen",
                 dcc.RadioItems(["Fahrzeit in min", "Distanz in km"], "Fahrzeit in min", id="radioitems_unit")], style={"backgroundColor":"#A0CCF0", "borderRadius":"10px"}, width=3)
    ], style={"backgroundColor":"#C6E0F5", "padding":"12px", "borderRadius":"10px"}),
    dbc.Row([
        dbc.Col([
            dcc.Loading(id="loading-map", type="circle", overlay_style={"visibility":"visible", "filter": "blur(2px)"}, children=
            dcc.Graph(id="graph-map"))
        ], width=8),
        dbc.Col([
            dcc.Loading(id="loading-bar", type="circle", overlay_style={"visibility":"visible", "filter": "blur(2px)"}, children=
            dcc.Graph(id="graph-bar"))
            ], width=4)
    ], style={"margin-top":"1rem"}),
    dbc.Row([
        dbc.Col(["© openrouteservice.org by HeiGIT | Map data © OpenStreetMap contributors"])
    ])
    ], style={"margin":".5rem 1rem"}) #Endtag html.DIV

@app.callback(
    Output("spitaeler_dropdown", "value"),
    Input("reset-dropdown", "n_clicks"),
    prevent_initial_call=True)

def reset_dropdown(n_clicks):
    return spitaeler_namelist_current

@callback(Output('modal', 'is_open'),
          Input('info', 'n_clicks'),
          prevent_initial_call=True)

def manage_info_popup(n_clicks):
    is_open = True
    return is_open


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
    df_population_subset = df_population[["GDENAME", "Alle betroffenen Frauen"]]
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
    df_grouped = df_min.groupby("Klasse", as_index=False, observed=False)["Alle betroffenen Frauen"].sum()

    fig_bar = px.bar(
        df_grouped,
        x="Klasse",
        y="Alle betroffenen Frauen",
        title="Verteilung potenziell betroffener Personen <br>(Frauen im Alter von 15-54 Jahren)",
        color_discrete_sequence=["#42313A"]
    )

    fig_bar.update_layout(template="plotly_white", xaxis_title=gewaehlte_einheit, yaxis_title="Anzahl betroffene Personen")

    return fig_map, fig_bar

if __name__ == '__main__':
    app.run(debug=True)
