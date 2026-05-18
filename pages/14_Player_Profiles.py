import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.stats import zscore

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="SDHL Player Profiles",
    page_icon="🏒",
    layout="wide"
)

# ---------------------------------------------------
# FILE NAME
# ---------------------------------------------------

FILE = "Skaters - SDHL 2025-2026 WIN SHARE.xlsx"

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

@st.cache_data
def load_data():

    # READ EXCEL SHEETS
    players = pd.read_excel(FILE, sheet_name="Players")
    teams = pd.read_excel(FILE, sheet_name="Teams")

    # ---------------------------------------------------
    # CLEAN COLUMN NAMES
    # ---------------------------------------------------

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

    # ---------------------------------------------------
    # MERGE DATA
    # ---------------------------------------------------

    df = players.merge(teams, on="Team")

    # ---------------------------------------------------
    # RENAME COLUMNS
    # ---------------------------------------------------

    rename_dict = {
        "Goals_per_60": "Goals60",
        "Assists_per_60": "Assists60",
        "xG_per_60": "xG60",
        "Takeaways__per_60": "Takeaways60",
        "Puck_losses_per_60": "PuckLosses60",
        "Net_penalties_per_60": "NetPenalties60",
        "Passes_to_the_slot": "SlotPasses",
        "Puck_battles_won": "PuckBattlesWon",
        "Net_xG": "NetxG"
    }

    df = df.rename(columns=rename_dict)

    # ---------------------------------------------------
    # FILL MISSING VALUES
    # ---------------------------------------------------

    numeric_cols = df.select_dtypes(include=np.number).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)

    # ---------------------------------------------------
    # CREATE Z-SCORES
    # ---------------------------------------------------

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

    for metric in metrics:

        if metric in df.columns:

            df[f"{metric}_z"] = zscore(df[metric])

            # FIX NaN VALUES
            df[f"{metric}_z"] = (
                df[f"{metric}_z"]
                .replace(np.nan, 0)
            )

    # ---------------------------------------------------
    # OFFENSIVE WIN SHARES
    # ---------------------------------------------------

    df["OWS"] = (
        0.30 * df["Goals60_z"] +
        0.35 * df["Assists60_z"] +
        0.20 * df["xG60_z"] +
        0.15 * df["SlotPasses_z"]
    )

    # ---------------------------------------------------
    # DEFENSIVE WIN SHARES
    # ---------------------------------------------------

    df["DWS"] = (
        0.40 * df["NetxG_z"] +
        0.20 * df["Takeaways60_z"] -
        0.20 * df["PuckLosses60_z"] +
        0.10 * df["NetPenalties60_z"] +
        0.10 * df["PuckBattlesWon_z"]
    )

    # ---------------------------------------------------
    # TOTAL WIN SHARES
    # ---------------------------------------------------

    df["WS"] = df["OWS"] + df["DWS"]

    # ---------------------------------------------------
    # PERCENTILES
    # ---------------------------------------------------

    df["OWS_percentile"] = (
        df["OWS"]
        .rank(pct=True) * 100
    )

    df["DWS_percentile"] = (
        df["DWS"]
        .rank(pct=True) * 100
    )

    df["WS_percentile"] = (
        df["WS"]
        .rank(pct=True) * 100
    )

    return df


# ---------------------------------------------------
# LOAD DATAFRAME
# ---------------------------------------------------

df = load_data()

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------

st.title("🏒 SDHL Player Profiles")

st.markdown("""
This dashboard includes:

- Offensive Win Shares (OWS)
- Defensive Win Shares (DWS)
- Total Win Shares (WS)
- Player percentiles
- Radar visualization
""")

# ---------------------------------------------------
# PLAYER SELECTOR
# ---------------------------------------------------

player = st.selectbox(
    "Select Player",
    sorted(df["Player"].unique())
)

# ---------------------------------------------------
# PLAYER DATA
# ---------------------------------------------------

player_df = df[df["Player"] == player].iloc[0]

# ---------------------------------------------------
# PLAYER HEADER
# ---------------------------------------------------

st.subheader(
    f"{player_df['Player']} | "
    f"{player_df['Team']} | "
    f"{player_df['Position']}"
)

# ---------------------------------------------------
# MAIN METRICS
# ---------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "OWS",
        round(player_df["OWS"], 2)
    )

with col2:
    st.metric(
        "DWS",
        round(player_df["DWS"], 2)
    )

with col3:
    st.metric(
        "WS",
        round(player_df["WS"], 2)
    )

# ---------------------------------------------------
# PLAYER INFO
# ---------------------------------------------------

st.subheader("Player Information")

info1, info2, info3, info4 = st.columns(4)

with info1:
    st.write(f"**Games Played:** {player_df['Games_played']}")

with info2:
    st.write(f"**Time on Ice:** {player_df['Time_on_ice']}")

with info3:
    st.write(f"**Points:** {player_df['Points']}")

with info4:
    st.write(f"**Net xG:** {round(player_df['NetxG'], 2)}")

# ---------------------------------------------------
# RADAR CHART
# ---------------------------------------------------

st.subheader("Player Radar")

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

fig = px.line_polar(
    radar_df,
    r="Value",
    theta="Metric",
    line_close=True
)

fig.update_traces(fill="toself")

st.plotly_chart(
    fig,
    use_container_width=True
)

# ---------------------------------------------------
# ADDITIONAL STATS TABLE
# ---------------------------------------------------

st.subheader("Additional Statistics")

stats_df = pd.DataFrame({
    "Statistic": [
        "Goals/60",
        "Assists/60",
        "xG/60",
        "Takeaways/60",
        "Puck Losses/60",
        "Net Penalties/60",
        "Puck Battles Won",
        "Slot Passes"
    ],
    "Value": [
        round(player_df["Goals60"], 2),
        round(player_df["Assists60"], 2),
        round(player_df["xG60"], 2),
        round(player_df["Takeaways60"], 2),
        round(player_df["PuckLosses60"], 2),
        round(player_df["NetPenalties60"], 2),
        round(player_df["PuckBattlesWon"], 2),
        round(player_df["SlotPasses"], 2)
    ]
})

st.dataframe(
    stats_df,
    use_container_width=True,
    hide_index=True
)

# ---------------------------------------------------
# PERCENTILES
# ---------------------------------------------------

st.subheader("League Percentiles")

p1, p2, p3 = st.columns(3)

with p1:
    st.metric(
        "OWS Percentile",
        f"{round(player_df['OWS_percentile'])}%"
    )

with p2:
    st.metric(
        "DWS Percentile",
        f"{round(player_df['DWS_percentile'])}%"
    )

with p3:
    st.metric(
        "WS Percentile",
        f"{round(player_df['WS_percentile'])}%"
    )

# ---------------------------------------------------
# TOP PLAYERS
# ---------------------------------------------------

st.subheader("Top 10 Win Shares")

top_ws = (
    df[[
        "Player",
        "Team",
        "Position",
        "OWS",
        "DWS",
        "WS"
    ]]
    .sort_values("WS", ascending=False)
    .head(10)
)

st.dataframe(
    top_ws,
    use_container_width=True,
    hide_index=True
)
