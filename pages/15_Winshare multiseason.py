import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import zscore

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="SDHL Player Profiles - Multiseason Engine",
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
        .str.replace(",", "")
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

    # FIX PLAYER POSITIONS
    df.loc[df["Player"] == "Elisa Holopainen", "Position"] = "F"

    # =====================================================
    # LASKETAAN LUVUT JA PER 60 -METRIIKAT SUORAAN DATASTA
    # =====================================================
    
    # 1. NetxG haku (Otetaan Excelin sarake "Net_xG_xG_player_on_0_opp._team's_xG")
    netxg_cols = [c for c in df.columns if "Net_xG" in c]
    if netxg_cols:
        df["NetxG"] = df[netxg_cols[0]]
    else:
        df["NetxG"] = 0.0

    # 2. Jäähytasapaino (Koska "Net_penalties" puuttuu, lasketaan: hankitut jäähyt - otetut jäähyt)
    if "Penalties_drawn" in df.columns and "Penalties" in df.columns:
        df["Net_penalties_raw"] = df["Penalties_drawn"] - df["Penalties"]
    else:
        df["Net_penalties_raw"] = 0.0

    # Luodaan puuttuvat /60-sarakkeet lennossa (jaettuna peliajalla ja kerrottuna 60:llä)
    # Suojataan nollalla jakamiselta (np.where)
    df["Goals60"] = np.where(df["Time_on_ice"] > 0, (df["Goals"] / df["Time_on_ice"]) * 60, 0.0)
    df["Assists60"] = np.where(df["Time_on_ice"] > 0, (df["Assists"] / df["Time_on_ice"]) * 60, 0.0)
    df["xG60"] = np.where(df["Time_on_ice"] > 0, (df["xG_Expected_goals"] / df["Time_on_ice"]) * 60, 0.0)
    df["Takeaways60"] = np.where(df["Time_on_ice"] > 0, (df["Takeaways"] / df["Time_on_ice"]) * 60, 0.0)
    df["PuckLosses60"] = np.where(df["Time_on_ice"] > 0, (df["Puck_losses"] / df["Time_on_ice"]) * 60, 0.0)
    df["NetPenalties60"] = np.where(df["Time_on_ice"] > 0, (df["Net_penalties_raw"] / df["Time_on_ice"]) * 60, 0.0)
    
    # Volyymitilastot (Käytetään suoraan sellaisenaan ilman /60 jakoa, kuten alkuperäisessä kaavassa)
    df["SlotPasses"] = df["Passes_to_the_slot"] if "Passes_to_the_slot" in df.columns else 0.0
    df["PuckBattlesWon"] = df["Puck_battles_won"] if "Puck_battles_won" in df.columns else 0.0

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

    # =====================================================
    # SINGLE SEASON ENGINE (Alkuperäinen matemaattinen logiikka)
    # =====================================================
    for season in seasons:
        season_df = df[df["Season"] == season].copy()
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

        # LEAGUE AVERAGES
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

        # TEAM-ADJUSTED WIN SHARES (Täysin alkuperäiset korjauskertoimet)
        season_df["OWS"] = season_df["Raw_OWS"] - ((season_df["Team_Off_Strength"] - 1) * 0.50)
        season_df["DWS"] = season_df["Raw_DWS"] - ((season_df["Team_Def_Strength"] - 1) * 0.50)

        # TOI STABILIZATION (K = 400)
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
# DASHBOARD UI
# =========================================================
st.title("🏒 SDHL Player Profiles - Multiseason Engine")

st.markdown("""
Tämä dashboard laskee pelipaikka- ja joukkuekorjatut **Win Shares (WS)** -metriikat turvallisesti **kausi kerrallaan**, suhteuttaen tilastot pelaajien peliaikaan lennossa.
""")

# FILTERS
filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

with filter_col1:
    season_filter = st.selectbox("Valitse kausi", sorted(df["Season"].unique(), reverse=True))

# Rajataan data valitulle kaudelle
season_data = df[df["Season"] == season_filter]

with filter_col2:
    team_filter = st.selectbox("Valitse joukkue", ["All"] + sorted(season_data["Team"].unique().tolist()))

with filter_col3:
    position_filter = st.selectbox("Valitse pelipaikka", ["All", "F", "D"])

with filter_col4:
    min_games = st.slider("Minimiottelut", 1, int(season_data["Games_played"].max()), 10)

# APPLY FILTERS
filtered_df = season_data.copy()

if team_filter != "All":
    filtered_df = filtered_df[filtered_df["Team"] == team_filter]

if position_filter != "All":
    filtered_df = filtered_df[filtered_df["Position"] == position_filter]

filtered_df = filtered_df[filtered_df["Games_played"] >= min_games]

# PLAYER SELECTOR
if not filtered_df.empty:
    player = st.selectbox("Valitse pelaaja", sorted(filtered_df["Player"].unique()))
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
    st.subheader("Kauden prosenttipisteet (Percentiles)")
    p1, p2, p3 = st.columns(3)
    with p1:
        st.metric("OWS Percentile", f"{round(player_df['OWS_percentile'])}%")
    with p2:
        st.metric("DWS Percentile", f"{round(player_df['DWS_percentile'])}%")
    with p3:
        st.metric("WS Percentile", f"{round(player_df['WS_percentile'])}%")

    # PLAYER INFORMATION
    st.subheader("Pelaajan perustiedot")
    info1, info2, info3, info4 = st.columns(4)
    with info1:
        st.write(f"**Ottelut (GP):** {player_df['Games_played']}")
    with info2:
        st.write(f"**Peliaika (TOI):** {round(player_df['Time_on_ice'],1)}")
    with info3:
        st.write(f"**Pisteet:** {player_df['Points']}")
    with info4:
        st.write(f"**Net xG:** {round(player_df['NetxG'],2)}")

    # ADDITIONAL STATISTICS
    st.subheader("Lasketut tehokkuustilastot (Per 60 / Volyymit)")
    stats_df = pd.DataFrame({
        "Tilasto": ["Maalit / 60", "Syötöt / 60", "xG / 60", "Riistot / 60", "Kiekonmenetykset / 60", "Jäähytasapaino / 60", "Voitetut kamppailut", "Syötöt parhaaseen sektoriin"],
        "Arvo": [
            round(player_df["Goals60"], 2), round(player_df["Assists60"], 2), round(player_df["xG60"], 2),
            round(player_df["Takeaways60"], 2), round(player_df["PuckLosses60"], 2), round(player_df["NetPenalties60"], 2),
            round(player_df["PuckBattlesWon"], 2), round(player_df["SlotPasses"], 2)
        ]
    })
    st.dataframe(stats_df, use_container_width=True, hide_index=True)

else:
    st.warning("Valituilla suodattimilla ei löytynyt pelaajia.")

# TOP 10 WIN SHARES FOR THE SELECTED SEASON
st.subheader(f"Top 10 Win Shares - Kausi {season_filter}")
if not filtered_df.empty:
    top_ws = (
        filtered_df[["Player", "Team", "Position", "OWS", "DWS", "WS", "WS_percentile"]]
        .sort_values("WS", ascending=False)
        .head(10)
    )
    st.dataframe(top_ws, use_container_width=True, hide_index=True)
