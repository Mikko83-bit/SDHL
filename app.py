import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="SDHL Player Value Dashboard",
    layout="wide"
)

# =========================
# TITLE
# =========================

st.title("🏒 SDHL Player Value Dashboard")

# =========================
# LOAD DATA
# =========================

df = pd.read_excel("SDHL_Player_Value_Model.xlsx")

# =========================
# SIDEBAR FILTERS
# =========================

st.sidebar.header("Filters")

min_toi = st.sidebar.slider(
    "Min Time on Ice",
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

df = df[
    (df["Time on ice"] >= min_toi) &
    (df["Team"].isin(teams)) &
    (df["Position"].isin(positions))
]

# =========================
# TOP METRICS
# =========================

col1, col2, col3 = st.columns(3)

col1.metric(
    "Players",
    len(df)
)

col2.metric(
    "Avg Value",
    round(df["Value"].mean(), 2)
)

top_player = (
    df.sort_values("Value", ascending=False)
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
    df,
    x="Creation Score",
    y="Net xG /60",
    color="Position",
    hover_name="Player",
    hover_data=[
        "Team",
        "Value",
        "Goals/60",
        "Assists/60"
    ],
    size="Value",
    title="Creation vs Impact"
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
    df.sort_values("Value", ascending=False)
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
    sorted(df["Player"].unique())
)

player_data = df[
    df["Player"] == player
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
    "Creation",
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

st.subheader("Player Details")

details = pd.DataFrame({
    "Metric": [
        "Goals/60",
        "Assists/60",
        "xG/60",
        "Puck Control",
        "Takeaways/60",
        "Puck losses/60"
    ],
    "Value": [
        round(player_data["Goals/60"], 2),
        round(player_data["Assists/60"], 2),
        round(player_data["xG/60"], 2),
        round(player_data["Puck Control"], 2),
        round(player_data["Takeaways  /60"], 2),
        round(player_data["Puck losses/60"], 2)
    ]
})

st.dataframe(
    details,
    use_container_width=True
)
