import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import zscore
import plotly.express as px

# -------------------------------------------------------
# PAGE
# -------------------------------------------------------

st.set_page_config(
    page_title="Winshare Multiseason",
    page_icon="🏒",
    layout="wide"
)

# -------------------------------------------------------
# FILE
# -------------------------------------------------------

FILE = "Sdhl 2023-2026_players_teams.xlsx"

# -------------------------------------------------------
# LOAD DATA
# -------------------------------------------------------

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

    def clean_columns(df):

        df.columns = (

            df.columns
            .str.strip()
            .str.replace(" ", "_")
            .str.replace("/", "_")
            .str.replace("%", "perc")
            .str.replace("(", "", regex=False)
            .str.replace(")", "", regex=False)

        )

        return df

    players = clean_columns(players)
    teams = clean_columns(teams)

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

    teams["Goals_For_Per_Game"] = (
        teams["Goal_for"] / teams["GP"]
    )

    teams["Goals_Against_Per_Game"] = (
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
    # TOI
    # ---------------------------------------------------

    df["Time_on_ice"] = (
        df["Time_on_ice"]
        .replace(0, np.nan)
    )

    # ---------------------------------------------------
    # FIND NET XG COLUMN
    # ---------------------------------------------------

    netxg_col = [

        col for col in df.columns

        if "Net_xG" in col

    ][0]

    df["NetxG"] = df[netxg_col]

    # ---------------------------------------------------
    # PER60
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

    df["SlotPasses"] = (
        df["Passes_to_the_slot"]
    )

    df["PuckBattlesWon"] = (
        df["Puck_battles_won"]
    )

    # ---------------------------------------------------
    # CLEAN NAN
    # ---------------------------------------------------

    df = df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    df = df.fillna(0)

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
    # STORE RESULTS
    # ---------------------------------------------------

    all_seasons = []

    # ---------------------------------------------------
    # SINGLE SEASON ENGINE
    # ---------------------------------------------------

    seasons = sorted(
        df["Season"].unique()
    )

    for season in seasons:

        season_df = df[
            df["Season"] == season
        ].copy()

        # ---------------------------------------------------
        # POSITION ADJUSTED Z-SCORES
        # ---------------------------------------------------

        for metric in offensive_metrics + defensive_metrics:

            season_df[f"{metric}_z"] = 0.0

            for position in ["F", "D"]:

                mask = (
                    season_df["Position"] == position
                )

                values = season_df.loc[
                    mask,
                    metric
                ]

                if len(values) > 1:

                    z_values = zscore(values)

                    z_values = np.nan_to_num(
                        z_values
                    )

                    season_df.loc[
                        mask,
                        f"{metric}_z"
                    ] = z_values

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

        league_gf = (
            season_df["Goals_For_Per_Game"]
            .mean()
        )

        league_ga = (
            season_df["Goals_Against_Per_Game"]
            .mean()
        )

        season_df["Team_Off_Strength"] = (

            season_df["Goals_For_Per_Game"]

            /

            league_gf

        )

        season_df["Team_Def_Strength"] = (

            league_ga

            /

            season_df["Goals_Against_Per_Game"]

        )

        season_df["OWS"] = (

            season_df["Raw_OWS"]

            -

            (
                (
                    season_df["Team_Off_Strength"] - 1
                )

                * 0.50
            )

        )

        season_df["DWS"] = (

            season_df["Raw_DWS"]

            -

            (
                (
                    season_df["Team_Def_Strength"] - 1
                )

                * 0.50
            )

        )

        # ---------------------------------------------------
        # TOI STABILIZATION
        # ---------------------------------------------------

        season_df["TOI_Factor"] = (

            season_df["Time_on_ice"]

            /

            (
                season_df["Time_on_ice"] + 400
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

            season_df["OWS"]

            +

            season_df["DWS"]

        )

        # ---------------------------------------------------
        # PERCENTILE
        # ---------------------------------------------------

        season_df["WS_percentile"] = (

            season_df["WS"]
            .rank(pct=True)

            * 100

        )

        # ---------------------------------------------------
        # RANK
        # ---------------------------------------------------

        season_df["WS_rank"] = (

            season_df["WS"]
            .rank(
                ascending=False,
                method="min"
            )

        ).astype(int)

        # ---------------------------------------------------
        # STORE
        # ---------------------------------------------------

        all_seasons.append(
            season_df
        )

    # ---------------------------------------------------
    # FINAL DF
    # ---------------------------------------------------

    final_df = pd.concat(
        all_seasons,
        ignore_index=True
    )

    return final_df

# -------------------------------------------------------
# LOAD
# -------------------------------------------------------

df = load_data()

# -------------------------------------------------------
# FILTERS
# -------------------------------------------------------

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

# -------------------------------------------------------
# FILTER DF
# -------------------------------------------------------

filtered_df = df[
    df["Season"] == season_filter
]

if team_filter != "All":

    filtered_df = filtered_df[
        filtered_df["Team"] == team_filter
    ]

if position_filter != "All":

    filtered_df = filtered_df[
        filtered_df["Position"] == position_filter
    ]

# -------------------------------------------------------
# TOP TABLE
# -------------------------------------------------------

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

# -------------------------------------------------------
# PLAYER SELECT
# -------------------------------------------------------

player = st.selectbox(
    "Select Player",
    sorted(filtered_df["Player"].unique())
)

player_df = filtered_df[
    filtered_df["Player"] == player
].iloc[0]

# -------------------------------------------------------
# PLAYER HEADER
# -------------------------------------------------------

st.subheader(

    f"{player_df['Player']} | "

    f"{player_df['Team']} | "

    f"{player_df['Season']} | "

    f"{player_df['Position']}"

)

# -------------------------------------------------------
# METRICS
# -------------------------------------------------------

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

# -------------------------------------------------------
# PERCENTILES
# -------------------------------------------------------

p1, p2, p3 = st.columns(3)

with p1:

    st.metric(
        "OWS Percentile",
        f"{round(filtered_df['OWS'].rank(pct=True)[player_df.name]*100,1)}%"
    )

with p2:

    st.metric(
        "DWS Percentile",
        f"{round(filtered_df['DWS'].rank(pct=True)[player_df.name]*100,1)}%"
    )

with p3:

    st.metric(
        "WS Percentile",
        f"{round(player_df['WS_percentile'],1)}%"
    )

# -------------------------------------------------------
# PLAYER INFO
# -------------------------------------------------------

st.subheader("Player Information")

i1, i2, i3, i4 = st.columns(4)

with i1:
    st.write(f"Games Played: {player_df['played']}")

with i2:
    st.write(f"Time on Ice: {round(player_df['Time_on_ice'],1)}")

with i3:
    st.write(f"Points: {player_df['Points']}")

with i4:
    st.write(f"Net xG: {round(player_df['NetxG'],1)}")

# -------------------------------------------------------
# ADDITIONAL STATS
# -------------------------------------------------------

st.subheader("Additional Statistics")

extra_stats = pd.DataFrame({

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
        round(player_df["PuckBattlesWon"], 0),
        round(player_df["SlotPasses"], 0)

    ]

})

st.dataframe(
    extra_stats,
    use_container_width=True,
    hide_index=True
)

# -------------------------------------------------------
# CAREER TREND
# -------------------------------------------------------

career_df = (

    df[
        df["Player"] == player
    ]

    .sort_values("Season")

)

if len(career_df) > 1:

    st.subheader("Career Trend")

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
