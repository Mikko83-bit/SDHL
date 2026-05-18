# =========================================================
# WINSHARE MULTISEASON
# FIXED VERSION
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import zscore

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
        .str.replace("/", "_per_")
        .str.replace("%", "perc")
        .str.replace("-", "_")
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
    )

    return df


def safe_zscore(series):

    series = pd.to_numeric(
        series,
        errors="coerce"
    ).fillna(0)

    if series.std() == 0:
        return np.zeros(len(series))

    return zscore(series)


# =========================================================
# LOAD
# =========================================================

@st.cache_data
def load_data():

    # =====================================================
    # READ
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
        teams["Goal_for"] /
        teams["GP"]
    )

    teams["GAPG"] = (
        teams["Goal_agn"] /
        teams["GP"]
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

    def find_col(keyword):

        for c in df.columns:

            if keyword.lower() in c.lower():
                return c

        return None

    NETXG_COL = find_col("Net_xG")
    CORSI_COL = find_col("CORSI")
    FENWICK_COL = find_col("Fenwick")

    # =====================================================
    # CREATE METRICS
    # =====================================================

    df["Goals60"] = pd.to_numeric(
        df["Goals_per_60"],
        errors="coerce"
    ).fillna(0)

    df["Assists60"] = pd.to_numeric(
        df["Assists_per_60"],
        errors="coerce"
    ).fillna(0)

    df["xG60"] = pd.to_numeric(
        df["x_Expected_goals_per_60"],
        errors="coerce"
    ).fillna(0)

    df["Takeaways60"] = pd.to_numeric(
        df["Takeaways_per_60"],
        errors="coerce"
    ).fillna(0)

    df["PuckLosses60"] = pd.to_numeric(
        df["Puck_losses_per_60"],
        errors="coerce"
    ).fillna(0)

    df["NetPenalties60"] = (

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

    df["SlotPasses"] = pd.to_numeric(
        df["Passes_to_the_slot"],
        errors="coerce"
    ).fillna(0)

    df["PuckBattlesWon"] = pd.to_numeric(
        df["Puck_battles_won"],
        errors="coerce"
    ).fillna(0)

    df["NetxG"] = pd.to_numeric(
        df[NETXG_COL],
        errors="coerce"
    ).fillna(0)

    # =====================================================
    # POSSESSION
    # =====================================================

    if CORSI_COL:
        df["Corsi"] = pd.to_numeric(
            df[CORSI_COL],
            errors="coerce"
        ).fillna(0)
    else:
        df["Corsi"] = 0

    if FENWICK_COL:
        df["Fenwick"] = pd.to_numeric(
            df[FENWICK_COL],
            errors="coerce"
        ).fillna(0)
    else:
        df["Fenwick"] = 0

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

        # =================================================
        # Z-SCORE METRICS
        # =================================================

        metrics = [

            "Goals60",
            "Assists60",
            "xG60",
            "SlotPasses",

            "NetxG",
            "Takeaways60",
            "PuckLosses60",
            "NetPenalties60",
            "PuckBattlesWon",

            "Corsi",
            "Fenwick"

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
        # TEAM OFFENSE ADJUSTMENT
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

            0.15 * season_df["SlotPasses_z"]

        )

        # =================================================
        # FIXED RAW DWS
        # IMPORTANT:
        # POSSESSION NOW INCLUDED
        # =================================================

        season_df["Raw_DWS"] = (

            0.15 * season_df["NetxG_z"] +

            0.10 * season_df["Takeaways60_z"] -

            0.20 * season_df["PuckLosses60_z"] +

            0.10 * season_df["NetPenalties60_z"] +

            0.15 * season_df["PuckBattlesWon_z"] +

            0.30 * season_df["Corsi_z"]

        )

        # =================================================
        # OWS
        # =================================================

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
        # =================================================

        season_df["DWS"] = (
            season_df["Raw_DWS"]
        )

        # =================================================
        # TOI STABILIZATION
        # =================================================

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

        # =================================================
        # FINAL WS
        # =================================================

        season_df["WS"] = (

            season_df["OWS"]

            +

            season_df["DWS"]

        )

        # =================================================
        # PERCENTILES
        # =================================================

        season_df["WS_percentile"] = (

            season_df["WS"]
            .rank(pct=True) * 100

        )

        # =================================================
        # STORE
        # =================================================

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
# LOAD
# =========================================================

df = load_data()

# =========================================================
# FILTERS
# =========================================================

st.title("🏒 Winshare Multiseason")

c1, c2, c3 = st.columns(3)

with c1:

    season_filter = st.selectbox(
        "Season",
        sorted(df["Season"].unique())
    )

with c2:

    team_filter = st.selectbox(
        "Team",
        ["All"] +
        sorted(
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

# =========================================================
# FILTER DATA
# =========================================================

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

# =========================================================
# TABLE
# =========================================================

st.subheader(
    f"Top Win Shares - Season {season_filter}"
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
