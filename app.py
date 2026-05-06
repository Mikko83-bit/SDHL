import streamlit as st
import pandas as pd
st.set_page_config(layout="wide")
st.title("🏒 SDHL Dashboard")
df = pd.read_excel("SDHL_Player_Value_Model.xlsx")
st.write(df.head())
st.sidebar.header("Filters")
min_toi = st.sidebar.slider(
    "Minimum TOI",
    0,
    800,
    300
)
filtered_df = df[
    df["Time on ice"] >= min_toi
]
st.dataframe(filtered_df.head(20))
import plotly.express as px
fig = px.scatter(
    filtered_df,
    x="Creation Score",
    y="Net xG /60"
)
st.plotly_chart(fig)
fig = px.scatter(
    filtered_df,
    x="Creation Score",
    y="Net xG /60",
    color="Position"
)

st.plotly_chart(fig)
