import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import numpy as np  

# 📌 CSV-bestanden inlezen
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

# 📌 Dictionary van { "StationName": (latitude, longitude) }
stations_dict = {
    row["Station"]: (row["Latitude"], row["Longitude"]) 
    for _, row in metro_stations_data.iterrows()
}

# 📌 Dropdowns toevoegen
filter_optie = st.selectbox(
    "Filter op type passagiers:",
    ["Beide", "Ingangen", "Uitgangen"]
)

dag_optie = st.selectbox(
    "Filter op dag:",
    ["Weekday(Mon-Thu)", "Friday", "Saturday", "Sunday"]
)

# 📌 Bepaal kolomnamen per dagkeuze
entries_col = dag_optie + "Entries"
exits_col = dag_optie + "Exits"

# 📌 Lege lijst voor alle waarden (voor kleurberekening)
passagiers_values = []

# Stap 1: **Alleen geldige stations bekijken**
valid_metro_data = metro_data[metro_data["Station"].isin(stations_dict.keys())]

for _, row in valid_metro_data.iterrows():
    if filter_optie == "Ingangen":
        busy_value = pd.to_numeric(row[entries_col], errors="coerce")
    elif filter_optie == "Uitgangen":
        busy_value = pd.to_numeric(row[exits_col], errors="coerce")
    else:  # Beide
        busy_value = pd.to_numeric(row[entries_col], errors="coerce") + pd.to_numeric(row[exits_col], errors="coerce")

    if pd.notnull(busy_value):
        passagiers_values.append(busy_value)

# **Stap 2: Kleurberekening corrigeren**
if passagiers_values:
    min_value, max_value = min(passagiers_values), max(passagiers_values)
else:
    min_value, max_value = 0, 1  # Fall-back bij lege data

# **Stap 3: Kaart genereren**
m = folium.Map(location=[51.509865, -0.118092], tiles='CartoDB positron', zoom_start=11)

for _, row in valid_metro_data.iterrows():
    station_name = row["Station"]
    lat, lon = stations_dict[station_name]

    if filter_optie == "Ingangen":
        busy_value = pd.to_numeric(row[entries_col], errors="coerce")
    elif filter_optie == "Uitgangen":
        busy_value = pd.to_numeric(row[exits_col], errors="coerce")
    else:
        busy_value = pd.to_numeric(row[entries_col], errors="coerce") + pd.to_numeric(row[exits_col], errors="coerce")

    if pd.notnull(busy_value):
        # 🚀 **Houd de radius vast op 8 pixels**
        radius = 8  # Vaste grootte

        # 📌 **Kleuren fix**: Normaliseren naar groen-geel-rood
        color_scale = ['green', 'yellow', 'red']
        color_index = int(np.interp(busy_value, [min_value, max_value], [0, 2]))
        color = color_scale[color_index]

        # **Popup met stationnaam en waarde**
        popup_text = f"{station_name}: {busy_value:,.0f} passagiers"

        folium.CircleMarker(
            location=[lat, lon],
            radius=radius,  # 🎯 Vaste grootte
            popup=popup_text,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8
        ).add_to(m)

# **Kaart tonen in Streamlit**
folium_static(m)
