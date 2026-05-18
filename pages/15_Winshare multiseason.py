import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Winshare Multiseason",
    page_icon="🏒",
    layout="wide"
)

# ---------------------------------------------------
# FILE
# ---------------------------------------------------

FILE = "Sdhl 2023-2026_players_teams.xlsx"

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

@st.cache_data
def load_data():

    # ---------------------------------------------------
    # READ EXCEL
    # ---------------------------------------------------

    players = pd.read_excel(
        FILE,
        sheet_name="Players"
    )

    teams = pd.read_excel(
        FILE,
        sheet_name="Teams"
    )

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
        .str.replace("%", "perc")
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
    )

    players.columns = players.columns.str.replace("__", "_")
    teams.columns = teams.columns.str.replace("__", "_")

    # ---------------------------------------------------
    # CLEAN TEAM + SEASON
    # ---------------------------------------------------

    players["Team"] = (
        players["Team"]
        .astype(str)
        .str.strip()
    )

    teams["Team"] = (
        teams["Team"]
        .astype(str)
        .str.strip()
    )

    players["Season"] = (
        players["Season"]
        .astype(str)
        .str.strip()
    )

    teams["Season"] = (
        teams["Season"]
        .astype(str)
        .str.strip()
    )

    # ---------------------------------------------------
    # TEAM STATS
    # ---------------------------------------------------

    teams["GPG"] = (
        pd.to_numeric(
            teams["Goal_for"],
            errors="coerce"
        ).fillna(0)

        /

        pd.to_numeric(
            teams["GP"],
            errors="coerce"
        ).fillna(1)
    )

    teams["GAPG"] = (
        pd.to_numeric(
            teams["Goal_agn"],
            errors="coerce"
        ).fillna(0)

        /

        pd.to_numeric(
            teams["GP"],
            errors="coerce"
        ).fillna(1)
    )

    # ---------------------------------------------------
    # MERGE
    # ---------------------------------------------------

    df = players.merge(
        teams,
        on=["Season", "Team"],
        how="inner"
    )

    # ---------------------------------------------------
    # FIX POSITION
    # ---------------------------------------------------

    df.loc[
        df["Player"] == "Elisa Holopainen",
        "Position"
    ] = "F"

    # ---------------------------------------------------
    # RENAME IMPORTANT COLUMNS
    # ---------------------------------------------------

    rename_dict = {

        # offense
        "Goals_per_60": "Goals60",
        "Assists_per_60": "Assists60",
        "xG_per_60": "xG60",

        # defense
        "Takeaways_per_60": "Takeaways60",
        "Puck_losses_per_60": "PuckLosses60",
        "Net_penalties_per_60": "NetPenalties60",

        # other
        "Passes_to_the_slot": "SlotPasses",
        "Puck_battles_won": "PuckBattlesWon",
        "Net_xG": "NetxG"

    }

    df = df.rename(columns=rename_dict)

    # ---------------------------------------------------
    # CONVERT NUMERIC
    # ---------------------------------------------------

    for col in df.columns:

        if col not in [
            "Player",
            "Team",
            "Position",
            "Season"
        ]:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    df = df.fillna(0)

    # ---------------------------------------------------
    # EXISTING METRICS ONLY
    # ---------------------------------------------------

    possible_offensive = [

        "Goals60",
        "Assists60",
        "xG60",
        "SlotPasses"

    ]

    possible_defensive = [

        "NetxG",
        "Takeaways60",
        "PuckLosses60",
        "NetPenalties60",
        "PuckBattlesWon"

    ]

    offensive_metrics = [

        x for x in possible_offensive
        if x in df.columns

    ]

    defensive_metrics = [

        x for x in possible_defensive
        if x in df.columns

    ]

    all_metrics = (
        offensive_metrics +
        defensive_metrics
    )

    # ---------------------------------------------------
    # Z-SCORES
    # POSITION + SEASON ADJUSTED
    # ---------------------------------------------------

    for metric in all_metrics:

        df[f"{metric}_z"] = (

            df.groupby(
                ["Season", "Position"]
            )[metric]

            .transform(

                lambda x:

                (
                    (x - x.mean())

                    /

                    x.std()

                )

                if x.std() != 0

                else 0

            )

        )

        df[f"{metric}_z"] = (

            df[f"{metric}_z"]
            .replace([np.inf, -np.inf], 0)
            .fillna(0)

        )

    # ---------------------------------------------------
    # RAW OFFENSE
    # ---------------------------------------------------

    df["Raw_OWS"] = 0

    if "Goals60_z" in df.columns:
        df["Raw_OWS"] += (
            0.35 * df["Goals60_z"]
        )

    if "Assists60_z" in df.columns:
        df["Raw_OWS"] += (
            0.35 * df["Assists60_z"]
        )

    if "xG60_z" in df.columns:
        df["Raw_OWS"] += (
            0.20 * df["xG60_z"]
        )

    if "SlotPasses_z" in df.columns:
        df["Raw_OWS"] += (
            0.10 * df["SlotPasses_z"]
        )

    # ---------------------------------------------------
    # RAW DEFENSE
    # ---------------------------------------------------

    df["Raw_DWS"] = 0

    if "NetxG_z" in df.columns:
        df["Raw_DWS"] += (
            0.50 * df["NetxG_z"]
        )

    if "Takeaways60_z" in df.columns:
        df["Raw_DWS"] += (
            0.15 * df["Takeaways60_z"]
        )

    if "PuckLosses60_z" in df.columns:
        df["Raw_DWS"] -= (
            0.15 * df["PuckLosses60_z"]
        )

    if "NetPenalties60_z" in df.columns:
        df["Raw_DWS"] += (
            0.10 * df["NetPenalties60_z"]
        )

    if "PuckBattlesWon_z" in df.columns:
        df["Raw_DWS"] += (
            0.10 * df["PuckBattlesWon_z"]
        )

    # ---------------------------------------------------
    # INITIALIZE
    # ---------------------------------------------------

    df["OWS"] = 0.0
    df["DWS"] = 0.0

    # ---------------------------------------------------
    # SEASON LOOP
    # ---------------------------------------------------

    for season in df["Season"].unique():

        season_mask = (
            df["Season"] == season
        )

        # league averages

        league_gpg = (
            df.loc[
                season_mask,
                "GPG"
            ].mean()
        )

        league_gapg = (
            df.loc[
                season_mask,
                "GAPG"
            ].mean()
        )

        # team strengths

        off_strength = (

            df.loc[
                season_mask,
                "GPG"
            ]

            /

            league_gpg

        )

        def_strength = (

            league_gapg

            /

            df.loc[
                season_mask,
                "GAPG"
            ]

        )

        # adjusted

        df.loc[
            season_mask,
            "OWS"
        ] = (

            df.loc[
                season_mask,
                "Raw_OWS"
            ]

            /

            (
                off_strength ** 0.35
            )

        )

        df.loc[
            season_mask,
            "DWS"
        ] = (

            df.loc[
                season_mask,
                "Raw_DWS"
            ]

            /

            (
                def_strength ** 0.25
            )

        )

    # ---------------------------------------------------
    # SCALE
    # ---------------------------------------------------

    SCALE = 1.8

    df["OWS"] = (
        (df["OWS"] + 2)
        * SCALE
    )

    df["DWS"] = (
        (df["DWS"] + 2)
        * SCALE
        * 0.8
    )

    # ---------------------------------------------------
    # FLOOR
    # ---------------------------------------------------

    df["OWS"] = df["OWS"].clip(lower=0)
    df["DWS"] = df["DWS"].clip(lower=0)

    # ---------------------------------------------------
    # TOI STABILIZATION
    # ---------------------------------------------------

    K = 250

    if "Time_on_ice" in df.columns:

        df["TOI_Factor"] = (

            df["Time_on_ice"]

            /

            (
                df["Time_on_ice"] + K
            )

        )

    else:

        df["TOI_Factor"] = 1

    df["OWS"] = (
        df["OWS"] *
        df["TOI_Factor"]
    )

    df["DWS"] = (
        df["DWS"] *
        df["TOI_Factor"]
    )

    # ---------------------------------------------------
    # FINAL WS
    # ---------------------------------------------------

    df["WS"] = (
        df["OWS"] +
        df["DWS"]
    )

    # ---------------------------------------------------
    # PERCENTILES
    # ---------------------------------------------------

    df["OWS_percentile"] = (

        df.groupby("Season")["OWS"]

        .rank(pct=True)

        * 100

    )

    df["DWS_percentile"] = (

        df.groupby("Season")["DWS"]

        .rank(pct=True)

        * 100

    )

    df["WS_percentile"] = (

        df.groupby("Season")["WS"]

        .rank(pct=True)

        * 100

    )

    # ---------------------------------------------------
    # RANKINGS
    # ---------------------------------------------------

    df["OWS_rank"] = (

        df.groupby("Season")["OWS"]

        .rank(
            ascending=False,
            method="min"
        )

    )

    df["DWS_rank"] = (

        df.groupby("Season")["DWS"]

        .rank(
            ascending=False,
            method="min"
        )

    )

    df["WS_rank"] = (

        df.groupby("Season")["WS"]

        .rank(
            ascending=False,
            method="min"
        )

    )

    return df

