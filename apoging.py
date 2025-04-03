import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm
import plotly.express as px

# Data inladen
bestanden = ['2021_Q2_Central.csv', '2021_Q3_Central.csv', '2021_Q4_Central.csv']
fiets_data_jaar = pd.concat([pd.read_csv(file) for file in bestanden], ignore_index=True)

weer_data = pd.read_csv('weather_london.csv')
metro_data = pd.read_csv('AC2021_AnnualisedEntryExit.csv', sep=';')
metro_stations_data = pd.read_csv('London stations.csv')
tube_lines_data = pd.read_csv('London tube lines.csv')

# Tabs aanmaken
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🚇 Metro Stations en Lijnen",
    "🚲 Fietsverhuurstations",
    "🌤️ Weerdata",
    "🔧 Onderhoud",
    "📊 Ritduur per maand"
])

# --- 📊 BOX PLOT PER MAAND ---
with tab5:
    st.header("📊 Verdeling van ritduur per maand")

    # Bestandsnamen koppelen aan maanden
    file_names = [
        'bike_1klein.csv', 'bike_2klein.csv', 'bike_3klein.csv', 'bike_4klein.csv',
        'bike_5klein.csv', 'bike_6klein.csv', 'bike_7klein.csv', 'bike_8klein.csv',
        'bike_9klein.csv', 'bike_10klein.csv', 'bike_11klein.csv', 'bike_12klein.csv'
    ]
    
    month_names = [
        'January', 'February', 'March', 'April', 'May', 'June', 
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    # Data van alle maanden inladen en combineren
    dfs = []
    for i, file in enumerate(file_names):
        df = pd.read_csv(file, usecols=['Duration', 'Bike Id'])  # Laad alleen relevante kolommen
        df['Month'] = month_names[i]  # Voeg maandnaam toe
        dfs.append(df)
    
    all_months_data = pd.concat(dfs, ignore_index=True)

    # Boxplot maken
    plt.figure(figsize=(12, 6))
    sns.boxplot(x="Month", y="Duration", data=all_months_data, order=month_names)
    plt.xticks(rotation=45)
    plt.xlabel("Maand")
    plt.ylabel("Duur van een ritje (seconden)")
    plt.title("Boxplot van ritduur per maand")

    # Toon de plot in Streamlit
    st.pyplot(plt)
