import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("🏒 SDHL Dashboard")

df = pd.read_excel("SDHL_Player_Value_Model.xlsx")

st.write(df.head())
