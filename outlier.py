import pandas as pd
import plotly.express as px
import streamlit as st

# Titel van de app
st.title("Bike Ride Duration Analysis per Month 🚴‍♂️")

# Maanden toewijzen aan bestandsnamen
months = {
    "bike_1klein.csv": "January",
    "bike_2klein.csv": "February",
    "bike_3klein.csv": "March",
    "bike_4klein.csv": "April",
    "bike_5klein.csv": "May",
    "bike_6klein.csv": "June",
    "bike_7klein.csv": "July",
    "bike_8klein.csv": "August",
    "bike_9klein.csv": "September",
    "bike_10klein.csv": "October",
    "bike_11klein.csv": "November",
    "bike_12klein.csv": "December"
}

# Lege lijst om data van alle maanden op te slaan
all_data = []

# Loop door alle bestanden en voeg data toe
for file, month in months.items():
    df = pd.read_csv(file)
    df["Month"] = month
    all_data.append(df)

# Combineer alle datasets
full_data = pd.concat(all_data, ignore_index=True)

# Zet de maand op volgorde
full_data["Month"] = pd.Categorical(full_data["Month"], categories=months.values(), ordered=True)

# Zet duur om van seconden naar minuten
full_data["Duration"] = full_data["Duration"] / 60  

# Checkbox om outliers in- of uit te schakelen
show_outliers = st.checkbox("Show Outliers", value=True)

if not show_outliers:
    # Filter outliers: Neem alleen data tot het 95e percentiel
    max_duration = full_data["Duration"].quantile(0.95)
    filtered_data = full_data[full_data["Duration"] <= max_duration]
else:
    filtered_data = full_data  # Toon alles, inclusief outliers

# Interactieve boxplot maken met Plotly
fig = px.box(
    filtered_data, 
    x="Month", 
    y="Duration", 
    color="Month",  # Geeft elke maand een andere kleur
    title="Distribution of Ride Durations per Month",
    labels={"Duration": "Ride Duration (minutes)", "Month": "Month"},
    template="plotly_white"
)

# Toon de interactieve plot
st.plotly_chart(fig)
