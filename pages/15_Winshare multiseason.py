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
    # CLEAN COLUMNS
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
    # CLEAN TEAM + SEASON
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
        how="inner"
    )

    # ---------------------------------------------------
    # FIX POSITIONS
    # ---------------------------------------------------

    df.loc[
        df["Player"] == "Elisa Holopainen",
        "Position"
    ] = "F"

    # ---------------------------------------------------
    # RENAME COLUMNS
    # ---------------------------------------------------

    rename_dict = {

        "Goals_per_60": "Goals60",
        "Assists_per_60": "Assists60",
        "xG_per_60": "xG60",

        "Takeaways_per_60": "Takeaways60",
        "Puck_losses_per_60": "PuckLosses60",
        "Net_penalties_per_60": "NetPenalties60",

        "Passes_to_the_slot": "SlotPasses",
        "Puck_battles_won": "PuckBattlesWon",

        "Net_xG": "NetxG"

    }

    df = df.rename(columns=rename_dict)

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
    # METRICS
    # ---------------------------------------------------

    offensive_metrics = [
        "Goals60",
        "Assists60",
        "xG60",
        "SlotPasses"
    ]

    defensive_metrics = [
        "NetxG",
        "Takeaways60",
        "PuckLosses60",
        "NetPenalties60",
        "PuckBattlesWon"
    ]

    # ---------------------------------------------------
    # KEEP ONLY EXISTING
    # ---------------------------------------------------

    offensive_metrics = [
        x for x in offensive_metrics
        if x in df.columns
    ]

    defensive_metrics = [
        x for x in defensive_metrics
        if x in df.columns
    ]

    all_metrics = (
        offensive_metrics +
        defensive_metrics
    )

    # ---------------------------------------------------
    # POSITION + SEASON Z-SCORES
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
                    / x.std()
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
    # RAW OWS
    # ---------------------------------------------------

    df["Raw_OWS"] = (

        0.30 * df.get("Goals60_z", 0) +
        0.35 * df.get("Assists60_z", 0) +
        0.20 * df.get("xG60_z", 0) +
        0.15 * df.get("SlotPasses_z", 0)

    )

    # ---------------------------------------------------
    # RAW DWS
    # ---------------------------------------------------

    df["Raw_DWS"] = (

        0.40 * df.get("NetxG_z", 0) +
        0.20 * df.get("Takeaways60_z", 0) -
        0.20 * df.get("PuckLosses60_z", 0) +
        0.10 * df.get("NetPenalties60_z", 0) +
        0.10 * df.get("PuckBattlesWon_z", 0)

    )

    # ---------------------------------------------------
    # INITIALIZE
    # ---------------------------------------------------

    df["OWS"] = 0.0
    df["DWS"] = 0.0

    # ---------------------------------------------------
    # TEAM ADJUSTMENT
    # ---------------------------------------------------

    for season in df["Season"].unique():

        season_mask = (
            df["Season"] == season
        )

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

        off_strength = (

            df.loc[
                season_mask,
                "GPG"
            ]

            / league_gpg

        )

        def_strength = (

            league_gapg

            / df.loc[
                season_mask,
                "GAPG"
            ]

        )

        # OWS

        df.loc[
            season_mask,
            "OWS"
        ] = (

            df.loc[
                season_mask,
                "Raw_OWS"
            ]

            -

            (
                (
                    off_strength - 1
                ) * 0.50
            )

        )

        # DWS

        df.loc[
            season_mask,
            "DWS"
        ] = (

            df.loc[
                season_mask,
                "Raw_DWS"
            ]

            -

            (
                (
                    def_strength - 1
                ) * 0.35
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

    K = 400

    df["TOI_Factor"] = (

        df["Time_on_ice"]

        /

        (
            df["Time_on_ice"] + K
        )

    )

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

    df["WS_percentile"] = (

        df.groupby("Season")["WS"]

        .rank(pct=True)

        * 100

    )

    # ---------------------------------------------------
    # RANKS
    # ---------------------------------------------------

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
# FILTER
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
# PLAYER INFO
# ---------------------------------------------------

st.subheader(
    f"{player_df['Player']} | "
    f"{player_df['Team']} | "
    f"{player_df['Season']}"
)

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
        round(player_df["WS"], 2)
    )

# ---------------------------------------------------
# CAREER TREND
# ---------------------------------------------------

career_df = df[
    df["Player"] == player
].sort_values("Season")

fig = px.line(
    career_df,
    x="Season",
    y="WS",
    markers=True
)

st.plotly_chart(
    fig,
    use_container_width=True
)
