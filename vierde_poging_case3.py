import pandas as pd

bestanden = [
    '2021_Q2_Central.csv',
    '2021_Q3_Central.csv',
    '2021_Q4_Central.csv'
]

dfs = [pd.read_csv(file) for file in bestanden]

fiets_data_jaar = pd.concat(dfs, ignore_index=True)
weer_data = pd.read_csv('weather_london.csv')
metro_data = pd.read_csv('AC2021_AnnualisedEntryExit.csv', sep = ';')
metro_stations_data = pd.read_csv('London stations.csv')

import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd

# Keuze dropdown
filter_optie = st.selectbox(
    "Filter op type passagiers:",
    ["Alle passagiers", "Ingangen", "Uitgangen"]
)

# Loop door stations en pas filtering toe
for idx, row in metro_data.iterrows():
    station_name = row["Station"]
    
    if station_name in stations_dict:
        lat, lon = stations_dict[station_name]

        # ✅ Kies de juiste dataset op basis van dropdown
        if filter_optie == "Ingangen":
            busy_value = pd.to_numeric(row["Weekday(Mon-Thu)Entries"], errors="coerce")
        elif filter_optie == "Uitgangen":
            busy_value = pd.to_numeric(row["Weekday(Mon-Thu)Exits"], errors="coerce")
        else:
            busy_value = pd.to_numeric(row["AnnualisedEnEx"], errors="coerce")  # Standaardwaarde

        # Alleen markers tonen als de waarde geldig is
        if pd.notnull(busy_value):
            scale_factor = 1000
            radius = busy_value / scale_factor

            folium.CircleMarker(
                location=[lat, lon],
                radius=radius,
                popup=f"{station_name}: {busy_value:,}",
                fill=True,
                fill_opacity=0.6
            ).add_to(m)
