import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static

# Data inladen
bestanden = ['2021_Q2_Central.csv', '2021_Q3_Central.csv', '2021_Q4_Central.csv']
fiets_data_jaar = pd.concat([pd.read_csv(file) for file in bestanden], ignore_index=True)

weer_data = pd.read_csv('weather_london.csv')
metro_data = pd.read_csv('AC2021_AnnualisedEntryExit.csv', sep=';')
metro_stations_data = pd.read_csv('London stations.csv')

# Coördinaten dictionary
stations_dict = {
    row["Station"]: (row["Latitude"], row["Longitude"]) 
    for _, row in metro_stations_data.iterrows()
}

# Fix 'AnnualisedEnEx' (verwijder niet-numerieke tekens en zet om naar float)
metro_data["AnnualisedEnEx"] = (
    metro_data["AnnualisedEnEx"]
    .astype(str)                      # Zet om naar string om bewerkingen uit te voeren
    .str.replace(r"[^\d]", "", regex=True)  # Verwijder ALLES wat geen cijfer is
    .astype(float)                    # Zet om naar float
)

# Bereken het minimum, mediaan en maximum voor kleurindeling
low_threshold = metro_data["AnnualisedEnEx"].quantile(0.33)
mid_threshold = metro_data["AnnualisedEnEx"].quantile(0.66)

# Kaart aanmaken
m = folium.Map(location=[51.509865, -0.118092], tiles='CartoDB positron', zoom_start=11)

# Metro stations plotten
for _, row in metro_data.iterrows():
    station_name = row["Station"]
    busy_value = row["AnnualisedEnEx"]

    if station_name in stations_dict and pd.notnull(busy_value):
        lat, lon = stations_dict[station_name]
        radius = max(busy_value / 500000, 2)  # Dynamische schaal

        # Kleur bepalen op basis van drempels
        if busy_value <= low_threshold:
            color = "green"
        elif busy_value <= mid_threshold:
            color = "orange"
        else:
            color = "red"

        folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            popup=f"<b>{station_name}</b><br>Bezoekers: {busy_value:,.0f}",
            fill=True,
            fill_opacity=0.6,
            color=color
        ).add_to(m)
    else:
        print(f"Station niet gevonden: {station_name}")

# Weergeven in Streamlit
folium_static(m)