# ---------------------------------------------------
# LOAD
# ---------------------------------------------------

df = load_data()

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------

st.title("🏒 Winshare Multiseason")

# ---------------------------------------------------
# FILTERS
# ---------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

with c1:

    season_filter = st.selectbox(
        "Season",
        sorted(df["Season"].unique())
    )

with c2:

    team_options = sorted(

        df[
            df["Season"] == season_filter
        ]["Team"].unique()

    )

    team_filter = st.selectbox(
        "Team",
        ["All"] + team_options
    )

with c3:

    position_filter = st.selectbox(
        "Position",
        ["All", "F", "D"]
    )

with c4:

    min_games = st.slider(
        "Minimum Games",
        1,
        int(df["Games_played"].max()),
        10
    )

# ---------------------------------------------------
# FILTER DATA
# ---------------------------------------------------

filtered_df = df.copy()

filtered_df = filtered_df[
    filtered_df["Season"] == season_filter
]

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
# PLAYER
# ---------------------------------------------------

player = st.selectbox(
    "Select Player",
    sorted(filtered_df["Player"].unique())
)

player_df = filtered_df[
    filtered_df["Player"] == player
].iloc[0]

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

st.subheader(

    f"{player_df['Player']} | "
    f"{player_df['Team']} | "
    f"{player_df['Season']} | "
    f"{player_df['Position']}"

)

