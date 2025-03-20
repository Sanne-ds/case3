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

# Fix 'AnnualisedEnEx'
metro_data["AnnualisedEnEx"] = (
    metro_data["AnnualisedEnEx"]
    .astype(str)
    .str.replace(r"[^\d]", "", regex=True)
    .astype(float)
)

# Vermenigvuldig entries en exits met 1.000
entry_exit_cols = [
    "Weekday(Mon-Thu)Entries", "Weekday(Mon-Thu)Exits",
    "FridayEntries", "SaturdayEntries", "SundayEntries",
    "FridayExits", "SaturdayExits", "SundayExits"
]
metro_data[entry_exit_cols] = metro_data[entry_exit_cols] * 1000

# Bereken drempelwaardes
metro_data["TotalEnEx"] = metro_data[entry_exit_cols].sum(axis=1)
low_threshold = metro_data["TotalEnEx"].quantile(0.33)
mid_threshold = metro_data["TotalEnEx"].quantile(0.66)

# Tabs aanmaken
tab1, tab2, tab3 = st.tabs(["🚇 Metro Stations en Lijnen", "🚲 Fietsverhuurstations", "🌤️ Weerdata"])

with tab1:
    st.header("🚇 Metro Stations en Lijnen")
    with st.expander("⚙️ **Metro Filteropties**", expanded=True):
        filter_option = st.radio("**Toon data voor**", ["Weekdagen", "Weekend"])
        metro_data["FilteredEnEx"] = metro_data[["Weekday(Mon-Thu)Entries", "Weekday(Mon-Thu)Exits"]].sum(axis=1) if filter_option == "Weekdagen" else metro_data[["FridayEntries", "SaturdayEntries", "SundayEntries", "FridayExits", "SaturdayExits", "SundayExits"]].sum(axis=1)
        drukte_option = st.select_slider("**Selecteer drukte**", ["Alle", "Rustig", "Normaal", "Druk"], value="Alle")
    
    filtered_data = metro_data.copy()
    if drukte_option == "Rustig":
        filtered_data = metro_data[metro_data["FilteredEnEx"] <= low_threshold]
    elif drukte_option == "Normaal":
        filtered_data = metro_data[(metro_data["FilteredEnEx"] > low_threshold) & (metro_data["FilteredEnEx"] <= mid_threshold)]
    elif drukte_option == "Druk":
        filtered_data = metro_data[metro_data["FilteredEnEx"] > mid_threshold]
    
    m = folium.Map(location=[51.509865, -0.118092], tiles='CartoDB positron', zoom_start=11)
    folium_static(m)

with tab2:
    st.header("🚲 Fietsverhuurstations")
    df_cyclestations = pd.read_csv('cycle_stations.csv')
    df_cyclestations['installDateFormatted'] = pd.to_datetime(df_cyclestations['installDate'], unit='ms').dt.strftime('%d-%m-%Y')
    m = folium.Map(location=[51.5074, -0.1278], zoom_start=12)
    marker_cluster = MarkerCluster().add_to(m)
    folium_static(m)

with tab3:
    st.header("🌤️ Weerdata voor 2021")
    weer_data['Date'] = pd.to_datetime(weer_data['Unnamed: 0'], format='%Y-%m-%d')
    weer_data_2021 = weer_data[weer_data['Date'].dt.year == 2021]
    column_mapping = {
        'tavg': 'Gemiddelde Temperatuur (°C)', 'tmin': 'Minimale Temperatuur (°C)', 'tmax': 'Maximale Temperatuur (°C)',
        'prcp': 'Neerslag (mm)', 'snow': 'Sneeuwval (cm)', 'wdir': 'Windrichting (°)', 'wspd': 'Windsnelheid (m/s)',
        'wpgt': 'Windstoten (m/s)', 'pres': 'Luchtdruk (hPa)', 'tsun': 'Zonduur (uren)'
    }
    datum = st.date_input("Selecteer een datum in 2021", min_value=pd.to_datetime("2021-01-01"), max_value=pd.to_datetime("2021-12-31"))
    week_nummer = datum.isocalendar()[1]
    weer_data_2021['Week'] = weer_data_2021['Date'].dt.isocalendar().week
    filtered_data_week = weer_data_2021[weer_data_2021['Week'] == week_nummer]
    
    if not filtered_data_week.empty:
        st.write(f"Gegevens voor week {week_nummer} van 2021 (rondom {datum.strftime('%d-%m-%Y')}):")
        filtered_data_week = filtered_data_week.rename(columns=column_mapping)
        filtered_data_week_reset = filtered_data_week.reset_index(drop=True)
        filtered_data_week_reset.index = filtered_data_week_reset.index + 1
        st.dataframe(filtered_data_week_reset[['Date', 'Gemiddelde Temperatuur (°C)', 'Minimale Temperatuur (°C)', 'Maximale Temperatuur (°C)', 'Neerslag (mm)', 'Sneeuwval (cm)', 'Windrichting (°)', 'Windsnelheid (m/s)', 'Windstoten (m/s)', 'Luchtdruk (hPa)', 'Zonduur (uren)']])
    else:
        st.write(f"Geen gegevens gevonden voor week {week_nummer} van 2021.")
