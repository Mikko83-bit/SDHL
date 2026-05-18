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
    # FIX POSITIONS
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
    # NUMERIC CONVERSION
    # ---------------------------------------------------

    numeric_cols = df.select_dtypes(
        include=np.number
    ).columns

    df[numeric_cols] = (
        df[numeric_cols]
        .fillna(0)
    )

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

    # KEEP ONLY EXISTING

    metrics = [
        m for m in metrics
        if m in df.columns
    ]

    # ---------------------------------------------------
    # STORE RESULTS
    # ---------------------------------------------------

    season_results = []

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
        # CREATE Z-SCORE COLUMNS
        # ---------------------------------------------------

        for metric in metrics:

            season_df[f"{metric}_z"] = 0.0

        # ---------------------------------------------------
        # POSITION-ADJUSTED Z-SCORES
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

                # NOT ENOUGH PLAYERS

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

                    # CLIP OUTLIERS

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
        # TEAM ADJUSTMENT
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
        # TEAM ADJUSTMENT
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

        season_df["OWS_percentile"] = (
            season_df["OWS"]
            .rank(pct=True) * 100
        )

        season_df["DWS_percentile"] = (
            season_df["DWS"]
            .rank(pct=True) * 100
        )

        season_df["WS_percentile"] = (
            season_df["WS"]
            .rank(pct=True) * 100
        )

        # ---------------------------------------------------
        # RANKS
        # ---------------------------------------------------

        season_df["OWS_rank"] = (
            season_df["OWS"]
            .rank(
                ascending=False,
                method="min"
            )
            .astype(int)
        )

        season_df["DWS_rank"] = (
            season_df["DWS"]
            .rank(
                ascending=False,
                method="min"
            )
            .astype(int)
        )

        season_df["WS_rank"] = (
            season_df["WS"]
            .rank(
                ascending=False,
                method="min"
            )
            .astype(int)
        )

        # ---------------------------------------------------
        # STORE
        # ---------------------------------------------------

        season_results.append(
            season_df
        )

    # ---------------------------------------------------
    # COMBINE ALL SEASONS
    # ---------------------------------------------------

    final_df = pd.concat(
        season_results,
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

    team_filter = st.selectbox(
        "Team",
        ["All"] + sorted(
            df[
                df["Season"] == season_filter
            ]["Team"].unique()
        )
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
# TOP WIN SHARES
# ---------------------------------------------------

st.subheader("Top Win Shares")

top_ws = (

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
    top_ws,
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
# METRICS
# ---------------------------------------------------

m1, m2, m3 = st.columns(3)

with m1:

    st.metric(
        "OWS",
        f"{round(player_df['OWS'],2)} "
        f"(#{player_df['OWS_rank']})"
    )

with m2:

    st.metric(
        "DWS",
        f"{round(player_df['DWS'],2)} "
        f"(#{player_df['DWS_rank']})"
    )

with m3:

    st.metric(
        "WS",
        f"{round(player_df['WS'],2)} "
        f"(#{player_df['WS_rank']})"
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
