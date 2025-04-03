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
        
        # Verwijder deze regel om de tabel niet te tonen
        # st.dataframe(filtered_data_week_reset[kolommen])

    else:
        st.write(f"Geen gegevens gevonden voor week {week_nummer} van 2021.")

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

    # Selectbox om grafieken te kiezen
    grafiek_keuze = st.selectbox('Kies welke grafiek je wilt zien:', 
                                 ['Aantal Verhuurde Fietsen per Dag', 
                                  'Gemiddelde Temperatuur per Dag', 
                                  'Neerslag per Dag', 
                                  'Sneeuwval per Dag'])

    # Toon de gekozen grafiek
    if grafiek_keuze == 'Aantal Verhuurde Fietsen per Dag':
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.lineplot(data=filtered_data_week_reset, x='Date', y='Aantal Verhuurde Fietsen', marker='o', ax=ax, color='blue')
        ax.set_xlabel("Datum")
        ax.set_ylabel("Aantal Verhuurde Fietsen", color='blue')
        ax.set_title(f"Aantal Verhuurde Fietsen per Dag in Week {week_nummer}")
        ax.tick_params(axis='y', labelcolor='blue')
        
        # Stel de limieten van de y-as in zodat er altijd 2000 extra ruimte is
        min_fietsen = filtered_data_week_reset['Aantal Verhuurde Fietsen'].min()
        max_fietsen = filtered_data_week_reset['Aantal Verhuurde Fietsen'].max()
        ax.set_ylim(min_fietsen - 2000, max_fietsen + 2000)  # 2000 extra ruimte onder en boven de data
        
        plt.xticks(rotation=45)
        st.pyplot(fig)

    elif grafiek_keuze == 'Gemiddelde Temperatuur per Dag':
        fig, ax1 = plt.subplots(figsize=(10, 6))
        # Plot voor Gemiddelde Temperatuur aan de linker y-as
        sns.lineplot(data=filtered_data_week_reset, x='Date', y='Gemiddelde Temperatuur (°C)', marker='o', ax=ax1, color='orange')
        ax1.set_xlabel("Datum")
        ax1.set_ylabel("Gemiddelde Temperatuur (°C)", color='orange')
        ax1.tick_params(axis='y', labelcolor='orange')

        # Stel de limieten van de y-as voor Temperatuur in zodat er altijd 2 extra ruimte is
        min_temp = filtered_data_week_reset['Gemiddelde Temperatuur (°C)'].min()
        max_temp = filtered_data_week_reset['Gemiddelde Temperatuur (°C)'].max()
        ax1.set_ylim(min_temp - 2, max_temp + 2)  # 2 extra ruimte onder en boven de data

        # Maak een tweede y-as voor Aantal Verhuurde Fietsen
        ax2 = ax1.twinx()
        sns.lineplot(data=filtered_data_week_reset, x='Date', y='Aantal Verhuurde Fietsen', marker='o', ax=ax2, color='blue', label='Aantal Verhuurde Fietsen')
        ax2.set_ylabel("Aantal Verhuurde Fietsen", color='blue')
        ax2.tick_params(axis='y', labelcolor='blue')

        ax1.set_title(f"Gemiddelde Temperatuur en Aantal Verhuurde Fietsen per Dag in Week {week_nummer}")
        plt.xticks(rotation=45)
        st.pyplot(fig)

    elif grafiek_keuze == 'Neerslag per Dag':
        fig, ax1 = plt.subplots(figsize=(10, 6))
        # Plot voor Neerslag aan de linker y-as
        sns.barplot(data=filtered_data_week_reset, x='Date', y='Neerslag (mm)', ax=ax1, color='blue')
        ax1.set_xlabel("Datum")
        ax1.set_ylabel("Neerslag (mm)", color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')

        # Stel de limieten van de y-as voor Neerslag in zodat er altijd 0.5 extra ruimte is
        min_neerslag = filtered_data_week_reset['Neerslag (mm)'].min()
        max_neerslag = filtered_data_week_reset['Neerslag (mm)'].max()
        ax1.set_ylim(min_neerslag - 0.5, max_neerslag + 0.5)  # 0.5 extra ruimte onder en boven de data

        # Maak een tweede y-as voor Aantal Verhuurde Fietsen
        ax2 = ax1.twinx()
        sns.lineplot(data=filtered_data_week_reset, x='Date', y='Aantal Verhuurde Fietsen', marker='o', ax=ax2, color='red', label='Aantal Verhuurde Fietsen')
        ax2.set_ylabel("Aantal Verhuurde Fietsen", color='red')
        ax2.tick_params(axis='y', labelcolor='red')

        ax1.set_title(f"Neerslag en Aantal Verhuurde Fietsen per Dag in Week {week_nummer}")
        plt.xticks(rotation=45)
        st.pyplot(fig)

    elif grafiek_keuze == 'Sneeuwval per Dag':
        fig, ax1 = plt.subplots(figsize=(10, 6))
        # Plot voor Sneeuwval aan de linker y-as
        sns.lineplot(data=filtered_data_week_reset, x='Date', y='Sneeuwval (cm)', marker='o', ax=ax1, color='green')
        ax1.set_xlabel("Datum")
        ax1.set_ylabel("Sneeuwval (cm)", color='green')
        ax1.tick_params(axis='y', labelcolor='green')

        # Maak een tweede y-as voor Aantal Verhuurde Fietsen
        ax2 = ax1.twinx()
        sns.lineplot(data=filtered_data_week_reset, x='Date', y='Aantal Verhuurde Fietsen', marker='o', ax=ax2, color='blue', label='Aantal Verhuurde Fietsen')
        ax2.set_ylabel("Aantal Verhuurde Fietsen", color='blue')
        ax2.tick_params(axis='y', labelcolor='blue')

        # Stel de limieten van de y-as voor Aantal Verhuurde Fietsen in zodat er altijd 2000 extra ruimte is
        min_fietsen = filtered_data_week_reset['Aantal Verhuurde Fietsen'].min()
        max_fietsen = filtered_data_week_reset['Aantal Verhuurde Fietsen'].max()
        ax2.set_ylim(min_fietsen - 2000, max_fietsen + 2000)  # 2000 extra ruimte onder en boven de data

        ax1.set_title(f"Sneeuwval en Aantal Verhuurde Fietsen per Dag in Week {week_nummer}")
        plt.xticks(rotation=45)
        st.pyplot(fig)
