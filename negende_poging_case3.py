import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import numpy as np  # Voor normalisatie van waarden

# Bestanden laden
bestanden = [
    '2021_Q2_Central.csv',
    '2021_Q3_Central.csv',
    '2021_Q4_Central.csv'
]

dfs = [pd.read_csv(file) for file in bestanden]
fiets_data_jaar = pd.concat(dfs, ignore_index=True)

weer_data = pd.read_csv('weather_london.csv')
metro_data = pd.read_csv('AC2021_AnnualisedEntryExit.csv', sep=';')
metro_stations_data = pd.read_csv('London stations.csv')

# Dictionary van { "StationName": (latitude, longitude) }
stations_dict = {
    row["Station"]: (row["Latitude"], row["Longitude"]) 
    for _, row in metro_stations_data.iterrows()
}

# 📌 Dropdown voor passagiersfilter (Entries, Exits, Beide)
filter_optie = st.selectbox(
    "Filter op type passagiers:",
    ["Beide", "Ingangen", "Uitgangen"]
)

# 📌 Dropdown voor de dagkeuze
dag_optie = st.selectbox(
    "Filter op dag:",
    ["Weekday(Mon-Thu)", "Friday", "Saturday", "Sunday"]
)

# Kolomnamen bepalen op basis van de gekozen dag
entries_col = dag_optie + "Entries"
exits_col = dag_optie + "Exits"

# Folium map aanmaken
m = folium.Map(location=[51.509865, -0.118092], tiles='CartoDB positron', zoom_start=11)

# 🚀 **Stap 1: Verzamel alle passagiersdata om dynamisch te schalen**
passagiers_values = []

for idx, row in metro_data.iterrows():
    if row["Station"] in stations_dict:
        if filter_optie == "Ingangen":
            busy_value = pd.to_numeric(row[entries_col], errors="coerce")
        elif filter_optie == "Uitgangen":
            busy_value = pd.to_numeric(row[exits_col], errors="coerce")
        else:  # Beide
            busy_value = pd.to_numeric(row[entries_col], errors="coerce") + pd.to_numeric(row[exits_col], errors="coerce")

        if pd.notnull(busy_value):
            passagiers_values.append(busy_value)

# Normaalwaarden berekenen voor schaal en kleur
if passagiers_values:
    min_value, max_value = min(passagiers_values), max(passagiers_values)
else:
    min_value, max_value = 0, 1  # Fallback als er geen data is

# 🚀 **Stap 2: Markers toevoegen met dynamische grootte en kleur**
for idx, row in metro_data.iterrows():
    station_name = row["Station"]

    if station_name in stations_dict:
        lat, lon = stations_dict[station_name]

        # Bereken busy_value op basis van filterkeuze
        if filter_optie == "Ingangen":
            busy_value = pd.to_numeric(row[entries_col], errors="coerce")
        elif filter_optie == "Uitgangen":
            busy_value = pd.to_numeric(row[exits_col], errors="coerce")
        else:
            busy_value = pd.to_numeric(row[entries_col], errors="coerce") + pd.to_numeric(row[exits_col], errors="coerce")

        if pd.notnull(busy_value):
            # 📌 **Dynamische schaalgrootte (grotere verschillen zichtbaar)**
            radius = np.interp(busy_value, [min_value, max_value], [5, 10])  # Min 5, max 50 px

            # 📌 **Kleuren instellen (groen → geel → rood)**
            color_scale = ['green', 'yellow', 'red']
            color_index = int(np.interp(busy_value, [min_value, max_value], [0, 2]))  # 0 = groen, 2 = rood
            color = color_scale[color_index]

            folium.CircleMarker(
                location=[lat, lon],
                radius=radius,
                popup=f"{station_name}: {busy_value:,}",
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.6
            ).add_to(m)

# Folium kaart weergeven in Streamlit
folium_static(m)
