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
# FILE
# ---------------------------------------------------

FILE = "Skaters - SDHL 2025-2026 WIN SHARE.xlsx"

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

@st.cache_data
def load_data():

    # READ EXCEL
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

    # REMOVE DOUBLE UNDERSCORES
    players.columns = players.columns.str.replace("__", "_")
    players.columns = players.columns.str.replace("__", "_")

    teams.columns = teams.columns.str.replace("__", "_")
    teams.columns = teams.columns.str.replace("__", "_")

    # ---------------------------------------------------
    # MERGE
    # ---------------------------------------------------

    df = players.merge(teams, on="Team")

    # ---------------------------------------------------
    # FIX PLAYER POSITIONS
    # ---------------------------------------------------

    df.loc[
        df["Player"] == "Elisa Holopainen",
        "Position"
    ] = "F"

    # ---------------------------------------------------
    # RENAME IMPORTANT COLUMNS
    # ---------------------------------------------------

    rename_dict = {

        # OFFENSE
        "Goals_per_60": "Goals60",
        "Assists_per_60": "Assists60",
        "xG_per_60": "xG60",

        # DEFENSE
        "Takeaways_per_60": "Takeaways60",
        "Puck_losses_per_60": "PuckLosses60",
        "Net_penalties_per_60": "NetPenalties60",

        # OTHER
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

            # REPLACE NaN
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
        df["OWS"].rank(pct=True) * 100
    )

    df["DWS_percentile"] = (
        df["DWS"].rank(pct=True) * 100
    )

    df["WS_percentile"] = (
        df["WS"].rank(pct=True) * 100
    )

    return df

# ---------------------------------------------------
# LOAD DATA
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
- Overall Win Shares (WS)
- Radar charts
- Percentiles
- Team filters
- Position filters
""")

# ---------------------------------------------------
# FILTERS
# ---------------------------------------------------

filter_col1, filter_col2, filter_col3 = st.columns(3)

# TEAM FILTER
with filter_col1:

    team_filter = st.selectbox(
        "Select Team",
        ["All"] + sorted(df["Team"].unique().tolist())
    )

# POSITION FILTER
with filter_col2:

    position_filter = st.selectbox(
        "Select Position",
        ["All", "F", "D"]
    )

# MINIMUM GAMES FILTER
with filter_col3:

    min_games = st.slider(
        "Minimum Games Played",
        1,
        int(df["Games_played"].max()),
        10
    )

# ---------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------

filtered_df = df.copy()

if team_filter != "All":

    filtered_df = filtered_df[
        filtered_df["Team"] == team_filter
    ]

if position_filter != "All":

    filtered_df = filtered_df[
        filtered_df["Position"] == position_filter
    ]

filtered_df = filtered_df[
    filtered_df["Games_played"] >= min_games
]

# ---------------------------------------------------
# PLAYER SELECTOR
# ---------------------------------------------------

player = st.selectbox(
    "Select Player",
    sorted(filtered_df["Player"].unique())
)

# ---------------------------------------------------
# PLAYER DATA
# ---------------------------------------------------

player_df = filtered_df[
    filtered_df["Player"] == player
].iloc[0]

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
# PLAYER INFORMATION
# ---------------------------------------------------

st.subheader("Player Information")

info1, info2, info3, info4 = st.columns(4)

with info1:

    st.write(
        f"**Games Played:** "
        f"{player_df['Games_played']}"
    )

with info2:

    st.write(
        f"**Time on Ice:** "
        f"{round(player_df['Time_on_ice'], 1)}"
    )

with info3:

    st.write(
        f"**Points:** "
        f"{player_df['Points']}"
    )

with info4:

    st.write(
        f"**Net xG:** "
        f"{round(player_df['NetxG'], 2)}"
    )

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

        player_df["Goals60_z"],
        player_df["Assists60_z"],
        player_df["xG60_z"],
        player_df["NetxG_z"],
        player_df["Takeaways60_z"],
        player_df["PuckBattlesWon_z"]

    ]

})

fig = px.line_polar(
    radar_df,
    r="Value",
    theta="Metric",
    line_close=True
)

fig.update_traces(fill="toself")

fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[-3, 3]
        )
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ---------------------------------------------------
# ADDITIONAL STATISTICS
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
# TOP 10 WIN SHARES
# ---------------------------------------------------

st.subheader("Top 10 Win Shares")

top_ws = (

    filtered_df[[
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