# ---------------------------------------------------
# METRICS
# ---------------------------------------------------

m1, m2, m3 = st.columns(3)

with m1:

    st.metric(
        "OWS",
        f"{round(player_df['OWS'],2)} "
        f"(#{int(player_df['OWS_rank'])})"
    )

with m2:

    st.metric(
        "DWS",
        f"{round(player_df['DWS'],2)} "
        f"(#{int(player_df['DWS_rank'])})"
    )

with m3:

    st.metric(
        "WS",
        f"{round(player_df['WS'],2)} "
        f"(#{int(player_df['WS_rank'])})"
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
# CAREER TREND
# ---------------------------------------------------

st.subheader("Career Trend")

career_df = df[
    df["Player"] == player
].sort_values("Season")

fig = px.line(
    career_df,
    x="Season",
    y="WS",
    markers=True,
    hover_data=["OWS", "DWS"]
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ---------------------------------------------------
# TOP PLAYERS
# ---------------------------------------------------

st.subheader("Top 10 Win Shares")

top_df = (

    filtered_df[[
        "Player",
        "Team",
        "Position",
        "OWS",
        "DWS",
        "WS"
    ]]

    .sort_values(
        "WS",
        ascending=False
    )

    .head(10)

)

st.dataframe(
    top_df,
    use_container_width=True,
    hide_index=True
)
