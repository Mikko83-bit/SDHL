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

st.title("🏒 Game Score Model")

# =========================
# LOAD DATA
# =========================

df = pd.read_excel("SDHL_ZScore_GameScore_Final.xlsx")

# =========================
# CLEAN DATA
# =========================

numeric_columns = [
    "Game Score",
    "Adjusted Game Score",
    "Time on ice"
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
    "Teams",
    options=sorted(df["Team"].unique()),
    default=sorted(df["Team"].unique())
)

positions = st.sidebar.multiselect(
    "Positions",
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
# OVERVIEW
# =========================

st.subheader("📈 Overview")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Players",
    len(filtered_df)
)

col2.metric(
    "Average Game Score",
    round(filtered_df["Adjusted Game Score"].mean(), 2)
)

top_player = (
    filtered_df
    .sort_values(
        by="Adjusted Game Score",
        ascending=False
    )["Player"]
    .iloc[0]
)

col3.metric(
    "Top Player",
    top_player
)

# =========================
# SCATTER PLOT
# =========================

st.subheader("📊 Game Score Map")

fig = px.scatter(
    filtered_df,
    x="Game Score",
    y="Adjusted Game Score",
    color="Position",
    hover_name="Player",
    hover_data=[
        "Team",
        "Time on ice"
    ],
    title="Game Score vs Adjusted Game Score"
)

fig.update_layout(
    template="plotly_dark",
    height=700
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =========================
# TOP PLAYERS
# =========================

st.subheader("🔥 Top Players")

top_players = (
    filtered_df
    .sort_values(
        by="Adjusted Game Score",
        ascending=False
    )
    [
        [
            "Player",
            "Team",
            "Position",
            "Game Score",
            "Adjusted Game Score"
        ]
    ]
    .head(25)
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
# PLAYER METRICS
# =========================

col1, col2, col3 = st.columns(3)

col1.metric(
    "Game Score",
    round(player_data["Game Score"], 2)
)

col2.metric(
    "Adjusted Game Score",
    round(player_data["Adjusted Game Score"], 2)
)

col3.metric(
    "TOI",
    round(player_data["Time on ice"], 1)
)

# =========================
# DETAILS TABLE
# =========================

st.subheader("📋 Details")

details = pd.DataFrame({
    "Metric": [
        "Goals/60",
        "Assists/60",
        "xG/60",
        "Net xG",
        "Puck battles/60"
    ],
    "Value": [
        round(player_data["Goals/60"], 2),
        round(player_data["Assists/60"], 2),
        round(player_data["xG/60"], 2),
        round(player_data["Net xG"], 2),
        round(player_data["Puck battles/60"], 2)
    ]
})

st.dataframe(
    details,
    use_container_width=True
)
