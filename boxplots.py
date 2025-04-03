import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import streamlit as st

def load_data():
    data = []
    for i in range(1, 13):  # Voor alle maanden
        filename = f'bike_{i}klein.csv'
        if os.path.exists(filename):
            df = pd.read_csv(filename, usecols=["Duration"])
            df["Month"] = i  # Maand toevoegen
            data.append(df)
    return pd.concat(data, ignore_index=True) if data else pd.DataFrame()

data = load_data()

st.title("Boxplot van ritduur per maand")

if not data.empty:
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='Month', y='Duration', data=data, showfliers=False)
    plt.xlabel("Maand")
    plt.ylabel("Duur (seconden)")
    plt.title("Boxplot van ritduur per maand")
    st.pyplot(plt)
else:
    st.write("Geen data gevonden. Zorg ervoor dat de bestanden aanwezig zijn.")
