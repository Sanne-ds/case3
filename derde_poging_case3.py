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

# Dictionary of { "StationName": (latitude, longitude) }
stations_dict = {
    row["Station"]: (row["Latitude"], row["Longitude"]) 
    for _, row in metro_stations_data.iterrows()
}

m = folium.Map(location=[51.509865, -0.118092], tiles='CartoDB positron', zoom_start=11)

# Loop through every station in AC2021_AnnualisedEntryExit
for idx, row in metro_data.iterrows():
    station_name = row["Station"]  # Adjust if your CSV column is named differently
    
    # Convert busy_value to a numeric type to avoid the string/int error
    busy_value = pd.to_numeric(row["AnnualisedEnEx"], errors="coerce")

    # Check if station exists in the dictionary to avoid KeyErrors
    if station_name in stations_dict:
        lat, lon = stations_dict[station_name]
        
        # Scale factor for the circle radius
        scale_factor = 1000
        radius = busy_value / scale_factor if pd.notnull(busy_value) else 2
        
        folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            popup=f"{station_name}: {busy_value:,}" if pd.notnull(busy_value) else station_name,
            fill=True,
            fill_opacity=0.6
        ).add_to(m)

folium_static(m)

import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd

# Data inladen
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

# Dictionary met station locaties
stations_dict = {
    row["Station"]: (row["Latitude"], row["Longitude"]) 
    for _, row in metro_stations_data.iterrows()
}

# **Dropdowns voor filtering**
dag_optie = st.selectbox(
    "Selecteer een dag:", 
    ["Weekdag (ma-do)", "Vrijdag", "Zaterdag", "Zondag"]
)

filter_optie = st.selectbox(
    "Filter op type passagiers:", 
    ["Beide", "Alleen Entry", "Alleen Exit"]
)

# **Koppeling tussen dag-opties en kolomnamen**
dag_kolommen = {
    "Weekdag (ma-do)": ("Weekday(Mon-Thu)Entries", "Weekday(Mon-Thu)Exits"),
    "Vrijdag": ("FridayEntries", "FridayExits"),
    "Zaterdag": ("SaturdayEntries", "SaturdayExits"),
    "Zondag": ("SundayEntries", "SundayExits"),
}

entry_kolom, exit_kolom = dag_kolommen[dag_optie]

# **Kaart maken**
m = folium.Map(location=[51.509865, -0.118092], tiles='CartoDB positron', zoom_start=11)

# Loop door de stations
for idx, row in metro_data.iterrows():
    station_name = row["Station"]
    
    # Entries en Exits ophalen en omzetten naar getallen
    entry_value = pd.to_numeric(row[entry_kolom], errors="coerce")
    exit_value = pd.to_numeric(row[exit_kolom], errors="coerce")

    # **Filter op dropdown-keuze**
    if filter_optie == "Beide":
        busy_value = (entry_value + exit_value) if pd.notnull(entry_value) and pd.notnull(exit_value) else None
    elif filter_optie == "Alleen Entry":
        busy_value = entry_value if pd.notnull(entry_value) else None
    elif filter_optie == "Alleen Exit":
        busy_value = exit_value if pd.notnull(exit_value) else None
    
    # **Marker toevoegen als station bestaat**
    if station_name in stations_dict and busy_value is not None:
        lat, lon = stations_dict[station_name]

        # Schaal factor voor radius
        scale_factor = 1000
        radius = busy_value / scale_factor if pd.notnull(busy_value) else 2
        
        folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            popup=f"{station_name}: {busy_value:,}",
            fill=True,
            fill_opacity=0.6
        ).add_to(m)

# **Kaart tonen in Streamlit**
folium_static(m)
