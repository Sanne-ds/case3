import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm
import plotly.express as px
import plotly.graph_objects as go

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
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚇 Metro Stations en Lijnen", "🚲 Fietsverhuurstation", "🚴 Ritjes", "🔧 Onderhoud", "🌤️ Weerdata"])

with tab1:
    st.header("🚇 Metro Stations en Lijnen")

    with st.expander("⚙ *Metro Filteropties*", expanded=True):
        filter_option = st.radio("*Toon data voor*", ["Weekdagen", "Weekend"])

        if filter_option == "Weekdagen":
            metro_data["FilteredEnEx"] = metro_data[["Weekday(Mon-Thu)Entries", "Weekday(Mon-Thu)Exits"]].sum(axis=1)
        else:
            metro_data["FilteredEnEx"] = metro_data[["FridayEntries", "SaturdayEntries", "SundayEntries", "FridayExits", "SaturdayExits", "SundayExits"]].sum(axis=1)

        # Select slider voor drukte
        drukte_option = st.select_slider(
            "*Selecteer drukte*",
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

        st.write("*Kies visualisatie*")
        show_stations = st.checkbox("Metro stations en bezoekersaantal", value=True)
        show_tube_lines = st.checkbox("Metro lijnen", value=True)

    # Metro kaart renderen...
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

    if show_tube_lines:
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

    folium_static(m)

with tab2:
    
    st.header("🚲 Fietsverhuurstations")

    with st.expander("⚙ *Fiets Filteropties*", expanded=True):
        bike_slider = st.slider("*Selecteer het minimum aantal beschikbare fietsen*", 0, 100, 0)

    df_cyclestations = pd.read_csv('cycle_stations.csv')
    df_cyclestations['installDateFormatted'] = pd.to_datetime(df_cyclestations['installDate'], unit='ms').dt.strftime('%d-%m-%Y')

    m = folium.Map(location=[51.5074, -0.1278], zoom_start=12)
    marker_cluster = MarkerCluster().add_to(m)

    for index, row in df_cyclestations.iterrows():
        lat, long, station_name = row['lat'], row['long'], row['name']
        nb_bikes, nb_standard_bikes, nb_ebikes = row['nbBikes'], row['nbStandardBikes'], row['nbEBikes']
        install_date = row['installDateFormatted']

        if nb_bikes >= bike_slider:
            folium.Marker(
                location=[lat, long],
                popup=folium.Popup(f"Station: {station_name}<br>Aantal fietsen: {nb_bikes}<br>Standaard: {nb_standard_bikes}<br>EBikes: {nb_ebikes}<br>Installatiedatum: {install_date}", max_width=300),
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(marker_cluster)

    folium_static(m)

    # Hieronder komt de nieuwe code die je vroeg:
    # Bereken het totaal aantal fietsen, standaard fietsen, en ebikes
    total_bikes = df_cyclestations['nbBikes'].sum()
    total_standard_bikes = df_cyclestations['nbStandardBikes'].sum()
    total_ebikes = df_cyclestations['nbEBikes'].sum()
    
     # Bereken de percentages van de standaard fietsen en ebikes
    percentage_standard_bikes = (total_standard_bikes / total_bikes * 100) if total_bikes > 0 else 0
    percentage_ebikes = (total_ebikes / total_bikes * 100) if total_bikes > 0 else 0
    
     # Toont de percentages in vakjes onderaan de pagina
    st.write("### Percentage Fietsen")
    
     # Maak twee kolommen voor de percentages
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Standaard Fietsen", f"{total_standard_bikes} fietsen", f"{percentage_standard_bikes:.2f}%")
     
    with col2:
        st.metric("Elektrische Fietsen", f"{total_ebikes} fietsen", f"{percentage_ebikes:.2f}%")

with tab3:
    
    # Streamlit titel
    st.header("🚴 Ritjes")
    
    # Lijst van maandnamen in het Nederlands
    maandnamen = [
        'Januari', 'Februari', 'Maart', 'April', 'Mei', 'Juni', 
        'Juli', 'Augustus', 'September', 'Oktober', 'November', 'December'
    ]
    
    # Maak lege lijsten voor de gemiddelde duur en het aantal ritjes per maand
    average_durations = []
    ride_counts = []
    
    # Itereer door de bestanden bike_1klein t/m bike_12klein
    for i in range(1, 13):
        # Bestandsnaam opbouwen
        file_name = f'bike_{i}klein.csv'
        
        # Lees het CSV-bestand in een DataFrame
        df = pd.read_csv(file_name)
        
        # Bereken de gemiddelde 'Duration' in minuten
        avg_duration_minutes = df['Duration'].mean() / 60  # Omrekenen van seconden naar minuten
        average_durations.append(avg_duration_minutes)
        
        # Tel het aantal ritjes (aantal rijen in de DataFrame)
        ride_count = len(df)
        ride_counts.append(ride_count)
    
    # Maak een DataFrame met maandnamen, gemiddelde duur en het aantal ritjes
    avg_df = pd.DataFrame({
        'Month': maandnamen,  # Gebruik maandnamen in plaats van nummers
        'Average Duration (Minutes)': average_durations,
        'Ride Count': ride_counts
    })
    
    # Dropdown menu voor de grafiekkeuze
    option = st.selectbox("Selecteer een optie:", ['Gemiddelde duur', 'Aantal ritjes', 'Beide'])
    
    if option == 'Gemiddelde duur':
        # Maak een Plotly lijn plot van de gemiddelde duur per maand in minuten
        fig_avg_duration = go.Figure()
        fig_avg_duration.add_trace(go.Scatter(
            x=avg_df['Month'], 
            y=avg_df['Average Duration (Minutes)'], 
            mode='lines+markers',
            name='Gemiddelde Duur (Minuten)'
        ))
        fig_avg_duration.update_layout(
            title='Gemiddelde ritjesduur (Minuten)',
            xaxis_title='Maand',
            yaxis_title='Gemiddelde Duur (Minuten)',
            xaxis=dict(type='category', tickangle=45),
            yaxis=dict(range=[10, 30])
        )
        st.plotly_chart(fig_avg_duration)
    
    elif option == 'Aantal ritjes':
        # Maak een Plotly lijn plot van het aantal ritjes per maand
        fig_ride_count = go.Figure()
        fig_ride_count.add_trace(go.Scatter(
            x=avg_df['Month'], 
            y=avg_df['Ride Count'], 
            mode='lines+markers',
            name='Aantal Ritjes'
        ))
        fig_ride_count.update_layout(
            title='Aantal Ritjes per Maand',
            xaxis_title='Maand',
            yaxis_title='Aantal Ritjes',
            xaxis=dict(type='category', tickangle=45)
        )
        st.plotly_chart(fig_ride_count)
    
    elif option == 'Beide':
        # Maak een gecombineerde grafiek met dubbele y-assen
        fig_combined = go.Figure()
    
        # Lijn voor gemiddelde duur
        fig_combined.add_trace(go.Scatter(
            x=avg_df['Month'], 
            y=avg_df['Average Duration (Minutes)'], 
            mode='lines+markers',
            name='Gemiddelde Duur (Minuten)',
            yaxis='y1'
        ))
    
        # Lijn voor aantal ritjes
        fig_combined.add_trace(go.Scatter(
            x=avg_df['Month'], 
            y=avg_df['Ride Count'], 
            mode='lines+markers',
            name='Aantal Ritjes',
            yaxis='y2'
        ))
    
        # Layout instellen met dubbele y-assen
        fig_combined.update_layout(
            title='Gemiddelde Duur en Aantal Ritjes per Maand',
            xaxis=dict(title='Maand', type='category', tickangle=45),
            yaxis=dict(title='Gemiddelde Duur (Minuten)', side='left', range=[10, 30]),
            yaxis2=dict(title='Aantal Ritjes', side='right', overlaying='y'),
            legend=dict(x=0.5, y=-0.2, orientation='h')
        )
        st.plotly_chart(fig_combined)

with tab4:
       # Functie om de grafiek te plotten op basis van het geselecteerde bestand
    def plot_bike_data(month_name):
        if month_name == 'All year':
            # Alle bestanden laden en samenvoegen
            all_data = pd.concat([pd.read_csv(file) for file in file_month_dict.values()])
            
            # Bereken de totale huurduur en het aantal verhuur per Bike Id voor het hele jaar
            bike_duration = all_data.groupby('Bike Id').agg(
                total_duration=('Duration', 'sum'),
                rental_count=('Bike Id', 'count')
            ).reset_index()
    
            # Sorteer de resultaten op basis van het aantal verhuur (hoe vaker verhuurd, hoe hoger de ranking)
            bike_duration_sorted = bike_duration.sort_values(by='rental_count', ascending=False)
    
            # Selecteer de top 20 Bike Id's die het vaakst verhuurd zijn
            top_20_bike_ids = bike_duration_sorted.head(20)
    
            # Zet de totale duur om van seconden naar uren
            top_20_bike_ids.loc[:, 'total_duration_hours'] = top_20_bike_ids['total_duration'] / 3600
    
            # Plot een histogram van de top 20 Bike Id's op basis van het aantal verhuur (y-as schaal mag dynamisch zijn)
            plt.figure(figsize=(10,6))
            plt.bar(top_20_bike_ids['Bike Id'].astype(str), top_20_bike_ids['rental_count'])
            plt.xlabel('Bike ID')
            plt.ylabel('Aantal Verhuur')
            plt.title(f'De meest gebruikte fietsen van het jaar')
            plt.xticks(rotation=90)
            
        else:
            # Laad de geselecteerde maand
            file_name = file_month_dict[month_name]
            df = pd.read_csv(file_name)
    
            # Bereken de totale huurduur en het aantal verhuur per Bike Id
            bike_duration = df.groupby('Bike Id').agg(
                total_duration=('Duration', 'sum'),
                rental_count=('Bike Id', 'count')
            ).reset_index()
    
            # Sorteer de resultaten op basis van de totale huurduur in aflopende volgorde
            bike_duration_sorted = bike_duration.sort_values(by='total_duration', ascending=False)
    
            # Selecteer de top 20 Bike Id's die het langst verhuurd zijn
            top_20_bike_ids = bike_duration_sorted.head(20)
    
            # Zet de totale duur om van seconden naar uren
            top_20_bike_ids.loc[:, 'total_duration_hours'] = top_20_bike_ids['total_duration'] / 3600
    
            # Plot een histogram van de top 20 Bike Id's op basis van de totale huurduur (in uren)
            plt.figure(figsize=(10,6))
            plt.bar(top_20_bike_ids['Bike Id'].astype(str), top_20_bike_ids['total_duration_hours'])
            plt.xlabel('Bike ID')
            plt.ylabel('Aantal uur gebruikt')
            plt.title(f'Meest gebruikte fietsen in ({month_name})')
            plt.xticks(rotation=90)
    
            # Zet de limieten van de y-as vast (bijvoorbeeld van 0 tot 250 uur)
            plt.ylim(0, 250)
    
        # Toon de plot
        st.pyplot(plt)
    
    # Lijst van bestandsnamen en maandnamen
    file_names = ['bike_1klein.csv', 'bike_2klein.csv', 'bike_3klein.csv', 'bike_4klein.csv', 
                  'bike_5klein.csv', 'bike_6klein.csv', 'bike_7klein.csv', 'bike_8klein.csv', 
                  'bike_9klein.csv', 'bike_10klein.csv', 'bike_11klein.csv', 'bike_12klein.csv']
    
    # Maandnamen voor de dropdown, inclusief de optie 'All year'
    month_names = ['All year', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 
                   'September', 'October', 'November', 'December']
    
    # Maak een dictionary om bestanden te koppelen aan maandnamen
    file_month_dict = dict(zip(month_names[1:], file_names))  # Skip 'All year' voor file mapping
    
    # Streamlit interface
    st.header('🔧 Tijd voor wat olie op de ketting')
    
    # Dropdown menu voor maandselectie
    month_name = st.selectbox('Selecteer een maand:', month_names)
    
    # Plot de grafiek op basis van de geselecteerde maand
    plot_bike_data(month_name)

with tab5:
    
    st.header("🌤️ Weerdata voor 2021")

 
    # Zet de 'Unnamed: 0' kolom om naar een datetime-object
    weer_data['Date'] = pd.to_datetime(weer_data['Unnamed: 0'], format='%Y-%m-%d')

    # Zet de datum in de fietsdata correct
    fiets_rentals = pd.read_csv('fietsdata2021_rentals_by_day.csv')
    fiets_rentals["Day"] = pd.to_datetime(fiets_rentals["Day"])

    # Merge de weerdata en fietsdata op datum
    weer_data = pd.merge(weer_data, fiets_rentals[['Day', 'Total Rentals']], left_on='Date', right_on='Day', how='left')

    # Filter de data voor 2021
    weer_data_2021 = weer_data[weer_data['Date'].dt.year == 2021]

    # Vertaling van kolomnamen
    column_mapping = {
        'Total Rentals': 'Aantal Verhuurde Fietsen',
        'tavg': 'Gemiddelde Temperatuur (°C)',
        'tmin': 'Minimale Temperatuur (°C)',
        'tmax': 'Maximale Temperatuur (°C)',
        'prcp': 'Neerslag (mm)',
        'snow': 'Sneeuwval (cm)',
        'wdir': 'Windrichting (°)',
        'wspd': 'Windsnelheid (m/s)',
        'wpgt': 'Windstoten (m/s)',
        'pres': 'Luchtdruk (hPa)',
        'tsun': 'Zonduur (uren)'
    }

    # Kalender om een specifieke datum te kiezen
    datum = st.date_input("*Selecteer een datum in 2021*", min_value=pd.to_datetime("2021-01-01"), max_value=pd.to_datetime("2021-12-31"))

    # Haal het weeknummer van de geselecteerde datum op
    week_nummer = datum.isocalendar()[1]

    # Filter de data voor de geselecteerde week
    weer_data_2021['Week'] = weer_data_2021['Date'].dt.isocalendar().week
    filtered_data_week = weer_data_2021[weer_data_2021['Week'] == week_nummer]

    # Toon de gegevens voor de geselecteerde week
    if not filtered_data_week.empty:
        st.write(f"Gegevens voor week {week_nummer} van 2021 (rondom {datum.strftime('%d-%m-%Y')}):")

        # Vervang kolomnamen met de vertaalde versie
        filtered_data_week = filtered_data_week.rename(columns=column_mapping)

        # Reset de index en voeg de aangepaste index toe die begint bij 1
        filtered_data_week_reset = filtered_data_week.reset_index(drop=True)
        filtered_data_week_reset.index = filtered_data_week_reset.index + 1  # Start index vanaf 1

        # Datum formatteren
        filtered_data_week_reset['Date'] = filtered_data_week_reset['Date'].dt.strftime('%d %B %Y')

        # Kolommen herschikken om "Aantal Verhuurde Fietsen" direct na de datum te zetten
        kolommen = ['Date', 'Aantal Verhuurde Fietsen', 'Gemiddelde Temperatuur (°C)', 'Minimale Temperatuur (°C)', 
                    'Maximale Temperatuur (°C)', 'Neerslag (mm)', 'Sneeuwval (cm)', 'Windrichting (°)', 
                    'Windsnelheid (m/s)', 'Windstoten (m/s)', 'Luchtdruk (hPa)', 'Zonduur (uren)']
        

    else:
        st.write(f"Geen gegevens gevonden voor week {week_nummer} van 2021.")


    # Selectbox om grafieken te kiezen
    grafiek_keuze = st.selectbox('Kies welke grafiek je wilt zien:', 
                                 ['Aantal Verhuurde Fietsen per Dag', 
                                  'Gemiddelde Temperatuur per Dag', 
                                  'Neerslag per Dag', 
                                  'Sneeuwval per Dag'])

    # Toon de gekozen grafiek
    if grafiek_keuze == 'Aantal Verhuurde Fietsen per Dag':
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.lineplot(data=filtered_data_week_reset, x='Date', y='Aantal Verhuurde Fietsen', marker='o', ax=ax, color='blue')
        ax.set_xlabel("Datum")
        ax.set_ylabel("Aantal Verhuurde Fietsen", color='blue')
        ax.set_title(f"Aantal Verhuurde Fietsen per Dag in Week {week_nummer}")
        ax.tick_params(axis='y', labelcolor='blue')
        
        # Stel de limieten van de y-as in zodat er altijd 2000 extra ruimte is
        min_fietsen = filtered_data_week_reset['Aantal Verhuurde Fietsen'].min()
        max_fietsen = filtered_data_week_reset['Aantal Verhuurde Fietsen'].max()
        ax.set_ylim(min_fietsen - 2000, max_fietsen + 2000)  # 2000 extra ruimte onder en boven de data
        
        plt.xticks(rotation=45)
        st.pyplot(fig)

    elif grafiek_keuze == 'Gemiddelde Temperatuur per Dag':
        fig, ax1 = plt.subplots(figsize=(10, 6))
        # Plot voor Gemiddelde Temperatuur aan de linker y-as
        sns.lineplot(data=filtered_data_week_reset, x='Date', y='Gemiddelde Temperatuur (°C)', marker='o', ax=ax1, color='orange')
        ax1.set_xlabel("Datum")
        ax1.set_ylabel("Gemiddelde Temperatuur (°C)", color='orange')
        ax1.tick_params(axis='y', labelcolor='orange')

        # Stel de limieten van de y-as voor Temperatuur in zodat er altijd 2 extra ruimte is
        min_temp = filtered_data_week_reset['Gemiddelde Temperatuur (°C)'].min()
        max_temp = filtered_data_week_reset['Gemiddelde Temperatuur (°C)'].max()
        ax1.set_ylim(min_temp - 2, max_temp + 2)  # 2 extra ruimte onder en boven de data

        # Maak een tweede y-as voor Aantal Verhuurde Fietsen
        ax2 = ax1.twinx()
        sns.lineplot(data=filtered_data_week_reset, x='Date', y='Aantal Verhuurde Fietsen', marker='o', ax=ax2, color='blue', label='Aantal Verhuurde Fietsen')
        ax2.set_ylabel("Aantal Verhuurde Fietsen", color='blue')
        ax2.tick_params(axis='y', labelcolor='blue')

        ax1.set_title(f"Gemiddelde Temperatuur en Aantal Verhuurde Fietsen per Dag in Week {week_nummer}")
        plt.xticks(rotation=45)
        st.pyplot(fig)

    elif grafiek_keuze == 'Neerslag per Dag':
        fig, ax1 = plt.subplots(figsize=(10, 6))
        # Plot voor Neerslag aan de linker y-as
        sns.barplot(data=filtered_data_week_reset, x='Date', y='Neerslag (mm)', ax=ax1, color='blue')
        ax1.set_xlabel("Datum")
        ax1.set_ylabel("Neerslag (mm)", color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')

        # Stel de limieten van de y-as voor Neerslag in zodat er altijd 0.5 extra ruimte is
        min_neerslag = filtered_data_week_reset['Neerslag (mm)'].min()
        max_neerslag = filtered_data_week_reset['Neerslag (mm)'].max()
        ax1.set_ylim(min_neerslag - 0.5, max_neerslag + 0.5)  # 0.5 extra ruimte onder en boven de data

        # Maak een tweede y-as voor Aantal Verhuurde Fietsen
        ax2 = ax1.twinx()
        sns.lineplot(data=filtered_data_week_reset, x='Date', y='Aantal Verhuurde Fietsen', marker='o', ax=ax2, color='red', label='Aantal Verhuurde Fietsen')
        ax2.set_ylabel("Aantal Verhuurde Fietsen", color='red')
        ax2.tick_params(axis='y', labelcolor='red')

        ax1.set_title(f"Neerslag en Aantal Verhuurde Fietsen per Dag in Week {week_nummer}")
        plt.xticks(rotation=45)
        st.pyplot(fig)

    elif grafiek_keuze == 'Sneeuwval per Dag':
        fig, ax1 = plt.subplots(figsize=(10, 6))
        # Plot voor Sneeuwval aan de linker y-as
        sns.lineplot(data=filtered_data_week_reset, x='Date', y='Sneeuwval (cm)', marker='o', ax=ax1, color='green')
        ax1.set_xlabel("Datum")
        ax1.set_ylabel("Sneeuwval (cm)", color='green')
        ax1.tick_params(axis='y', labelcolor='green')

        # Maak een tweede y-as voor Aantal Verhuurde Fietsen
        ax2 = ax1.twinx()
        sns.lineplot(data=filtered_data_week_reset, x='Date', y='Aantal Verhuurde Fietsen', marker='o', ax=ax2, color='blue', label='Aantal Verhuurde Fietsen')
        ax2.set_ylabel("Aantal Verhuurde Fietsen", color='blue')
        ax2.tick_params(axis='y', labelcolor='blue')

        # Stel de limieten van de y-as voor Aantal Verhuurde Fietsen in zodat er altijd 2000 extra ruimte is
        min_fietsen = filtered_data_week_reset['Aantal Verhuurde Fietsen'].min()
        max_fietsen = filtered_data_week_reset['Aantal Verhuurde Fietsen'].max()
        ax2.set_ylim(min_fietsen - 2000, max_fietsen + 2000)  # 2000 extra ruimte onder en boven de data

        ax1.set_title(f"Sneeuwval en Aantal Verhuurde Fietsen per Dag in Week {week_nummer}")
        plt.xticks(rotation=45)
        st.pyplot(fig)

    
        # Data inladen
    fiets_rentals = pd.read_csv('fietsdata2021_rentals_by_day.csv')
    weer_data = pd.read_csv('weather_london.csv')

    # Zorg ervoor dat de datums in datetime-formaat staan
    fiets_rentals["Day"] = pd.to_datetime(fiets_rentals["Day"])
    weer_data["Date"] = pd.to_datetime(weer_data["Unnamed: 0"])  # Zet de juiste kolomnaam om

    # Merge de datasets op datum
    combined_df = pd.merge(fiets_rentals, weer_data, left_on="Day", right_on="Date", how="inner")

    # Verwijder de dubbele datumkolom (we houden "Day")
    combined_df.drop(columns=["Date"], inplace=True)

    # Streamlit-app titel
    st.header("Correlatie tussen fietsverhuur en weer")
    
    # Mapping van kolomnamen naar leesbare labels
    weerfactor_mapping = {
        "tavg": "Average Temperature",
        "tmin": "Minimum Temperature",
        "tmax": "Maximum Temperature",
        "prcp": "Rainfall"
    }
    
    # Selecteer een weerfactor met aangepaste labels
    weerfactor_label = st.selectbox("Kies een weerfactor:", list(weerfactor_mapping.values()))
    
    # Converteer de geselecteerde label terug naar de juiste kolomnaam
    weerfactor = [k for k, v in weerfactor_mapping.items() if v == weerfactor_label][0]
    
    # X en Y variabelen
    x = combined_df[weerfactor]  # Gekozen weerfactor
    y = combined_df["Total Rentals"]  # Aantal fietsverhuringen
    
    # Regressiemodel maken
    x_with_constant = sm.add_constant(x)  # Constante toevoegen voor de regressie
    model = sm.OLS(y, x_with_constant).fit()
    r_squared = model.rsquared  # R²-waarde van de regressie
    equation = f"y = {model.params[1]:.2f}x + {model.params[0]:.2f}"  # Regressievergelijking
    
    # Plot maken met seaborn
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.regplot(x=x, y=y, line_kws={'color': 'red'}, scatter_kws={'alpha': 0.5}, ax=ax)
    ax.set_xlabel(weerfactor_label)
    ax.set_ylabel("Aantal Fietsverhuringen")
    ax.set_title(f"Regressie: {weerfactor_label} vs. Fietsverhuur\nR² = {r_squared:.2f}")
    ax.text(0.05, 0.9, equation, transform=ax.transAxes, fontsize=12, color="red")
    
    # Toon de plot in Streamlit
    st.pyplot(fig)
