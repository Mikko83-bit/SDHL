import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import zscore

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="SDHL Player Profiles - Multiseason",
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
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
        .str.replace("-", "_")
    )
    return df

def safe_zscore(series):
    if series.std() == 0:
        return np.zeros(len(series))
    return zscore(series)

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    # READ EXCEL
    players = pd.read_excel(FILE, sheet_name="Players")
    teams = pd.read_excel(FILE, sheet_name="Teams")

    # CLEAN COLUMNS
    players = clean_columns(players)
    teams = clean_columns(teams)

    # CLEAN STRINGS
    players["Season"] = players["Season"].astype(str).str.strip()
    teams["Season"] = teams["Season"].astype(str).str.strip()
    players["Team"] = players["Team"].astype(str).str.strip()
    teams["Team"] = teams["Team"].astype(str).str.strip()

    # TEAM STATS
    teams["GPG"] = teams["Goal_for"] / teams["GP"]
    teams["GAPG"] = teams["Goal_agn"] / teams["GP"]

    # MERGE BY SEASON + TEAM
    df = players.merge(teams, on=["Season", "Team"], how="left")

    # FIX PLAYER POSITIONS (Alkuperäinen fiksi)
    df.loc[df["Player"] == "Elisa Holopainen", "Position"] = "F"

    # RENAME IMPORTANT COLUMNS
    rename_map = {
        "Goals_per_60": "Goals60",
        "Assists_per_60": "Assists60",
        "xG_per_60": "xG60",
        "Takeaways_per_60": "Takeaways60",
        "Puck_losses_per_60": "PuckLosses60",
        "Net_penalties_per_60": "NetPenalties60",
        "Passes_to_the_slot": "SlotPasses",
        "Puck_battles_won": "PuckBattlesWon"
    }
    df = df.rename(columns=rename_map)

    # FIND NET XG COLUMN
    netxg_candidates = [c for c in df.columns if "Net" in c and "xG" in c]
    if netxg_candidates:
        df["NetxG"] = df[netxg_candidates[0]]
    else:
        df["NetxG"] = 0.0

    # FILL NaN VALUES
    numeric_cols = df.select_dtypes(include=np.number).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)

    # METRICS FOR Z-SCORES
    metrics = [
        "Goals60", "Assists60", "xG60", "SlotPasses",
        "NetxG", "Takeaways60", "PuckLosses60", "NetPenalties60", "PuckBattlesWon"
    ]

    all_seasons = []
    seasons = sorted(df["Season"].unique())

    # SINGLE SEASON ENGINE (Kausi kerrallaan, mutta alkuperäinen logiikka)
    for season in seasons:
        season_df = df[df["Season"] == season].copy()
        
        # Eristetään kauden joukkueet liigan keskiarvoja varten
        season_teams = teams[teams["Season"] == season]

        # CREATE EMPTY Z-SCORE COLUMNS
        for metric in metrics:
            season_df[f"{metric}_z"] = 0.0

        # POSITION-ADJUSTED Z-SCORES
        for position in ["F", "D"]:
            pos_mask = (season_df["Position"] == position)
            
            for metric in metrics:
                if metric in season_df.columns:
                    values = season_df.loc[pos_mask, metric]
                    z_values = safe_zscore(values)
                    season_df.loc[pos_mask, f"{metric}_z"] = z_values

        # LEAGUE AVERAGES (Alkuperäinen logiikka käytti teams-taulukkoa)
        league_gpg = season_teams["GPG"].mean()
        league_gapg = season_teams["GAPG"].mean()

        # TEAM ADJUSTMENTS
        season_df["Team_Off_Strength"] = season_df["GPG"] / league_gpg
        season_df["Team_Def_Strength"] = league_gapg / season_df["GAPG"]

        # RAW OFFENSIVE WIN SHARES
        season_df["Raw_OWS"] = (
            0.30 * season_df["Goals60_z"] +
            0.35 * season_df["Assists60_z"] +
            0.20 * season_df["xG60_z"] +
            0.15 * season_df["SlotPasses_z"]
        )

        # RAW DEFENSIVE WIN SHARES
        season_df["Raw_DWS"] = (
            0.40 * season_df["NetxG_z"] +
            0.20 * season_df["Takeaways60_z"] -
            0.20 * season_df["PuckLosses60_z"] +
            0.10 * season_df["NetPenalties60_z"] +
            0.10 * season_df["PuckBattlesWon_z"]
        )

        # TEAM-ADJUSTED WIN SHARES (Täysin alkuperäinen logiikka molemmissa)
        season_df["OWS"] = season_df["Raw_OWS"] - ((season_df["Team_Off_Strength"] - 1) * 0.50)
        season_df["DWS"] = season_df["Raw_DWS"] - ((season_df["Team_Def_Strength"] - 1) * 0.50)

        # TOI STABILIZATION
        K = 400
        season_df["TOI_Factor"] = season_df["Time_on_ice"] / (season_df["Time_on_ice"] + K)

        # APPLY STABILIZATION
        season_df["OWS"] = season_df["OWS"] * season_df["TOI_Factor"]
        season_df["DWS"] = season_df["DWS"] * season_df["TOI_Factor"]

        # TOTAL WIN SHARES
        season_df["WS"] = season_df["OWS"] + season_df["DWS"]

        # PERCENTILES (Kauden sisäiset)
        season_df["OWS_percentile"] = season_df["OWS"].rank(pct=True) * 100
        season_df["DWS_percentile"] = season_df["DWS"].rank(pct=True) * 100
        season_df["WS_percentile"] = season_df["WS"].rank(pct=True) * 100

        # RANKINGS (Kauden sisäiset)
        season_df["OWS_rank"] = season_df["OWS"].rank(ascending=False, method="min").astype(int)
        season_df["DWS_rank"] = season_df["DWS"].rank(ascending=False, method="min").astype(int)
        season_df["WS_rank"] = season_df["WS"].rank(ascending=False, method="min").astype(int)

        all_seasons.append(season_df)

    return pd.concat(all_seasons, ignore_index=True)


