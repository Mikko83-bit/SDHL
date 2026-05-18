import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.stats import zscore

st.set_page_config(
    page_title="Player Profiles",
    page_icon="🏒",
    layout="wide"
)

FILE = "Skaters - SDHL 2025-2026 WIN SHARE.xlsx"

@st.cache_data
def load_data():

    # READ EXCEL
    players = pd.read_excel(FILE, sheet_name="Players")
    teams = pd.read_excel(FILE, sheet_name="Teams")

    # CLEAN COLUMN NAMES
    players.columns = (
        players.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("/", "_per_")
        .str.replace("%", "perc")
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
    )

    teams.columns = (
        teams.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("/", "_per_")
    )

    # MERGE PLAYER + TEAM DATA
    df = players.merge(teams, on="Team")

    # RENAME IMPORTANT COLUMNS
    df = df.rename(columns={
        "Goals_per_60": "Goals60",
        "Assists_per_60": "Assists60",
        "xG_per_60": "xG60",
        "Takeaways__per_60": "Takeaways60",
        "Puck_losses_per_60": "PuckLosses60",
        "Net_penalties_per_60": "NetPenalties60",
        "Passes_to_the_slot": "SlotPasses",
        "Puck_battles_won": "PuckBattlesWon",
        "Net_xG": "NetxG"
    })

    # FILL MISSING VALUES
    numeric_cols = df.select_dtypes(include=np.number).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)

    # METRICS FOR Z-SCORES
    metrics = [
        "Goals60",
        "Assists60",
        "xG60",
        "Scoring_chances",
        "SlotPasses",
        "NetxG",
        "Takeaways60",
        "PuckLosses60",
        "NetPenalties60",
        "PuckBattlesWon"
    ]

    # CREATE Z-SCORES
    for metric in metrics:
        if metric in df.columns:
            df[f"{metric}_z"] = zscore(df[metric])

    # OFFENSIVE WIN SHARES
    df["OWS"] = (
        0.30 * df["Goals60_z"] +
        0.35 * df["Assists60_z"] +
        0.20 * df["xG60_z"] +
        0.15 * df["SlotPasses_z"]
    )

    # DEFENSIVE WIN SHARES
    df["DWS"] = (
        0.40 * df["NetxG_z"] +
        0.20 * df["Takeaways60_z"] -
        0.20 * df["PuckLosses60_z"] +
        0.10 * df["NetPenalties60_z"] +
        0.10 * df["PuckBattlesWon_z"]
    )

    # TOTAL WIN SHARES
    df["WS"] = df["OWS"] + df["DWS"]

    # PERCENTILES
    df["OWS_percentile"] = df["OWS"].rank(pct=True) * 100
    df["DWS_percentile"] = df["DWS"].rank(pct=True) * 100
    df["WS_percentile"] = df["WS"].rank(pct=True) * 100

    return df


# LOAD DATA
df = load_data()

# TITLE
st.title("🏒 Player Profiles")

# PLAYER SELECTOR
player = st.selectbox(
    "Select Player",
    sorted(df["Player"].unique())
)

# PLAYER DATA
player_df = df[df["Player"] == player].iloc[0]

# HEADER
st.subheader(f"{player_df['Player']} | {player_df['Team']}")

# MAIN METRICS
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Offensive Win Shares",
        round(player_df["OWS"], 2)
    )

with col2:
    st.metric(
        "Defensive Win Shares",
        round(player_df["DWS"], 2)
    )

with col3:
    st.metric(
        "Total Win Shares",
        round(player_df["WS"], 2)
    )

# PLAYER INFO
st.subheader("Player Information")

info_col1, info_col2, info_col3, info_col4 = st.columns(4)

with info_col1:
    st.write(f"**Position:** {player_df['Position']}")

with info_col2:
    st.write(f"**Games Played:** {player_df['Games_played']}")

with info_col3:
    st.write(f"**Time on Ice:** {player_df['Time_on_ice']}")

with info_col4:
    st.write(f"**Points:** {player_df['Points']}")

# RADAR DATA
radar_df = pd.DataFrame({
    "Metric": [
        "Goals60",
        "Assists60",
        "xG60",
        "NetxG",
        "Takeaways60",
        "PuckBattlesWon"
    ],
    "Value": [
        player_df["Goals60"],
        player_df["Assists60"],
        player_df["xG60"],
        player_df["NetxG"],
        player_df["Takeaways60"],
        player_df["PuckBattlesWon"]
    ]
})

# RADAR CHART
fig = px.line_polar(
    radar_df,
    r="Value",
    theta="Metric",
    line_close=True
)

fig.update_traces(fill='toself')

st.subheader("Player Radar")

st.plotly_chart(
    fig,
    use_container_width=True
)

# ADDITIONAL STATS
st.subheader("Additional Statistics")

stats_df = pd.DataFrame({
    "Statistic": [
        "Goals/60",
        "Assists/60",
        "xG/60",
        "Net xG",
        "Takeaways/60",
        "Puck Losses/60",
        "Net Penalties/60",
        "Puck Battles Won"
    ],
    "Value": [
        round(player_df["Goals60"], 2),
        round(player_df["Assists60"], 2),
        round(player_df["xG60"], 2),
        round(player_df["NetxG"], 2),
        round(player_df["Takeaways60"], 2),
        round(player_df["PuckLosses60"], 2),
        round(player_df["NetPenalties60"], 2),
        round(player_df["PuckBattlesWon"], 2)
    ]
})

st.dataframe(
    stats_df,
    use_container_width=True,
    hide_index=True
)

# PERCENTILES
st.subheader("League Percentiles")

perc_col1, perc_col2, perc_col3 = st.columns(3)

with perc_col1:
    st.metric(
        "OWS Percentile",
        f"{round(player_df['OWS_percentile'])}%"
    )

with perc_col2:
    st.metric(
        "DWS Percentile",
        f"{round(player_df['DWS_percentile'])}%"
    )

with perc_col3:
    st.metric(
        "WS Percentile",
        f"{round(player_df['WS_percentile'])}%"
    )
