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

        "Goals_per_60": "Goals60",
        "Assists_per_60": "Assists60",
        "xG_per_60": "xG60",

        "Takeaways_per_60": "Takeaways60",
        "Puck_losses_per_60": "PuckLosses60",

        "Passes_to_the_slot": "SlotPasses",

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
        "PuckLosses60"
    ]

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
    # POSITION + SEASON ADJUSTED Z-SCORES
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

        # CLEAN

        df[f"{metric}_z"] = (

            df[f"{metric}_z"]

            .replace([np.inf, -np.inf], 0)

            .fillna(0)

        )

        # ---------------------------------------------------
        # CLIP OUTLIERS
        # ---------------------------------------------------

        df[f"{metric}_z"] = (
            df[f"{metric}_z"]
            .clip(-2.5, 2.5)
        )

    # ---------------------------------------------------
    # RAW OWS
    # ---------------------------------------------------

    df["Raw_OWS"] = (

        0.35 * df.get("Goals60_z", 0) +
        0.40 * df.get("Assists60_z", 0) +
        0.20 * df.get("xG60_z", 0) +
        0.05 * df.get("SlotPasses_z", 0)

    )

    # ---------------------------------------------------
    # RAW DWS
    # ---------------------------------------------------

    df["Raw_DWS"] = (

        0.60 * df.get("NetxG_z", 0) +
        0.20 * df.get("Takeaways60_z", 0) -
        0.20 * df.get("PuckLosses60_z", 0)

    )

    # ---------------------------------------------------
    # SHIFT TO POSITIVE SCALE
    # ---------------------------------------------------

    df["OWS"] = (
        df["Raw_OWS"] + 2
    )

    df["DWS"] = (
        df["Raw_DWS"] + 2
    )

    # ---------------------------------------------------
    # SCALE
    # ---------------------------------------------------

    df["OWS"] = (
        df["OWS"] * 0.70
    )

    df["DWS"] = (
        df["DWS"] * 0.30
    )

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
        f"{player_df['OWS']:.2f}"
    )

with m2:

    st.metric(
        "DWS",
        f"{player_df['DWS']:.2f}"
    )

with m3:

    st.metric(
        "WS",
        f"{player_df['WS']:.2f} "
        f"(#{int(player_df['WS_rank'])})"
    )

# ---------------------------------------------------
# PERCENTILES
# ---------------------------------------------------

p1, p2 = st.columns(2)

with p1:

    st.metric(
        "WS Percentile",
        f"{player_df['WS_percentile']:.1f}%"
    )

with p2:

    st.metric(
        "Games Played",
        int(player_df["Games_played"])
        if "Games_played" in player_df
        else "-"
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
    title="Career Trend"
)

st.plotly_chart(
    fig,
    use_container_width=True
)
