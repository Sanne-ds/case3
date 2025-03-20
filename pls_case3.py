import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm

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
tab1, tab2, tab3 = st.tabs(["🚇 Metro Stations en Lijnen", "🚲 Fietsverhuurstations", "🌤️ Weerdata"])

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

with tab3:

    
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
        
        st.dataframe(filtered_data_week_reset[kolommen])

    else:
        st.write(f"Geen gegevens gevonden voor week {week_nummer} van 2021.")

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
st.title("Regressieanalyse: Fietsverhuur en Weer")

# Selecteer een weerfactor voor de regressie
weerfactor = st.selectbox("Kies een weerfactor:", ["tavg", "tmin", "tmax", "prcp", "wspd"])

# X en Y variabelen
x = combined_df[weerfactor]  # Weerfactor (bijv. temperatuur)
y = combined_df["Total Rentals"]  # Aantal fietsverhuringen

# Regressiemodel maken
x_with_constant = sm.add_constant(x)  # Constante toevoegen voor de regressie
model = sm.OLS(y, x_with_constant).fit()
r_squared = model.rsquared  # R²-waarde van de regressie
equation = f"y = {model.params[1]:.2f}x + {model.params[0]:.2f}"  # Regressievergelijking

# Plot maken met seaborn
fig, ax = plt.subplots(figsize=(8, 5))
sns.regplot(x=x, y=y, line_kws={'color': 'red'}, scatter_kws={'alpha': 0.5}, ax=ax)
ax.set_xlabel(weerfactor)
ax.set_ylabel("Aantal Fietsverhuringen")
ax.set_title(f"Regressie: {weerfactor} vs. Fietsverhuur\nR² = {r_squared:.2f}")
ax.text(0.05, 0.9, equation, transform=ax.transAxes, fontsize=12, color="red")

# Toon de plot in Streamlit
st.pyplot(fig)

# Ensure 'Day' is in datetime format
rentals_data['Day'] = pd.to_datetime(rentals_data['Day'])

# Add a 'Month' column to the rentals data
rentals_data['Month'] = rentals_data['Day'].dt.month

# Ensure 'Date' in weather data is in datetime format
weather_data['Date'] = pd.to_datetime(weather_data['Unnamed: 0'])
weather_data['Month'] = weather_data['Date'].dt.month

# Calculate monthly averages for weather data
monthly_weather = weather_data.groupby('Month').agg({
    'tavg': 'mean',  # Average temperature
    'prcp': 'mean'   # Average precipitation
}).reset_index()

# Calculate total rentals for each month
monthly_rentals = rentals_data.groupby('Month').agg({'Total Rentals': 'sum'}).reset_index()

# Calculate the global minimum and maximum total rentals across all months
global_min_rentals = monthly_rentals['Total Rentals'].min()
global_max_rentals = monthly_rentals['Total Rentals'].max()

# Streamlit app title
st.title("London Bike Rentals per Month with Weather Data")

# Month selection using a slider
selected_month = st.slider(
    "Select a month to visualize:",
    min_value=1,
    max_value=12,
    value=1,
    format="Month: %d"
)

# Get data for the selected month
selected_weather = monthly_weather[monthly_weather['Month'] == selected_month].iloc[0]
avg_temp = selected_weather['tavg']
avg_precipitation = selected_weather['prcp']

# Get total rentals for the selected month
selected_month_rentals = monthly_rentals[monthly_rentals['Month'] == selected_month].iloc[0]['Total Rentals']

# Display weather information and total rentals above the map
st.markdown(
    f"""
    ### Summary for {pd.to_datetime(f"2021-{selected_month}-01").strftime('%B')}
    - Total Rentals: {selected_month_rentals:,}
    - Average Temperature: {avg_temp:.1f}°C
    - Average Precipitation: {avg_precipitation:.1f} mm
    """
)

# Create a Folium map
m = folium.Map(location=[51.509865, -0.118092], tiles="CartoDB positron", zoom_start=10)

# Define a consistent colormap for rentals based on the global min and max rentals
colormap = linear.YlOrRd_09.scale(global_min_rentals, global_max_rentals)
colormap.caption = "Total Rentals per Month"

# Add a single GeoJson layer for London as a whole
for _, row in boroughs.iterrows():
    folium.GeoJson(
        row["geometry"],
        style_function=lambda feature: {
            "fillColor": colormap(selected_month_rentals),
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.7,
        },
        tooltip=(
            f"London<br>"
            f"Total Rentals: {selected_month_rentals:,}<br>"
            f"Avg Temp: {avg_temp:.1f}°C<br>"
            f"Avg Precipitation: {avg_precipitation:.1f} mm"
        )
    ).add_to(m)

# Add a legend to the map
m.add_child(colormap)

# Display the map in Streamlit
folium_static(m)

