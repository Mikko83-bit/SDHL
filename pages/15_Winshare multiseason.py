# =========================================================
# WINSHARE MULTISEASON
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import zscore
import plotly.express as px

# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="Winshare Multiseason",
    page_icon="🏒",
    layout="wide"
)

# =========================================================
# FILE
# =========================================================

FILE = "Sdhl 2023-2026_players_teams.xlsx"

# =========================================================
# HELPERS
# =========================================================

def clean_columns(df):

    df.columns = (
        df.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("/", "_")
        .str.replace("%", "perc")
        .str.replace("-", "_")
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
        .str.replace(".", "", regex=False)
    )

    return df


def safe_zscore(series):

    series = pd.to_numeric(
        series,
        errors="coerce"
    ).fillna(0)

    if len(series.unique()) <= 1:
        return np.zeros(len(series))

    return zscore(series)


def find_column(df, keywords):

    for col in df.columns:

        col_lower = col.lower()

        if all(k.lower() in col_lower for k in keywords):
            return col

    return None


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    # =====================================================
    # READ EXCEL
    # =====================================================

    players = pd.read_excel(
        FILE,
        sheet_name="Players"
    )

    teams = pd.read_excel(
        FILE,
        sheet_name="Teams"
    )

    # =====================================================
    # CLEAN
    # =====================================================

    players = clean_columns(players)
    teams = clean_columns(teams)

    # =====================================================
    # CLEAN STRINGS
    # =====================================================

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

    # =====================================================
    # TEAM STATS
    # =====================================================

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

    # =====================================================
    # MERGE
    # =====================================================

    df = players.merge(
        teams,
        on=["Season", "Team"],
        how="left"
    )

    # =====================================================
    # FIND IMPORTANT COLUMNS
    # =====================================================

    TOI_COL = find_column(df, ["time", "ice"])
    XG_COL = find_column(df, ["expected", "goals"])
    TAKEAWAYS_COL = find_column(df, ["takeaways"])
    PUCKLOSS_COL = find_column(df, ["puck", "loss"])
    SLOTPASS_COL = find_column(df, ["passes", "slot"])
    BATTLE_COL = find_column(df, ["puck", "battles"])
    NETXG_COL = find_column(df, ["net", "xg"])
    CORSI_COL = find_column(df, ["corsi"])

    # =====================================================
    # TOI
    # =====================================================

    df["TOI"] = pd.to_numeric(
        df[TOI_COL],
        errors="coerce"
    ).fillna(0)

    df["TOI"] = df["TOI"].replace(0, np.nan)

    # =====================================================
    # BASIC STATS
    # =====================================================

    df["Goals"] = pd.to_numeric(
        df["Goals"],
        errors="coerce"
    ).fillna(0)

    df["Assists"] = pd.to_numeric(
        df["Assists"],
        errors="coerce"
    ).fillna(0)

    # =====================================================
    # PER 60
    # =====================================================

    df["Goals60"] = (
        df["Goals"] / df["TOI"]
    ) * 60

    df["Assists60"] = (
        df["Assists"] / df["TOI"]
    ) * 60

    # =====================================================
    # XG
    # =====================================================

    df["xG"] = pd.to_numeric(
        df[XG_COL],
        errors="coerce"
    ).fillna(0)

    df["xG60"] = (
        df["xG"] / df["TOI"]
    ) * 60

    # =====================================================
    # TAKEAWAYS
    # =====================================================

    df["Takeaways"] = pd.to_numeric(
        df[TAKEAWAYS_COL],
        errors="coerce"
    ).fillna(0)

    df["Takeaways60"] = (
        df["Takeaways"] / df["TOI"]
    ) * 60

    # =====================================================
    # PUCK LOSSES
    # =====================================================

    df["PuckLosses"] = pd.to_numeric(
        df[PUCKLOSS_COL],
        errors="coerce"
    ).fillna(0)

    df["PuckLosses60"] = (
        df["PuckLosses"] / df["TOI"]
    ) * 60

    # =====================================================
    # SLOT PASSES
    # =====================================================

    df["SlotPasses"] = pd.to_numeric(
        df[SLOTPASS_COL],
        errors="coerce"
    ).fillna(0)

    df["SlotPasses60"] = (
        df["SlotPasses"] / df["TOI"]
    ) * 60

    # =====================================================
    # PUCK BATTLES
    # =====================================================

    df["PuckBattlesWon"] = pd.to_numeric(
        df[BATTLE_COL],
        errors="coerce"
    ).fillna(0)

    df["PuckBattlesWon60"] = (
        df["PuckBattlesWon"] / df["TOI"]
    ) * 60

    # =====================================================
    # NET PENALTIES
    # =====================================================

    df["NetPenalties"] = (

        pd.to_numeric(
            df["Penalties_drawn"],
            errors="coerce"
        ).fillna(0)

        -

        pd.to_numeric(
            df["Penalties"],
            errors="coerce"
        ).fillna(0)

    )

    df["NetPenalties60"] = (
        df["NetPenalties"] / df["TOI"]
    ) * 60

    # =====================================================
    # NET XG
    # =====================================================

    df["NetxG"] = pd.to_numeric(
        df[NETXG_COL],
        errors="coerce"
    ).fillna(0)

    # =====================================================
    # CORSI
    # =====================================================

    if CORSI_COL:

        df["Corsi"] = pd.to_numeric(
            df[CORSI_COL],
            errors="coerce"
        ).fillna(0)

    else:

        df["Corsi"] = 0

    # =====================================================
    # CLEAN NAN
    # =====================================================

    df = df.replace(
        [np.inf, -np.inf],
        0
    )

    df = df.fillna(0)

    # =====================================================
    # STORE
    # =====================================================

    all_seasons = []

    seasons = sorted(
        df["Season"].unique()
    )

    # =====================================================
    # SINGLE SEASON ENGINE
    # =====================================================

    for season in seasons:

        season_df = df[
            df["Season"] == season
        ].copy()

        metrics = [

            "Goals60",
            "Assists60",
            "xG60",
            "SlotPasses60",

            "NetxG",
            "Takeaways60",
            "PuckLosses60",
            "NetPenalties60",
            "PuckBattlesWon60",

            "Corsi"

        ]

        for metric in metrics:

            season_df[f"{metric}_z"] = 0.0

        # =================================================
        # POSITION ADJUSTED Z-SCORES
        # =================================================

        for position in ["F", "D"]:

            mask = (
                season_df["Position"] == position
            )

            pos_df = season_df[mask]

            for metric in metrics:

                z = safe_zscore(
                    pos_df[metric]
                )

                season_df.loc[
                    mask,
                    f"{metric}_z"
                ] = z

        # =================================================
        # TEAM OFFENSE STRENGTH
        # =================================================

        league_gpg = (
            season_df["GPG"].mean()
        )

        season_df["Team_Off_Strength"] = (

            season_df["GPG"]

            /

            league_gpg

        )

        # =================================================
        # RAW OWS
        # =================================================

        season_df["Raw_OWS"] = (

            0.30 * season_df["Goals60_z"] +

            0.35 * season_df["Assists60_z"] +

            0.20 * season_df["xG60_z"] +

            0.15 * season_df["SlotPasses60_z"]

        )

        # =================================================
        # RAW DWS
        # =================================================

        season_df["Raw_DWS"] = (

            0.15 * season_df["NetxG_z"] +

            0.10 * season_df["Takeaways60_z"] -

            0.20 * season_df["PuckLosses60_z"] +

            0.10 * season_df["NetPenalties60_z"] +

            0.15 * season_df["PuckBattlesWon60_z"] +

            0.30 * season_df["Corsi_z"]

        )

        # =================================================
        # OWS
        # =====================================================

        season_df["OWS"] = (

            season_df["Raw_OWS"]

            -

            (
                (
                    season_df["Team_Off_Strength"] - 1
                ) * 0.50
            )

        )

        # =================================================
        # DWS
        # =====================================================

        season_df["DWS"] = (
            season_df["Raw_DWS"]
        )

        # =================================================
        # TOI STABILIZATION
        # =====================================================

        K = 400

        season_df["TOI_Factor"] = (

            season_df["TOI"]

            /

            (
                season_df["TOI"] + K
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

        # =================================================
        # FINAL WS
        # =====================================================

        season_df["WS"] = (

            season_df["OWS"]

            +

            season_df["DWS"]

        )

        # =================================================
        # PERCENTILES
        # =====================================================

        season_df["WS_percentile"] = (

            season_df["WS"]
            .rank(pct=True) * 100

        )

        all_seasons.append(
            season_df
        )

    # =====================================================
    # CONCAT
    # =====================================================

    final_df = pd.concat(
        all_seasons,
        ignore_index=True
    )

    return final_df


# =========================================================
# LOAD FINAL DATA
# =========================================================

final_df = load_data()

# =========================================================
# UI
# =========================================================

st.title("🏒 Winshare Multiseason")

c1, c2, c3 = st.columns(3)

with c1:

    season_filter = st.selectbox(
        "Season",
        sorted(final_df["Season"].unique())
    )

with c2:

    team_filter = st.selectbox(
        "Team",
        ["All"] +
        sorted(
            final_df[
                final_df["Season"] == season_filter
            ]["Team"].unique()
        )
    )

with c3:

    position_filter = st.selectbox(
        "Position",
        ["All", "F", "D"]
    )

# =========================================================
# FILTER
# =========================================================

filtered_df = final_df[
    final_df["Season"] == season_filter
]

if team_filter != "All":

    filtered_df = filtered_df[
        filtered_df["Team"] == team_filter
    ]

if position_filter != "All":

    filtered_df = filtered_df[
        filtered_df["Position"] == position_filter
    ]

# =========================================================
# TABLE
# =========================================================

st.subheader(
    f"Top Win Shares - {season_filter}"
)

table = (

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
    table,
    use_container_width=True,
    hide_index=True
)

# =====================================================
# PLAYER CAREER TREND
# =====================================================

st.divider()

st.header("Player Career Trend")

# =====================================================
# TEAM FILTER
# =====================================================

career_team = st.selectbox(
    "Choose Team",
    ["All"] + sorted(
        final_df["Team"].dropna().unique()
    )
)

# =====================================================
# FILTER PLAYERS BY TEAM
# =====================================================

if career_team == "All":

    players_list = sorted(
        final_df["Player"].dropna().unique()
    )

else:

    players_list = sorted(

        final_df[
            final_df["Team"] == career_team
        ]["Player"]

        .dropna()
        .unique()

    )

# =====================================================
# PLAYER SELECT
# =====================================================

selected_player = st.selectbox(
    "Choose Player",
    players_list
)

# =====================================================
# PLAYER DATA
# =====================================================

player_df = final_df[
    final_df["Player"] == selected_player
].copy()

player_df = player_df.sort_values(
    "Season"
)

# =====================================================
# CAREER TABLE
# =====================================================

st.subheader(f"{selected_player} Career")

st.dataframe(

    player_df[[
        "Season",
        "Team",
        "Position",
        "OWS",
        "DWS",
        "WS",
        "WS_percentile"
    ]],

    use_container_width=True,
    hide_index=True

)

# =====================================================
# WS GRAPH
# =====================================================

fig = px.line(

    player_df,

    x="Season",
    y="WS",

    markers=True,

    title=f"{selected_player} - Win Share Trend"

)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================================
# OWS VS DWS GRAPH
# =====================================================

trend_df = player_df.melt(

    id_vars=["Season"],

    value_vars=["OWS", "DWS"],

    var_name="Metric",
    value_name="Value"

)

fig2 = px.line(

    trend_df,

    x="Season",
    y="Value",
    color="Metric",

    markers=True,

    title=f"{selected_player} - OWS vs DWS"

)

st.plotly_chart(
    fig2,
    use_container_width=True
)
