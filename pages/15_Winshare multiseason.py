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
    )

    players.columns = players.columns.str.replace("__", "_")
    teams.columns = teams.columns.str.replace("__", "_")

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
        on=["Season", "Team"]
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
    # FILL NaN
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

    all_metrics = (
        offensive_metrics +
        defensive_metrics
    )

    # ---------------------------------------------------
    # CREATE Z-COLUMNS
    # ---------------------------------------------------

    for metric in all_metrics:

        df[f"{metric}_z"] = 0.0

    # ---------------------------------------------------
    # POSITION + SEASON ADJUSTED Z-SCORES
    # ---------------------------------------------------

    for season in df["Season"].unique():

        for position in ["F", "D"]:

            mask = (

                (df["Season"] == season) &
                (df["Position"] == position)

            )

            for metric in all_metrics:

                if metric in df.columns:

                    values = df.loc[
                        mask,
                        metric
                    ]

                    if values.std() == 0:

                        df.loc[
                            mask,
                            f"{metric}_z"
                        ] = 0.0

                    else:

                        z_values = zscore(values)

                        z_values = np.nan_to_num(
                            z_values
                        )

                        df.loc[
                            mask,
                            f"{metric}_z"
                        ] = z_values

    # ---------------------------------------------------
    # RAW OFFENSIVE IMPACT
    # ---------------------------------------------------

    df["Raw_OWS"] = (

        0.35 * df["Goals60_z"] +
        0.35 * df["Assists60_z"] +
        0.20 * df["xG60_z"] +
        0.10 * df["SlotPasses_z"]

    )

    # ---------------------------------------------------
    # RAW DEFENSIVE IMPACT
    # ---------------------------------------------------

    df["Raw_DWS"] = (

        0.50 * df["NetxG_z"] +
        0.15 * df["Takeaways60_z"] -
        0.15 * df["PuckLosses60_z"] +
        0.10 * df["NetPenalties60_z"] +
        0.10 * df["PuckBattlesWon_z"]

    )

    # ---------------------------------------------------
    # TEAM CONTEXT ADJUSTMENT
    # ---------------------------------------------------

    df["Adj_OWS"] = 0.0
    df["Adj_DWS"] = 0.0

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

        # TEAM STRENGTH

        team_off_strength = (

            df.loc[
                season_mask,
                "GPG"
            ] / league_gpg

        )

        team_def_strength = (

            league_gapg /
            df.loc[
                season_mask,
                "GAPG"
            ]

        )

        # CONTEXT ADJUSTED

        df.loc[
            season_mask,
            "Adj_OWS"
        ] = (

            df.loc[
                season_mask,
                "Raw_OWS"
            ]

            *

            (
                1 /
                (
                    team_off_strength ** 0.35
                )
            )

        )

        df.loc[
            season_mask,
            "Adj_DWS"
        ] = (

            df.loc[
                season_mask,
                "Raw_DWS"
            ]

            *

            (
                1 /
                (
                    team_def_strength ** 0.25
                )
            )

        )

    # ---------------------------------------------------
    # TOI STABILIZATION
    # ---------------------------------------------------

    K = 250

    df["TOI_Factor"] = (

        df["Time_on_ice"]

        /

        (
            df["Time_on_ice"] + K
        )

    )

    df["Adj_OWS"] = (
        df["Adj_OWS"] *
        df["TOI_Factor"]
    )

    df["Adj_DWS"] = (
        df["Adj_DWS"] *
        df["TOI_Factor"]
    )

    # ---------------------------------------------------
    # TOTAL IMPACT
    # ---------------------------------------------------

    df["Impact"] = (

        df["Adj_OWS"] +
        df["Adj_DWS"]

    )

    # ---------------------------------------------------
    # CONVERT IMPACT -> WIN SHARES
    # ---------------------------------------------------

    df["OWS"] = 0.0
    df["DWS"] = 0.0
    df["WS"] = 0.0

    # ---------------------------------------------------
    # CALCULATE PER SEASON + TEAM
    # ---------------------------------------------------

    for season in df["Season"].unique():

        season_df = df[
            df["Season"] == season
        ]

        for team in season_df["Team"].unique():

            team_mask = (

                (df["Season"] == season) &
                (df["Team"] == team)

            )

            team_players = df.loc[
                team_mask
            ]

            # TEAM WINS

            team_wins = team_players[
                "Wins"
            ].iloc[0]

            # EXPONENTIAL SHARE SYSTEM

            offensive_exp = np.exp(
                team_players["Adj_OWS"]
            )

            defensive_exp = np.exp(
                team_players["Adj_DWS"]
            )

            offensive_total = offensive_exp.sum()
            defensive_total = defensive_exp.sum()

            # OWS

            df.loc[
                team_mask,
                "OWS"
            ] = (

                offensive_exp /
                offensive_total

            ) * (

                team_wins * 0.55

            )

            # DWS

            df.loc[
                team_mask,
                "DWS"
            ] = (

                defensive_exp /
                defensive_total

            ) * (

                team_wins * 0.45

            )

    # ---------------------------------------------------
    # TOTAL WS
    # ---------------------------------------------------

    df["WS"] = (
        df["OWS"] +
        df["DWS"]
    )

    # ---------------------------------------------------
    # PERCENTILES
    # ---------------------------------------------------

    df["OWS_percentile"] = 0.0
    df["DWS_percentile"] = 0.0
    df["WS_percentile"] = 0.0

    # ---------------------------------------------------
    # RANKINGS
    # ---------------------------------------------------

    df["OWS_rank"] = 0
    df["DWS_rank"] = 0
    df["WS_rank"] = 0

    # ---------------------------------------------------
    # CALCULATE PER SEASON
    # ---------------------------------------------------

    for season in df["Season"].unique():

        season_mask = (
            df["Season"] == season
        )

        # PERCENTILES

        df.loc[
            season_mask,
            "OWS_percentile"
        ] = (

            df.loc[
                season_mask,
                "OWS"
            ]
            .rank(pct=True) * 100

        )

        df.loc[
            season_mask,
            "DWS_percentile"
        ] = (

            df.loc[
                season_mask,
                "DWS"
            ]
            .rank(pct=True) * 100

        )

        df.loc[
            season_mask,
            "WS_percentile"
        ] = (

            df.loc[
                season_mask,
                "WS"
            ]
            .rank(pct=True) * 100

        )

        # RANKS

        df.loc[
            season_mask,
            "OWS_rank"
        ] = (

            df.loc[
                season_mask,
                "OWS"
            ]
            .rank(
                ascending=False,
                method="min"
            )

        )

        df.loc[
            season_mask,
            "DWS_rank"
        ] = (

            df.loc[
                season_mask,
                "DWS"
            ]
            .rank(
                ascending=False,
                method="min"
            )

        )

        df.loc[
            season_mask,
            "WS_rank"
        ] = (

            df.loc[
                season_mask,
                "WS"
            ]
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

st.markdown("""

This model includes:

- Position-adjusted Z-scores
- Offensive and Defensive Win Shares
- Team context adjustments
- TOI stabilization
- Win distribution by team success
- Multi-season player tracking

""")

# ---------------------------------------------------
# FILTERS
# ---------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

# SEASON

with col1:

    season_filter = st.selectbox(
        "Season",
        sorted(df["Season"].unique())
    )

# TEAM

with col2:

    available_teams = sorted(

        df[
            df["Season"] == season_filter
        ]["Team"].unique()

    )

    team_filter = st.selectbox(
        "Team",
        ["All"] + available_teams
    )

# POSITION

with col3:

    position_filter = st.selectbox(
        "Position",
        ["All", "F", "D"]
    )

# MIN GAMES

with col4:

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
    f"{player_df['Season']} | "
    f"{player_df['Position']}"

)

# ---------------------------------------------------
# MAIN METRICS
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

st.subheader("Top 20 Win Shares")

top_ws = (

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

    .head(20)

)

st.dataframe(
    top_ws,
    use_container_width=True,
    hide_index=True
)
