import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

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
    .astype(str)                      # Zet om naar string om bewerkingen uit te voeren
    .str.replace(r"[^\d]", "", regex=True)  # Verwijder ALLES wat geen cijfer is
    .astype(float)                    # Zet om naar float
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

# Streamlit interface
st.sidebar.title("Wat zou je willen zien?")
filter_option = st.sidebar.radio("Toon data voor:", ["Weekdagen", "Weekend"])

if filter_option == "Weekdagen":
    metro_data["FilteredEnEx"] = metro_data[["Weekday(Mon-Thu)Entries", "Weekday(Mon-Thu)Exits"]].sum(axis=1)
else:
    metro_data["FilteredEnEx"] = metro_data[["FridayEntries", "SaturdayEntries", "SundayEntries", "FridayExits", "SaturdayExits", "SundayExits"]].sum(axis=1)

# Slider voor filteren op drukte
min_val, max_val = st.sidebar.slider(
    "Selecteer bezoekersaantal",
    int(metro_data["FilteredEnEx"].min()),
    int(metro_data["FilteredEnEx"].max()),
    (int(metro_data["FilteredEnEx"].min()), int(metro_data["FilteredEnEx"].max()))
)

# Filter de data op basis van de sliderwaarden
filtered_data = metro_data[(metro_data["FilteredEnEx"] >= min_val) & (metro_data["FilteredEnEx"] <= max_val)]

# Titel voor de checkboxen
st.sidebar.subheader("Toon op de kaart")

# Checkboxen voor het tonen van stations en tube lines
show_stations = st.sidebar.checkbox("Metro stations en bezoekersaantal", value=True)
show_tube_lines = st.sidebar.checkbox("Metro lijnen", value=True)

# Tabs aanmaken
tab1, tab2 = st.tabs(["Metro Stations en Lijnen", "Fietsverhuurstations"])

with tab1:
    # Kaart aanmaken
    m = folium.Map(location=[51.509865, -0.118092], tiles='CartoDB positron', zoom_start=11)

    # Metro stations plotten
    if show_stations:
        for _, row in filtered_data.iterrows():
            station_name = row["Station"]
            busy_value = row["FilteredEnEx"]

            if station_name in stations_dict and pd.notnull(busy_value):
                lat, lon = stations_dict[station_name]
                radius = 5  # Statische grootte voor alle stippen

                # Kleur bepalen op basis van globale drempels
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
                print(f"Station niet gevonden of buiten bereik: {station_name}")

    # Define colors for each tube line
    line_colors = {
        "Bakerloo": "brown",
        "Central": "red",
        "Circle": "yellow",
        "District": "green",
        "Hammersmith and City": "pink",
        "Jubilee": "silver",
        "Metropolitan": "purple",
        "Northern": "black",
        "Piccadilly": "blue",
        "Victoria": "lightblue",
        "Waterloo and City": "turquoise",
        "Overground": "orange",
        "C2C": "darkblue",
        "DLR": "teal",
        "Elizabeth": "magenta",
        "Thameslink": "pink",
        "Southern": "chocolate",
        "Southeastern": "maroon",
        "South Western": "navy",
        "Tramlink": "lime",
        "Great Northern": "darkred",
        "Greater Anglia": "darkorange",
        "Heathrow Express": "gold",
        "Liberty": "lightgray",
        "Lioness": "darkgray",
        "Mildmay": "cyan",
        "Suffragette": "purple",
        "Windrush": "darkcyan",
        "Weaver": "olive",
    }

    # Tube lines plotten
    if show_tube_lines:
        for idx, row in tube_lines_data.iterrows():
            from_station = row["From Station"]
            to_station = row["To Station"]
            tube_line = row["Tube Line"]

            if from_station in stations_dict and to_station in stations_dict:
                lat_lon1 = stations_dict[from_station]
                lat_lon2 = stations_dict[to_station]

                line_color = line_colors.get(tube_line, "gray")

                folium.PolyLine(
                    locations=[lat_lon1, lat_lon2],
                    color=line_color,
                    weight=2.5,
                    opacity=0.8,
                    tooltip=f"{tube_line}: {from_station} ↔ {to_station}"
                ).add_to(m)

    # Weergeven in Streamlit
    folium_static(m)

with tab2:
    # Laad de bestanden
    df_cyclestations = pd.read_csv('cycle_stations.csv')

    # Zet de Unix timestamp om naar een datum in 'dd-mm-yyyy' formaat
    df_cyclestations['installDateFormatted'] = pd.to_datetime(df_cyclestations['installDate'], unit='ms').dt.strftime('%d-%m-%Y')

    # Create Streamlit app layout
    st.title('London Cycle Stations')
    st.markdown("Interaktive map met fietsverhuurstations in Londen")

    # Voeg een slider toe om het aantal fietsen in te stellen
    bike_slider = st.slider("Selecteer het aantal beschikbare fietsen", 0, 100, 0)

    # Maak een basemap van Londen
    m = folium.Map(location=[51.5074, -0.1278], zoom_start=12)

    # MarkerCluster om stations te groeperen
    marker_cluster = MarkerCluster().add_to(m)

    # Voeg de stations toe aan de kaart
    for index, row in df_cyclestations.iterrows():
        lat = row['lat']
        long = row['long']
        station_name = row['name']
        nb_bikes = row['nbBikes']  # Aantal fietsen
        nb_standard_bikes = row['nbStandardBikes']  # Aantal standaardfietsen
        nb_ebikes = row['nbEBikes']  # Aantal ebikes
        install_date = row['installDateFormatted']  # De geformatteerde installatiedatum

        # Voeg een marker toe met info over het station
        if nb_bikes >= bike_slider:  # Controleer of het aantal fietsen groter of gelijk is aan de slider
            folium.Marker(
                location=[lat, long],
                popup=folium.Popup(f"Station: {station_name}<br>Aantal fietsen: {nb_bikes}<br>Standaard: {nb_standard_bikes}<br>EBikes: {nb_ebikes}<br>Installatiedatum: {install_date}", max_width=300),
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(marker_cluster)

    # Render de kaart in de Streamlit app
    folium_static(m)
