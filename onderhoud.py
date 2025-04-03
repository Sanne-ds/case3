import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

# Lege lijst om de data van alle maanden op te slaan
all_data = []

# Loop door alle bestanden en voeg ze toe aan de lijst
for file, month in months.items():
    df = pd.read_csv(file)  # Lees het CSV-bestand in
    df["Month"] = month  # Voeg de maand als nieuwe kolom toe
    all_data.append(df)  # Voeg de DataFrame toe aan de lijst

# Combineer alle maanden in één DataFrame
full_data = pd.concat(all_data, ignore_index=True)

# Zet de maand om naar een categorie met juiste volgorde
full_data["Month"] = pd.Categorical(full_data["Month"], categories=months.values(), ordered=True)

# Zet de duratie om van seconden naar minuten
full_data["Duration"] = full_data["Duration"] / 60

# Maak de boxplot
plt.figure(figsize=(12, 6))
sns.boxplot(x="Month", y="Duration", data=full_data, palette="Blues")

# Grafiek opmaken
plt.xticks(rotation=45)
plt.xlabel("Month")
plt.ylabel("Ride Duration (minutes)")
plt.title("Distribution of Ride Durations per Month")
plt.ylim(0, full_data["Duration"].quantile(0.99))  # Limiteer de y-as op het 99e percentiel om extreme outliers te filteren

# Toon de plot
plt.show()
