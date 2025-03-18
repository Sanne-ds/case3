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

# 📌 Debugging: toon voorbeeld data
st.write("Voorbeeld data uit metro_data:")
st.write(metro_data[[entries_col, exits_col]].head())

# 📌 Lege lijst voor alle waarden (voor kleurberekening)
passagiers_values = []

# **Stap 1: Filter alleen stations die we kennen**
valid_metro_data = metro_data[metro_data["Station"].isin(stations_dict.keys())]

for _, row in valid_metro_data.iterrows():
    # **Ver
