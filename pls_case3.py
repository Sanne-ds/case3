# Streamlit-app titel
st.title("Regressieanalyse: Fietsverhuur en Weer")

# Vertaling van de weerfactoren
weerfactoren_mapping = {
    "tavg": "Gemiddelde Temperatuur (°C)",
    "tmin": "Minimale Temperatuur (°C)",
    "tmax": "Maximale Temperatuur (°C)",
    "prcp": "Neerslag (mm)"
}

# Selecteer een weerfactor voor de regressie (wspd is verwijderd)
weerfactor = st.selectbox("Kies een weerfactor:", list(weerfactoren_mapping.values()))

# Vind de originele kolomnaam op basis van de geselecteerde waarde
originele_kolomnaam = [k for k, v in weerfactoren_mapping.items() if v == weerfactor][0]

# X en Y variabelen
x = combined_df[originele_kolomnaam]  # Weerfactor (bijv. temperatuur)
y = combined_df["Total Rentals"]  # Aantal fietsverhuringen

# Regressiemodel maken
x_with_constant = sm.add_constant(x)  # Constante toevoegen voor de regressie
model = sm.OLS(y, x_with_constant).fit()
r_squared = model.rsquared  # R²-waarde van de regressie
equation = f"y = {model.params[1]:.2f}x + {model.params[0]:.2f}"  # Regressievergelijking

# Plot maken met seaborn
fig, ax = plt.subplots(figsize=(8, 5))
sns.regplot(x=x, y=y, line_kws={'color': 'red'}, scatter_kws={'alpha': 0.5}, ax=ax)
ax.set_xlabel(weerfactor)  # Gebruik de vertaalde naam
ax.set_ylabel("Aantal Fietsverhuringen")
ax.set_title(f"Regressie: {weerfactor} vs. Fietsverhuur\nR² = {r_squared:.2f}")
ax.text(0.05, 0.9, equation, transform=ax.transAxes, fontsize=12, color="red")

# Toon de plot in Streamlit
st.pyplot(fig)
