import pandas as pd
import plotly.graph_objects as go
import streamlit as st

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

        # Maak een Plotly grafiek
        fig = go.Figure(data=[
            go.Bar(
                x=top_20_bike_ids['Bike Id'].astype(str),
                y=top_20_bike_ids['rental_count'],
                marker=dict(color='skyblue'),
                text=top_20_bike_ids['rental_count'],
                hoverinfo='x+y'
            )
        ])

        # Titels en labels toevoegen
        fig.update_layout(
            title='Top 20 Bike IDs met de Meeste Verhuur in het Jaar',
            xaxis_title='Bike ID',
            yaxis_title='Aantal Verhuur',
            xaxis_tickangle=-45
        )

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

        # Maak een Plotly grafiek
        fig = go.Figure(data=[
            go.Bar(
                x=top_20_bike_ids['Bike Id'].astype(str),
                y=top_20_bike_ids['total_duration'] / 3600,  # Omrekenen naar uren
                marker=dict(color='skyblue'),
                text=top_20_bike_ids['total_duration'] / 3600,  # Hover tekst
                hoverinfo='x+y'
            )
        ])

        # Titels en labels toevoegen
        fig.update_layout(
            title=f'Top 20 Bike IDs met de Langste Verhuurtijden in de Maand ({month_name})',
            xaxis_title='Bike ID',
            yaxis_title='Totale Huurduur (uren)',
            xaxis_tickangle=-45,
            yaxis=dict(range=[0, 250])  # Beperk de y-as tot 250 uur voor maandgegevens
        )

    # Toon de plot
    st.plotly_chart(fig)

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
st.title('Bike Rental Analysis')

# Dropdown menu voor maandselectie
month_name = st.selectbox('Selecteer een maand:', month_names)

# Plot de grafiek op basis van de geselecteerde maand
plot_bike_data(month_name)
