import pandas as pd
import plotly.express as px
import streamlit as st

# 📌 Titel van de app
st.title("Bike Ride Duration Analysis 🚴‍♂️")

# 🗂️ Maanden koppelen aan bestandsnamen
months = {
    "January": "bike_1klein.csv",
    "February": "bike_2klein.csv",
    "March": "bike_3klein.csv",
    "April": "bike_4klein.csv",
    "May": "bike_5klein.csv",
    "June": "bike_6klein.csv",
    "July": "bike_7klein.csv",
    "August": "bike_8klein.csv",
    "September": "bike_9klein.csv",
    "October": "bike_10klein.csv",
    "November": "bike_11klein.csv",
    "December": "bike_12klein.csv",
    "All Year": None  # Speciale optie voor alle data
}

# 📌 Selecteer een maand
selected_month = st.selectbox("Select a month:", list(months.keys()), index=0)

# ✅ Checkbox om outliers in- of uit te schakelen
show_outliers = st.checkbox("Show Outliers", value=True)

@st.cache_data
def load_data(file):
    """🔄 Laadt een CSV-bestand en zet de duur om naar minuten."""
    df = pd.read_csv(file)
    df["Duration"] = df["Duration"] / 60  # ⏳ Seconden → Minuten
    return df

# 📌 Data inladen op basis van selectie
if selected_month == "All Year":
    # Laad ALLE maanden en voeg maandnamen toe
    all_data = []
    for month, file in months.items():
        if file:
            df = load_data(file)
            df["Month"] = month
            all_data.append(df)
    full_data = pd.concat(all_data, ignore_index=True)
    full_data["Month"] = pd.Categorical(full_data["Month"], categories=months.keys(), ordered=True)
else:
    # Laad alleen de geselecteerde maand
    full_data = load_data(months[selected_month])
    full_data["Month"] = selected_month

# 📌 Outliers filteren indien nodig
if not show_outliers:
    max_duration = full_data["Duration"].quantile(0.95)  # 95e percentiel
    filtered_data = full_data[full_data["Duration"] <= max_duration]
else:
    filtered_data = full_data  # Toon alle data

# 📊 Maak een interactieve boxplot met Plotly
fig = px.box(
    filtered_data, 
    x="Month", 
    y="Duration", 
    color="Month" if selected_month == "All Year" else None,  # Kleur per maand bij 'All Year'
    title=f"Ride Duration Distribution - {selected_month}",
    labels={"Duration": "Ride Duration (minutes)", "Month": "Month"},
    template="plotly_white",
    points="outliers" if show_outliers else False  # ⚡ Snellere rendering
)

# 🖼️ Toon de interactieve plot
st.plotly_chart(fig)
