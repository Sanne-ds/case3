import pandas as pd
import plotly.express as px
import streamlit as st

# 📌 Titel van de app
st.title("Bike Ride Duration Analysis per Month 🚴‍♂️")

# ✅ Checkbox om outliers in- of uit te schakelen
show_outliers = st.checkbox("Show Outliers", value=True)

# 📂 Maanden koppelen aan bestandsnamen
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
}

@st.cache_data
def load_data():
    """🔄 Laadt alle CSV-bestanden en voegt de maandnaam toe."""
    all_data = []
    for month, file in months.items():
        df = pd.read_csv(file)
        df["Duration"] = df["Duration"] / 60  # ⏳ Seconden → Minuten
        df["Month"] = month  # Voeg de maand toe
        all_data.append(df)
    
    full_data = pd.concat(all_data, ignore_index=True)
    full_data["Month"] = pd.Categorical(full_data["Month"], categories=months.keys(), ordered=True)  # Zet maand op volgorde
    return full_data

# 📂 Laad alle maanden in één keer
full_data = load_data()

# 📌 Outliers filteren indien nodig
if not show_outliers:
    max_duration = full_data["Duration"].quantile(0.95)  # 95e percentiel
    filtered_data = full_data[full_data["Duration"] <= max_duration]
else:
    filtered_data = full_data  # Toon alles

# 📊 Maak een interactieve boxplot met Plotly
fig = px.box(
    filtered_data, 
    x="Month", 
    y="Duration", 
    color="Month",  # Kleur per maand
    title="Ride Duration Distribution per Month",
    labels={"Duration": "Ride Duration (minutes)", "Month": "Month"},
    template="plotly_white",
    points="outliers" if show_outliers else False  # ⚡ Snellere rendering
)

# 🖼️ Toon de interactieve plot
st.plotly_chart(fig)
