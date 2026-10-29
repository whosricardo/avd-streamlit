import pandas as pd


# TODO: adicionar @st.cache_data (import streamlit as st) para evitar reler o CSV a cada interação
def load_data(path="data/clean/dataset.csv"):
    """Lê o dataset já tratado (exportado ao final do notebook de EDA)."""
    return pd.read_csv(path)
