import pandas as pd
import plotly.express as px
import streamlit as st

# Titel van de app
st.title("Bike Ride Duration Analysis per Month 🚴‍♂️")

# Maanden toewijzen aan bestandsnamen
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
    "All Year": None  # Speciaal voor alle data
}

# Dropdown menu voor maandselectie
selected_month = st.selectbox("Select a month:", list(months.keys()), index=0)

# Checkbox om outliers in- of uit te schakelen
show_outliers = st.checkbox("Show Outliers", value=True)

@st.cache_data
def load_data(file):
    """Laadt een CSV-bestand en zet de duur om naar minuten."""
    df = pd.read_csv(file)
    df["Duration"] = df["Duration"] / 60  # Seconden omzetten naar minuten
    return df

# Data inladen op basis van selectie
if selected_month == "All Year":
    # Laad alle maanden
    full_data = pd.concat([load_data(file) for file in months.values() if file], ignore_index=True)
    full_data["Month"] = pd.Categorical(full_data["Month"], categories=months.keys(), ordered=True)
else:
    full_data = load_data(months[selected_month])
    full_data["Month"] = selected_month

# Outliers filteren indien nodig
if not show_outliers:
    max_duration = full_data["Duration"].quantile(0.95)
    filtered_data = full_data[full_data["Duration"] <= max_duration]
else:
    filtered_data = full_data

# Interactieve boxplot maken met Plotly
fig = px.box(
    filtered_data, 
    x="Month", 
    y="Duration", 
    color="Month" if selected_month == "All Year" else None,  # Alleen kleuren bij 'All Year'
    title=f"Ride Duration Distribution - {selected_month}",
    labels={"Duration": "Ride Duration (minutes)", "Month": "Month"},
    template="plotly_white",
    points="outliers" if show_outliers else False  # Snellere rendering
)

# Toon de interactieve plot
st.plotly_chart(fig)
