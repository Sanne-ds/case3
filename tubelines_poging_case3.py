import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
from datetime import datetime

# Data inladen
bestanden = ['2021_Q2_Central.csv', '2021_Q3_Central.csv', '2021_Q4_Central.csv']
fiets_data_jaar = pd.concat([pd.read_csv(file) for file in bestanden], ignore_index=True)

weer_data = pd.read_csv('weather_london.csv')
metro_data = pd.read_csv('AC2021_AnnualisedEntryExit.csv', sep=';')
metro_stations_data = pd.read_csv('London stations.csv')
tube_lines_data = pd.read_csv('London tube lines.csv')

# Coördinaten dictionary
stations_dict = {
    row["Station"]: (row["Latitude"], row["Longitude"]) 
    for _, row in metro_stations_data.iterrows()
}

# Fix 'AnnualisedEnEx' (verwijder niet-numerieke tekens en zet om naar float)
metro_data["AnnualisedEnEx"] = (
    metro_data["AnnualisedEnEx"]
    .astype(str)
    .str.replace(r"[^\d]", "", regex=True)
    .astype(float)
)

# Vermenigvuldig de Entries en Exits met 1.000 om juiste aantallen te krijgen
entry_exit_cols = [
    "Weekday(Mon-Thu)Entries", "Weekday(Mon-Thu)Exits",
    "FridayEntries", "SaturdayEntries", "SundayEntries",
    "FridayExits", "SaturdayExits", "SundayExits"
]
metro_data[entry_exit_cols] = metro_data[entry_exit_cols] * 1000

# Bereken totale drempelwaardes over alle data
metro_data["TotalEnEx"] = metro_data[entry_exit_cols].sum(axis=1)

low_threshold = metro_data["TotalEnEx"].quantile(0.33)
mid_threshold = metro_data["TotalEnEx"].quantile(0.66)

# Tabs aanmaken
tab1, tab2, tab3 = st.tabs(["🚇 Metro Stations en Lijnen", "🚲 Fietsverhuurstations", "☀️ Weerdata"])

with tab1:
    st.header("🚇 Metro Stations en Lijnen")

    with st.expander("⚙️ **Metro Filteropties**", expanded=True):
        filter_option = st.radio("**Toon data voor**", ["Weekdagen", "Weekend"])

        if filter_option == "Weekdagen":
            metro_data["FilteredEnEx"] = metro_data[["Weekday(Mon-Thu)Entries", "Weekday(Mon-Thu)Exits"]].sum(axis=1)
        else:
            metro_data["FilteredEnEx"] = metro_data[["FridayEntries", "SaturdayEntries", "SundayEntries", "FridayExits", "SaturdayExits", "SundayExits"]].sum(axis=1)

        drukte_option = st.select_slider(
            "**Selecteer drukte**",
            options=["Alle", "Rustig", "Normaal", "Druk"],
            value="Alle"
        )

        if drukte_option == "Rustig":
            filtered_data = metro_data[metro_data["FilteredEnEx"] <= low_threshold]
        elif drukte_option == "Normaal":
            filtered_data = metro_data[(metro_data["FilteredEnEx"] > low_threshold) & (metro_data["FilteredEnEx"] <= mid_threshold)]
        elif drukte_option == "Druk":
            filtered_data = metro_data[metro_data["FilteredEnEx"] > mid_threshold]
        else:
            filtered_data = metro_data

        st.write("**Kies visualisatie**")
        show_stations = st.checkbox("Metro stations en bezoekersaantal", value=True)
        show_tube_lines = st.checkbox("Metro lijnen", value=True)

    m = folium.Map(location=[51.509865, -0.118092], tiles='CartoDB positron', zoom_start=11)

    if show_stations:
        for _, row in filtered_data.iterrows():
            station_name = row["Station"]
            busy_value = row["FilteredEnEx"]

            if station_name in stations_dict and pd.notnull(busy_value):
                lat, lon = stations_dict[station_name]
                radius = 5

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

    folium_static(m)

with tab2:
    st.header("🚲 Fietsverhuurstations")

    with st.expander("⚙️ **Fiets Filteropties**", expanded=True):
        bike_slider = st.slider("**Selecteer het minimum aantal beschikbare fietsen**", 0, 100, 0)

    df_cyclestations = pd.read_csv('cycle_stations.csv')
    df_cyclestations['installDateFormatted'] = pd.to_datetime(df_cyclestations['installDate'], unit='ms').dt.strftime('%d-%m-%Y')

    m = folium.Map(location=[51.5074, -0.1278], zoom_start=12)
    marker_cluster = MarkerCluster().add_to(m)

    for index, row in df_cyclestations.iterrows():
        if row['nbBikes'] >= bike_slider:
            folium.Marker(
                location=[row['lat'], row['long']],
                popup=f"Station: {row['name']}\nFietsen: {row['nbBikes']}",
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(marker_cluster)

    folium_static(m)

with tab3:
    st.header("☀️ Weerdata voor 2021")
    weer_data['Date'] = pd.to_datetime(weer_data['Unnamed: 0'], format='%Y-%m-%d')
    datum = st.date_input("Selecteer een datum in 2021", min_value=pd.to_datetime("2021-01-01"), max_value=pd.to_datetime("2021-12-31"))
    week_nummer = datum.isocalendar()[1]
    weer_data['Week'] = weer_data['Date'].dt.isocalendar().week
    filtered_data_week = weer_data[weer_data['Week'] == week_nummer]
    filtered_data_week['Date'] = filtered_data_week['Date'].dt.strftime('%-d %B %Y')
    st.dataframe(filtered_data_week)