# =========================================================
# RUN DATA ENGINE
# =========================================================
df = load_data()

# =========================================================
# DASHBOARD UI (Alkuperäinen tyyli + Kausivalinta)
# =========================================================
st.title("🏒 SDHL Player Profiles - Multiseason Engine")

st.markdown("""
This dashboard includes the **fully original mathematical logic** calculated safely season-by-season:
- Position-adjusted & Team-adjusted Win Shares (both Offensive & Defensive)
- TOI stabilization ($K=400$) and Season-specific League Percentiles/Rankings.
""")

# FILTERS
filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

with filter_col1:
    season_filter = st.selectbox("Select Season", sorted(df["Season"].unique(), reverse=True))

# Rajataan data valitulle kaudelle ennen muiden suodattimien täyttöä
season_data = df[df["Season"] == season_filter]

with filter_col2:
    team_filter = st.selectbox("Select Team", ["All"] + sorted(season_data["Team"].unique().tolist()))

with filter_col3:
    position_filter = st.selectbox("Select Position", ["All", "F", "D"])

with filter_col4:
    min_games = st.slider("Minimum Games Played", 1, int(season_data["Games_played"].max()), 10)

# APPLY FILTERS
filtered_df = season_data.copy()

if team_filter != "All":
    filtered_df = filtered_df[filtered_df["Team"] == team_filter]

if position_filter != "All":
    filtered_df = filtered_df[filtered_df["Position"] == position_filter]

filtered_df = filtered_df[filtered_df["Games_played"] >= min_games]

# PLAYER SELECTOR
if not filtered_df.empty:
    player = st.selectbox("Select Player", sorted(filtered_df["Player"].unique()))
    player_df = filtered_df[filtered_df["Player"] == player].iloc[0]

    # PLAYER HEADER
    st.subheader(f"{player_df['Player']} | {player_df['Team']} | {player_df['Position']} ({player_df['Season']})")

    # MAIN METRICS
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("OWS", f"{round(player_df['OWS'],2)} (#{player_df['OWS_rank']})")
    with col2:
        st.metric("DWS", f"{round(player_df['DWS'],2)} (#{player_df['DWS_rank']})")
    with col3:
        st.metric("WS", f"{round(player_df['WS'],2)} (#{player_df['WS_rank']})")

    # PERCENTILES
    st.subheader("Season Percentiles")
    p1, p2, p3 = st.columns(3)
    with p1:
        st.metric("OWS Percentile", f"{round(player_df['OWS_percentile'])}%")
    with p2:
        st.metric("DWS Percentile", f"{round(player_df['DWS_percentile'])}%")
    with p3:
        st.metric("WS Percentile", f"{round(player_df['WS_percentile'])}%")

    # PLAYER INFORMATION
    st.subheader("Player Information")
    info1, info2, info3, info4 = st.columns(4)
    with info1:
        st.write(f"**Games Played:** {player_df['Games_played']}")
    with info2:
        st.write(f"**Time on Ice:** {round(player_df['Time_on_ice'],1)}")
    with info3:
        st.write(f"**Points:** {player_df['Points']}")
    with info4:
        st.write(f"**Net xG:** {round(player_df['NetxG'],2)}")

    # ADDITIONAL STATISTICS
    st.subheader("Additional Statistics")
    stats_df = pd.DataFrame({
        "Statistic": ["Goals/60", "Assists/60", "xG/60", "Takeaways/60", "Puck Losses/60", "Net Penalties/60", "Puck Battles Won", "Slot Passes"],
        "Value": [
            round(player_df["Goals60"], 2), round(player_df["Assists60"], 2), round(player_df["xG60"], 2),
            round(player_df["Takeaways60"], 2), round(player_df["PuckLosses60"], 2), round(player_df["NetPenalties60"], 2),
            round(player_df["PuckBattlesWon"], 2), round(player_df["SlotPasses"], 2)
        ]
    })
    st.dataframe(stats_df, use_container_width=True, hide_index=True)

else:
    st.warning("No players found matching the selected filter criteria.")

# TOP 10 WIN SHARES FOR THE SELECTED SEASON
st.subheader(f"Top 10 Win Shares - Season {season_filter}")
top_ws = (
    filtered_df[["Player", "Team", "Position", "OWS", "DWS", "WS"]]
    .sort_values("WS", ascending=False)
    .head(10)
)
st.dataframe(top_ws, use_container_width=True, hide_index=True)
