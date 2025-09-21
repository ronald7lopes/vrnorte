"""
Arquivo principal para o funcionamento do Streamlit, execute 
esse arquivo da raiz do "SI PORTAL 1.5.0" com o comando

streamlit run streamlit_app.py
"""
import streamlit as st
import time
from streamlit_option_menu import option_menu


import pages.dashboard as dashboard
import pages.relatorio as relatorio


st.set_page_config(layout="wide", page_title="SI Dashboard", page_icon="🏆")


with open("./styles/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


with st.sidebar:
    selected = option_menu(
        "Suporte",  # Título
        ["Dashboard", "Relatorio"],
        icons=["graph-up", "book"],
        default_index=0,
    )


if selected == "Dashboard":
    dashboard.run()
    time.sleep(500)
    st.rerun()
elif selected == "Relatorio":
    relatorio.run()

