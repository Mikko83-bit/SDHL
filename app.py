import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(layout="wide")

# =========================
# TITLE
# =========================

st.title("🏒 SDHL Player Value Dashboard")

# =========================
# LOAD DATA
# =========================

df = pd.read_excel("SDHL_Player_Value_Model.xlsx")

# =========================
# CLEAN DATA
# =========================

numeric_columns = [
    "Time on ice",
    "Value",
    "Value_pct",
    "Creation Score",
    "Shot Quality",
    "Puck Control",
    "Net xG /60"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=numeric_columns)

# =========================
# SIDEBAR FILTERS
# =========================

st.sidebar.header("Filters")

min_toi = st.sidebar.slider(
    "Minimum TOI",
    0,
    800,
    300
)

teams = st.sidebar.multiselect(
    "Select Team",
    options=sorted(df["Team"].unique()),
    default=sorted(df["Team"].unique())
)

positions = st.sidebar.multiselect(
    "Position",
    options=sorted(df["Position"].unique()),
    default=sorted(df["Position"].unique())
)

# =========================
# FILTER DATA
# =========================

filtered_df = df[
    (df["Time on ice"] >= min_toi) &
    (df["Team"].isin(teams)) &
    (df["Position"].isin(positions))
]

# =========================
# OVERVIEW METRICS
# =========================

st.subheader("📈 Overview")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Players",
    len(filtered_df)
)

col2.metric(
    "Average Value",
    round(filtered_df["Value"].mean(), 2)
)

top_player = (
    filtered_df
    .sort_values("Value", ascending=False)
    ["Player"]
    .iloc[0]
)

col3.metric(
    "Top Player",
    top_player
)

# =========================
# PLAYER MAP
# =========================

st.subheader("📊 Player Map")

fig = px.scatter(
    filtered_df,
    x="Creation Score",
    y="Net xG /60",
    color="Position",
    hover_name="Player",
    hover_data=[
        "Team",
        "Value",
        "Shot Quality",
        "Puck Control"
    ]
)

fig.update_layout(
    height=700
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =========================
# TOP PLAYERS TABLE
# =========================

st.subheader("🔥 Top Players")

top_players = (
    filtered_df
    .sort_values("Value", ascending=False)
    [
        [
            "Player",
            "Team",
            "Position",
            "Value",
            "Value_pct"
        ]
    ]
    .head(15)
)

st.dataframe(
    top_players,
    use_container_width=True
)

# =========================
# PLAYER PROFILE
# =========================

st.subheader("🎯 Player Profile")

player = st.selectbox(
    "Select Player",
    sorted(filtered_df["Player"].unique())
)

player_data = filtered_df[
    filtered_df["Player"] == player
].iloc[0]

# =========================
# PROFILE METRICS
# =========================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Value %",
    round(player_data["Value_pct"], 1)
)

col2.metric(
    "Creation Score",
    round(player_data["Creation Score"], 2)
)

col3.metric(
    "Shot Quality",
    round(player_data["Shot Quality"], 2)
)

col4.metric(
    "Net xG /60",
    round(player_data["Net xG /60"], 2)
)

# =========================
# PLAYER DETAILS
# =========================

st.subheader("📋 Player Details")

details = pd.DataFrame({
    "Metric": [
        "Value",
        "Value %",
        "Creation Score",
        "Shot Quality",
        "Puck Control",
        "Net xG /60",
        "Time on ice"
    ],
    "Value": [
        round(player_data["Value"], 2),
        round(player_data["Value_pct"], 1),
        round(player_data["Creation Score"], 2),
        round(player_data["Shot Quality"], 2),
        round(player_data["Puck Control"], 2),
        round(player_data["Net xG /60"], 2),
        round(player_data["Time on ice"], 1)
    ]
})

st.dataframe(
    details,
    use_container_width=True
)
