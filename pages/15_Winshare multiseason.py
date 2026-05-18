import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import zscore
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
        .str.replace("/", "_")
        .str.replace("%", "perc")
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
    )

    teams.columns = (
        teams.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("/", "_")
        .str.replace("%", "perc")
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
    )

    # ---------------------------------------------------
    # CLEAN STRINGS
    # ---------------------------------------------------

    for df_ in [players, teams]:

        df_["Season"] = (
            df_["Season"]
            .astype(str)
            .str.strip()
        )

        df_["Team"] = (
            df_["Team"]
            .astype(str)
            .str.strip()
        )

    # ---------------------------------------------------
    # TEAM STATS
    # ---------------------------------------------------

    teams["GPG"] = (
        teams["Goal_for"] / teams["GP"]
    )

    teams["GAPG"] = (
        teams["Goal_agn"] / teams["GP"]
    )

    # ---------------------------------------------------
    # MERGE
    # ---------------------------------------------------

    df = players.merge(
        teams,
        on=["Season", "Team"],
        how="left"
    )

    # ---------------------------------------------------
    # FIX POSITION
    # ---------------------------------------------------

    if "Player" in df.columns:

        df.loc[
            df["Player"].astype(str).str.contains(
                "Elisa Holopainen",
                case=False,
                na=False
            ),
            "Position"
        ] = "F"

    # ---------------------------------------------------
    # NUMERIC
    # ---------------------------------------------------

    numeric_cols = df.select_dtypes(
        include=np.number
    ).columns

    df[numeric_cols] = (
        df[numeric_cols]
        .fillna(0)
    )

    # ---------------------------------------------------
    # AVOID DIVISION BY ZERO
    # ---------------------------------------------------

    df["Time_on_ice"] = (
        df["Time_on_ice"]
        .replace(0, np.nan)
    )

    # ---------------------------------------------------
    # CREATE PER60 STATS
    # ---------------------------------------------------

    df["Goals60"] = (
        df["Goals"] /
        df["Time_on_ice"]
    ) * 60

    df["Assists60"] = (
        df["Assists"] /
        df["Time_on_ice"]
    ) * 60

    df["xG60"] = (
        df["xG_Expected_goals"] /
        df["Time_on_ice"]
    ) * 60

    df["Takeaways60"] = (
        df["Takeaways"] /
        df["Time_on_ice"]
    ) * 60

    df["PuckLosses60"] = (
        df["Puck_losses"] /
        df["Time_on_ice"]
    ) * 60

    df["NetPenalties60"] = (

        (
            df["Penalties_drawn"] -
            df["Penalties"]
        )

        /

        df["Time_on_ice"]

    ) * 60

    # ---------------------------------------------------
    # OTHER METRICS
    # ---------------------------------------------------

    df["SlotPasses"] = (
        df["Passes_to_the_slot"]
    )

    df["PuckBattlesWon"] = (
        df["Puck_battles_won"]
    )

    # ---------------------------------------------------
    # FIND NET xG COLUMN AUTOMATICALLY
    # ---------------------------------------------------

    netxg_col = [

        col for col in df.columns

        if "Net_xG" in col

    ][0]

    df["NetxG"] = df[netxg_col]

    # ---------------------------------------------------
    # FILL AGAIN
    # ---------------------------------------------------

    df = df.fillna(0)

    # ---------------------------------------------------
    # METRICS
    # ---------------------------------------------------

    metrics = [

        # OFFENSE
        "Goals60",
        "Assists60",
        "xG60",
        "SlotPasses",

        # DEFENSE
        "NetxG",
        "Takeaways60",
        "PuckLosses60",
        "NetPenalties60",
        "PuckBattlesWon"

    ]

    # ---------------------------------------------------
    # STORE RESULTS
    # ---------------------------------------------------

    all_results = []

    # ---------------------------------------------------
    # SINGLE SEASON ENGINE
    # ---------------------------------------------------

    seasons = sorted(
        df["Season"].unique()
    )

    for season in seasons:

        # ---------------------------------------------------
        # FILTER SEASON
        # ---------------------------------------------------

        season_df = df[
            df["Season"] == season
        ].copy()

        # ---------------------------------------------------
        # CREATE EMPTY Z-COLUMNS
        # ---------------------------------------------------

        for metric in metrics:

            season_df[f"{metric}_z"] = 0.0

        # ---------------------------------------------------
        # POSITION ADJUSTED Z-SCORES
        # ---------------------------------------------------

        for metric in metrics:

            for position in ["F", "D"]:

                pos_mask = (
                    season_df["Position"] == position
                )

                values = season_df.loc[
                    pos_mask,
                    metric
                ]

                if len(values) < 2:

                    season_df.loc[
                        pos_mask,
                        f"{metric}_z"
                    ] = 0.0

                else:

                    z_values = zscore(values)

                    z_values = np.nan_to_num(
                        z_values
                    )

                    # CLIP EXTREMES

                    z_values = np.clip(
                        z_values,
                        -3,
                        3
                    )

                    season_df.loc[
                        pos_mask,
                        f"{metric}_z"
                    ] = z_values.astype(float)

        # ---------------------------------------------------
        # LEAGUE AVERAGES
        # ---------------------------------------------------

        league_gpg = (
            season_df["GPG"].mean()
        )

        league_gapg = (
            season_df["GAPG"].mean()
        )

        # ---------------------------------------------------
        # TEAM STRENGTH
        # ---------------------------------------------------

        season_df["Team_Off_Strength"] = (
            season_df["GPG"] / league_gpg
        )

        season_df["Team_Def_Strength"] = (
            league_gapg / season_df["GAPG"]
        )

        # ---------------------------------------------------
        # RAW OWS
        # ---------------------------------------------------

        season_df["Raw_OWS"] = (

            0.30 * season_df["Goals60_z"] +
            0.35 * season_df["Assists60_z"] +
            0.20 * season_df["xG60_z"] +
            0.15 * season_df["SlotPasses_z"]

        )

        # ---------------------------------------------------
        # RAW DWS
        # ---------------------------------------------------

        season_df["Raw_DWS"] = (

            0.40 * season_df["NetxG_z"] +
            0.20 * season_df["Takeaways60_z"] -
            0.20 * season_df["PuckLosses60_z"] +
            0.10 * season_df["NetPenalties60_z"] +
            0.10 * season_df["PuckBattlesWon_z"]

        )

        # ---------------------------------------------------
        # LIGHT TEAM ADJUSTMENT
        # ---------------------------------------------------

        season_df["OWS"] = (

            season_df["Raw_OWS"]

            -

            (
                (
                    season_df["Team_Off_Strength"] - 1
                )
                * 0.15
            )

        )

        season_df["DWS"] = (

            season_df["Raw_DWS"]

            -

            (
                (
                    season_df["Team_Def_Strength"] - 1
                )
                * 0.10
            )

        )

        # ---------------------------------------------------
        # TOI STABILIZATION
        # ---------------------------------------------------

        K = 400

        season_df["TOI_Factor"] = (

            season_df["Time_on_ice"]

            /

            (
                season_df["Time_on_ice"] + K
            )

        )

        season_df["OWS"] = (
            season_df["OWS"] *
            season_df["TOI_Factor"]
        )

        season_df["DWS"] = (
            season_df["DWS"] *
            season_df["TOI_Factor"]
        )

        # ---------------------------------------------------
        # FINAL WS
        # ---------------------------------------------------

        season_df["WS"] = (

            (season_df["OWS"] * 0.75)

            +

            (season_df["DWS"] * 0.25)

        )

        # ---------------------------------------------------
        # PERCENTILES
        # ---------------------------------------------------

        season_df["WS_percentile"] = (
            season_df["WS"]
            .rank(pct=True) * 100
        )

        # ---------------------------------------------------
        # RANKS
        # ---------------------------------------------------

        season_df["WS_rank"] = (
            season_df["WS"]
            .rank(
                ascending=False,
                method="min"
            )
            .astype(int)
        )

        # ---------------------------------------------------
        # STORE RESULTS
        # ---------------------------------------------------

        all_results.append(
            season_df
        )

    # ---------------------------------------------------
    # FINAL DATAFRAME
    # ---------------------------------------------------

    final_df = pd.concat(
        all_results,
        ignore_index=True
    )

    return final_df

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

