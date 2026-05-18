import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import zscore

# =====================================================
# PAGE
# =====================================================

st.set_page_config(
    page_title="Winshare Multiseason",
    page_icon="🏒",
    layout="wide"
)

# =====================================================
# FILE
# =====================================================

FILE = "Sdhl_2023_2026.xlsx"

# =====================================================
# HELPERS
# =====================================================

def clean_columns(df):

    df.columns = (
        df.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("/", "_per_")
        .str.replace("%", "perc")
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
        .str.replace("-", "_")
    )

    return df


def safe_zscore(series):

    if series.std() == 0:
        return np.zeros(len(series))

    return zscore(series)


# =====================================================
# LOAD DATA
# =====================================================

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
    # TEAM DATA
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
    # IMPORTANT:
    # SEASON + TEAM
    # =====================================================

    df = players.merge(
        teams,
        on=["Season", "Team"],
        how="left"
    )

    # =====================================================
    # RENAME COLUMNS
    # =====================================================

    rename_map = {

        "Goals_per_60": "Goals60",
        "Assists_per_60": "Assists60",
        "xG_per_60": "xG60",

        "Takeaways_per_60": "Takeaways60",
        "Puck_losses_per_60": "PuckLosses60",
        "Net_penalties_per_60": "NetPenalties60",

        "Scoring_chances": "ScoringChances",
        "Passes_to_the_slot": "SlotPasses",

        "Puck_battles_won": "PuckBattlesWon"

    }

    df = df.rename(columns=rename_map)

    # =====================================================
    # FIND NET XG COLUMN
    # =====================================================

    netxg_candidates = [

        c for c in df.columns

        if "Net" in c and "xG" in c

    ]

    NETXG_COL = netxg_candidates[0]

    df["NetxG"] = df[NETXG_COL]

    # =====================================================
    # NUMERIC
    # =====================================================

    numeric_cols = df.select_dtypes(
        include=np.number
    ).columns

    df[numeric_cols] = (
        df[numeric_cols]
        .fillna(0)
    )

    # =====================================================
    # METRICS
    # =====================================================

    metrics = [

        # offense
        "Goals60",
        "Assists60",
        "xG60",
        "SlotPasses",

        # defense
        "NetxG",
        "Takeaways60",
        "PuckLosses60",
        "NetPenalties60",
        "PuckBattlesWon"

    ]

    # =====================================================
    # STORE RESULTS
    # =====================================================

    all_seasons = []

    # =====================================================
    # SINGLE SEASON ENGINE
    # IMPORTANT:
    # SAME ENGINE AS ORIGINAL MODEL
    # =====================================================

    seasons = sorted(
        df["Season"].unique()
    )

    for season in seasons:

        # =====================================================
        # SINGLE SEASON ONLY
        # =====================================================

        season_df = df[
            df["Season"] == season
        ].copy()

        # =====================================================
        # POSITION ADJUSTED Z-SCORES
        # =====================================================

        for metric in metrics:

            season_df[f"{metric}_z"] = 0.0

        for position in ["F", "D"]:

            pos_mask = (
                season_df["Position"] == position
            )

            pos_df = season_df[pos_mask]

            for metric in metrics:

                if metric not in season_df.columns:
                    continue

                z_values = safe_zscore(
                    pos_df[metric]
                )

                season_df.loc[
                    pos_mask,
                    f"{metric}_z"
                ] = z_values

        # =====================================================
        # LEAGUE AVERAGES
        # =====================================================

        league_gpg = (
            season_df["GPG"].mean()
        )

        league_gapg = (
            season_df["GAPG"].mean()
        )

        # =====================================================
        # TEAM STRENGTH
        # =====================================================

        season_df["Team_Off_Strength"] = (

            season_df["GPG"] /
            league_gpg

        )

        season_df["Team_Def_Strength"] = (

            league_gapg /
            season_df["GAPG"]

        )

        # =====================================================
        # RAW OWS
        # =====================================================

        season_df["Raw_OWS"] = (

            0.30 * season_df["Goals60_z"] +

            0.35 * season_df["Assists60_z"] +

            0.20 * season_df["xG60_z"] +

            0.15 * season_df["SlotPasses_z"]

        )

        # =====================================================
        # RAW DWS
        # IMPORTANT:
        # KEEP ORIGINAL MODEL
        # =====================================================

        season_df["Raw_DWS"] = (

            0.40 * season_df["NetxG_z"] +

            0.20 * season_df["Takeaways60_z"] -

            0.20 * season_df["PuckLosses60_z"] +

            0.10 * season_df["NetPenalties60_z"] +

            0.10 * season_df["PuckBattlesWon_z"]

        )

        # =====================================================
        # TEAM ADJUSTMENT
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

        season_df["DWS"] = (

            season_df["Raw_DWS"]

            -

            (
                (
                    season_df["Team_Def_Strength"] - 1
                ) * 0.50
            )

        )

        # =====================================================
        # TOI STABILIZATION
        # =====================================================

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

        # =====================================================
        # TOTAL WS
        # =====================================================

        season_df["WS"] = (

            season_df["OWS"] +

            season_df["DWS"]

        )

        # =====================================================
        # PERCENTILES
        # =====================================================

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

        # =====================================================
        # RANKS
        # =====================================================

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

        # =====================================================
        # STORE
        # =====================================================

        all_seasons.append(
            season_df
        )

    # =====================================================
    # CONCAT ALL SEASONS
    # =====================================================

    final_df = pd.concat(
        all_seasons,
        ignore_index=True
    )

    return final_df


# =====================================================
# LOAD
# =====================================================

df = load_data()

# =====================================================
# TITLE
# =====================================================

st.title("🏒 Winshare Multiseason")

# =====================================================
# FILTERS
# =====================================================

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

# =====================================================
# FILTER
# =====================================================

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

# =====================================================
# TOP TABLE
# =====================================================

st.subheader("Top Win Shares")

table_df = (

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
    table_df,
    use_container_width=True,
    hide_index=True
)
