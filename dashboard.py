import json
import pandas as pd
import plotly.express as px


with open("./Kartendaten/transformiert/Kartendaten_Gemeinden.geojson") as f:
    gemeinden = json.load(f)
df_results = pd.read_excel("results.xlsx")
df_gemeinden = pd.read_excel("Gemeinden_Graubünden.xlsx")

#Neuen df erstellen mit minimaler Fahrzeit pro Gemeinde
min_fahrzeiten = df_results.groupby("GDENAME")["Fahrzeit in min"].min().reset_index()
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
fig.show()