df = load_data()

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------

st.title("🏒 Winshare Multiseason")

# ---------------------------------------------------
# FILTERS
# ---------------------------------------------------

c1, c2, c3 = st.columns(3)

with c1:

    season_filter = st.selectbox(
        "Season",
        sorted(df["Season"].unique())
    )

with c2:

    available_teams = sorted(
        df[
            df["Season"] == season_filter
        ]["Team"].unique()
    )

    team_filter = st.selectbox(
        "Team",
        ["All"] + available_teams
    )

with c3:

    position_filter = st.selectbox(
        "Position",
        ["All", "F", "D"]
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

# ---------------------------------------------------
# TOP PLAYERS
# ---------------------------------------------------

st.subheader("Top Win Shares")

top_df = (

    filtered_df[[
        "Player",
        "Team",
        "Position",
        "OWS",
        "DWS",
        "WS",
        "WS_percentile"
    ]]

    .sort_values(
        "WS",
        ascending=False
    )

)

st.dataframe(
    top_df,
    use_container_width=True,
    hide_index=True
)

# ---------------------------------------------------
# PLAYER SELECT
# ---------------------------------------------------

player = st.selectbox(
    "Select Player",
    sorted(filtered_df["Player"].unique())
)

player_df = filtered_df[
    filtered_df["Player"] == player
].iloc[0]

# ---------------------------------------------------
# PLAYER HEADER
# ---------------------------------------------------

st.subheader(
    f"{player_df['Player']} | "
    f"{player_df['Team']} | "
    f"{player_df['Season']} | "
    f"{player_df['Position']}"
)

# ---------------------------------------------------
# PLAYER METRICS
# ---------------------------------------------------

m1, m2, m3 = st.columns(3)

with m1:

    st.metric(
        "OWS",
        round(player_df["OWS"], 2)
    )

with m2:

    st.metric(
        "DWS",
        round(player_df["DWS"], 2)
    )

with m3:

    st.metric(
        "WS",
        f"{round(player_df['WS'],2)} "
        f"(#{player_df['WS_rank']})"
    )

# ---------------------------------------------------
# PERCENTILE
# ---------------------------------------------------

st.metric(
    "WS Percentile",
    f"{round(player_df['WS_percentile'],1)}%"
)

# ---------------------------------------------------
# CAREER TREND
# ---------------------------------------------------

career_df = (

    df[
        df["Player"] == player
    ]

    .sort_values("Season")

)

fig = px.line(
    career_df,
    x="Season",
    y="WS",
    markers=True,
    title="Career WS Trend"
)

st.plotly_chart(
    fig,
    use_container_width=True
)
