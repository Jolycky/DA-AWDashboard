import streamlit as st
import sys

sys.path.append('dashboard')
import pages as pg

st.set_page_config(page_title="Data Visualization Dashboard")

st.sidebar.title(':bar_chart: Data Visualization Dashboard')
st.sidebar.header("Jose Bagus Ramadhan (21082010206)")
page = st.sidebar.radio("Go to", ["Adventure Works", "IMDB"])

functions = {
    "Adventure Works": pg.show_db,
    "IMDB": pg.show_imdb,
}

functions[page]()