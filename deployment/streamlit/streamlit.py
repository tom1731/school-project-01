import streamlit as st
from toolbox import DatabaseInterface
from datetime import datetime
import graphs


########################### load data and init streamlit ###########################


@st.cache_data()
def load_data():
    databaseInterface = DatabaseInterface()
    data_articles = databaseInterface.select("query_articles")
    data_cities_from_articles = databaseInterface.select("query_cities_from_articles")

    # date range
    date_min = min(data_articles["article_date"]).to_pydatetime()
    date_max = max(data_articles["article_date"]).to_pydatetime()
    print(f"[LOG] date min: {date_min}, date max: {date_max}")

    return data_articles, data_cities_from_articles, date_min, date_max

data_articles, data_cities_from_articles, date_min, date_max = load_data()

# Initialization
if 'session_count' not in st.session_state:
    print("[LOG] New streamlit session")
    st.session_state['session_count'] = 0


########################### streamlit page ###########################


def date_slider():
    range_date = st.slider("Range de date voulu ?", value=(date_min, date_max))
    if range_date[0] == range_date[1]:
        st.warning("Veuillez séléctionner deux dates différentes.")
        st.stop()
    return range_date


st.session_state['session_count'] += 1
print(f"[LOG] New page generation ({st.session_state['session_count']})")

st.sidebar.header("Menu")
sidebar_menu_00 = st.sidebar.selectbox(
    "Analyse", ("Couverture médiatique", "Heatmap des villes", "Data")
)

if sidebar_menu_00 == "Couverture médiatique":

    date_range = date_slider()

    st.header("COUVRTURE MÉDIATIQUE")
    st.write("Ce graphique présente le couverture médiatique depuis 2021 jusqu'au debut 2023")
    
    journal_filter = st.multiselect(
        'Journal',
        ['Le Monde', 'Libération'],
        ['Le Monde', 'Libération'])

    if journal_filter:
        graphs.graph(data_articles, date_range, journal_filter)
        st.write(" On peut constater que pendant le début de la guerre, les articles du journal le monde qui parle du Ukraine on augmenter")
    else:
        st.warning("Sélectionnez au moins un journal dans la liste.")

elif sidebar_menu_00 == "Heatmap des villes":

    date_range = date_slider()

    df_cities = data_cities_from_articles.copy()
    df_cities = df_cities[
        (df_cities['article_date'] >= date_range[0])
        & (df_cities['article_date'] <= date_range[1])]
    df_cities["city"] = df_cities["city"].str.capitalize()

    df_mapcity = (
        df_cities.groupby(["city", "population_2023", "latitude", "longitude"])
        .count()
        .sort_values("article_date", ascending=False)
        .reset_index()
    )
    df_mapcity = df_mapcity.rename(columns={"article_date": "count"})
    df_mapcity = df_mapcity.dropna()

    # print graph
    st.header("HEATMAP DES VILLES")
    graphs.bubblemap(df_mapcity)
    st.write("")
    st.header("Les nombres d'articles parlant sur une ville")
    graphs.countplot(df_cities, "city")
    


elif sidebar_menu_00 == "Data":
    st.header("Data")
    st.dataframe(data_articles)
    st.dataframe(data_cities_from_articles)
