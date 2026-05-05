import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("🏒 SDHL Player Value Dashboard")

df = pd.read_excel("SDHL_Player_Value_Model.xlsx")

st.sidebar.header("Filters")

min_toi = st.sidebar.slider("Min Time on Ice", 0, 800, 300)

teams = st.sidebar.multiselect(
    "Select Team",
    options=df["Team"].unique(),
    default=df["Team"].unique()
)

positions = st.sidebar.multiselect(
    "Position",
    options=df["Position"].unique(),
    default=df["Position"].unique()
)

df = df[
    (df["Time on ice"] > min_toi) &
    (df["Team"].isin(teams)) &
    (df["Position"].isin(positions))
]

col1, col2, col3 = st.columns(3)

col1.metric("Players", len(df))
col2.metric("Avg Value", round(df["Value"].mean(), 2))
col3.metric("Top Player", df.sort_values("Value", ascending=False)["Player"].iloc[0])

st.subheader("📊 Player Map")

fig, ax = plt.subplots()

f = df[df["Position"] == "F"]
d = df[df["Position"] == "D"]

ax.scatter(f["Creation Score"], f["Net xG /60"], label="Forwards")
ax.scatter(d["Creation Score"], d["Net xG /60"], label="Defense")

ax.set_xlabel("Creation")
ax.set_ylabel("Impact (Net xG)")
ax.legend()

st.pyplot(fig)

st.subheader("🔥 Top Players")

st.dataframe(
    df.sort_values("Value", ascending=False)[
        ["Player","Team","Position","Value","Value_pct"]
    ].head(15)
)

st.subheader("🎯 Player Profile")

player = st.selectbox("Select Player", df["Player"])

player_data = df[df["Player"] == player].iloc[0]

st.write({
    "Value %": player_data["Value_pct"],
    "Creation": player_data["Creation Score"],
    "Shot Quality": player_data["Shot Quality"],
    "Puck Control": player_data["Puck Control"],
    "Net xG": player_data["Net xG /60"]
})