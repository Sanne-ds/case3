import pandas as pd
import plotly.express as px

# Lijst van maandnamen in het Nederlands
maandnamen = [
    'Januari', 'Februari', 'Maart', 'April', 'Mei', 'Juni', 
    'Juli', 'Augustus', 'September', 'Oktober', 'November', 'December'
]

# Maak een lege lijst voor de gemiddelde duur per maand
average_durations = []

# Itereer door de bestanden bike_1klein t/m bike_12klein
for i in range(1, 13):
    # Bestandsnaam opbouwen
    file_name = f'bike_{i}klein.csv'
    
    # Lees het CSV-bestand in een DataFrame
    df = pd.read_csv(file_name)
    
    # Bereken de gemiddelde 'Duration' in minuten
    avg_duration_minutes = df['Duration'].mean() / 60  # Omrekenen van seconden naar minuten
    average_durations.append(avg_duration_minutes)

# Maak een DataFrame met maandnamen en de gemiddelde duur
avg_df = pd.DataFrame({
    'Month': maandnamen,  # Gebruik maandnamen in plaats van nummers
    'Average Duration (Minutes)': average_durations
})

# Maak een Plotly lijn plot van de gemiddelde duur per maand in minuten
fig = px.line(avg_df, x='Month', y='Average Duration (Minutes)', 
              title='Gemiddelde Duur per Maand (Minuten)',
              labels={'Month': 'Maand', 'Average Duration (Minutes)': 'Gemiddelde Duur (Minuten)'})

# Toon de plot
fig.update_xaxes(type='category')  # Zorg ervoor dat de maanden als categorieën worden behandeld
fig.show()

