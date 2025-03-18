import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd

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

# 📌 Dropdown voor het filteren van passagiers (Entries, Exits, Beide)
filter_optie = st.selectbox(
    "Filter op type passagiers:",
    ["Beide", "Ingangen", "Uitgangen"]
)

# 📌 Dropdown voor het filteren per dag
dag_optie = st.selectbox(
    "Filter op dag:",
    ["Weekday(Mon-Thu)", "Friday", "Saturday", "Sunday"]
)

# Kolomnamen bepalen op basis van de gekozen dag
entries_col = dag_optie + "Entries"
exits_col = dag_optie + "Exits"

# Folium map aanmaken
m = folium.Map(location=[51.509865, -0.118092], tiles='CartoDB positron', zoom_start=11)

# Stations doorlopen en filtering toepassen
for idx, row in metro_data.iterrows():
    station_name = row["Station"]

    # Check of het station in het dictionary staat
    if station_name in stations_dict:
        lat, lon = stations_dict[station_name]

        # Kies de juiste dataset op basis van de dropdown
        if filter_optie == "Ingangen":
            busy_value = pd.to_numeric(row[entries_col], errors="coerce")
        elif filter_optie == "Uitgangen":
            busy_value = pd.to_numeric(row[exits_col], errors="coerce")
        else:  # Beide
            busy_value = pd.to_numeric(row[entries_col], errors="coerce") + pd.to_numeric(row[exits_col], errors="coerce")

        # Alleen markers tonen als de waarde geldig is
        if pd.notnull(busy_value):
            scale_factor = 1000
            radius = busy_value / scale_factor  # Schaal factor

            folium.CircleMarker(
                location=[lat, lon],
                radius=radius,
                popup=f"{station_name}: {busy_value:,}",
                fill=True,
                fill_opacity=0.6
            ).add_to(m)

# Folium kaart weergeven in Streamlit
folium_static(m)
