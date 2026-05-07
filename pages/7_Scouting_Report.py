import streamlit as st
import pandas as pd

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(layout="wide")

# =========================
# PAGE TITLE
# =========================

st.title("📝 Automated Scouting Report")

# =========================
# TEAM LOGOS
# =========================

logo_size = 120

team_logos = {

    "Brynas": "images/Brynas.png",

    "Djurgarden": "images/Djurgarden.png",

    "Farjestad": "images/Farjestad.png",

    "Frolunda": "images/Frolunda.png",

    "HV71": "images/HV71.png",

    "Linkoping": "images/Linkoping.png",

    "Lulea/MSSK": "images/Lulea.png",

    "MODO": "images/MODO.png",

    "SDE HF": "images/SDE HF.png",

    "Skelleftea": "images/Skelleftea AIK.png"
}

# =========================
# LOAD DATA
# =========================

df = pd.read_excel(
    "SDHL_ZScore_GameScore_Final.xlsx"
)

# =========================
# CLEAN DATA
# =========================

numeric_columns = [
    "Goals/60",
    "Assists/60",
    "xG/60",
    "Net xG",
    "Game Score",
    "Time on ice"
]

for col in numeric_columns:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

df = df.dropna(subset=numeric_columns)

# =========================
# SIDEBAR FILTERS
# =========================

st.sidebar.header("Filters")

# POSITION FILTER

positions = sorted(
    df["Position"].unique()
)

selected_position = st.sidebar.selectbox(
    "Position",
    positions
)

filtered_df = df[
    df["Position"] == selected_position
]

# TEAM FILTER

teams = sorted(
    filtered_df["Team"].unique()
)

selected_team = st.sidebar.selectbox(
    "Team",
    teams
)

# PLAYER FILTER

players = sorted(
    filtered_df[
        filtered_df["Team"] == selected_team
    ]["Player"].unique()
)

selected_player = st.sidebar.selectbox(
    "Player",
    players
)

# =========================
# PLAYER DATA
# =========================

p = filtered_df[
    filtered_df["Player"] == selected_player
].iloc[0]

# =========================
# PLAYER CARD
# =========================

st.subheader("🏒 Player Profile")

col1, col2 = st.columns([1, 2])

# LEFT SIDE

with col1:

    if p["Team"] in team_logos:

        st.image(
            team_logos[p["Team"]],
            width=logo_size
        )

    st.markdown(
        f"## {selected_player}"
    )

    st.markdown(
        f"### {p['Team']} | {p['Position']}"
    )

    st.metric(
        "Game Score",
        round(p["Game Score"], 2)
    )

    st.metric(
        "Goals/60",
        round(p["Goals/60"], 2)
    )

    st.metric(
        "Assists/60",
        round(p["Assists/60"], 2)
    )

    st.metric(
        "xG/60",
        round(p["xG/60"], 2)
    )

    st.metric(
        "Net xG",
        round(p["Net xG"], 2)
    )

    st.metric(
        "TOI",
        round(p["Time on ice"], 1)
    )

# =========================
# SCOUTING REPORT
# =========================

with col2:

    st.subheader("🔍 Automated Scouting Report")

    report = []

    # =========================
    # SCORING
    # =========================

    if p["Goals/60"] >= 1.0:

        report.append(
            "Elite goal scorer with high-end finishing ability."
        )

    elif p["Goals/60"] >= 0.7:

        report.append(
            "Strong scoring threat capable of generating offense consistently."
        )

    elif p["Goals/60"] >= 0.4:

        report.append(
            "Contributes offense regularly through scoring opportunities."
        )

    else:

        report.append(
            "Limited scoring production profile."
        )

    # =========================
    # PLAYMAKING
    # =========================

    if p["Assists/60"] >= 1.0:

        report.append(
            "Elite offensive playmaker with strong passing vision."
        )

    elif p["Assists/60"] >= 0.7:

        report.append(
            "Reliable offensive creator capable of generating chances for teammates."
        )

    elif p["Assists/60"] >= 0.4:

        report.append(
            "Provides moderate offensive support through puck movement."
        )

    # =========================
    # SHOT QUALITY
    # =========================

    if p["xG/60"] >= 1.0:

        report.append(
            "Consistently attacks dangerous scoring areas and creates high-quality chances."
        )

    elif p["xG/60"] >= 0.7:

        report.append(
            "Generates quality offensive opportunities regularly."
        )

    # =========================
    # IMPACT
    # =========================

    if p["Net xG"] >= 2:

        report.append(
            "Strong positive on-ice impact player who drives offensive play."
        )

    elif p["Net xG"] >= 0:

        report.append(
            "Positive overall impact profile."
        )

    else:

        report.append(
            "Negative overall impact results based on current metrics."
        )

    # =========================
    # GAME SCORE
    # =========================

    if p["Game Score"] >= 8:

        report.append(
            "Projects as an elite-level offensive performer."
        )

    elif p["Game Score"] >= 5:

        report.append(
            "Projects as a strong top-six offensive player."
        )

    elif p["Game Score"] >= 3:

        report.append(
            "Projects as a reliable middle-lineup contributor."
        )

    else:

        report.append(
            "Current profile suggests depth-level offensive contribution."
        )

    # =========================
    # TOI
    # =========================

    if p["Time on ice"] >= 700:

        report.append(
            "Trusted heavily by coaching staff in high-minute situations."
        )

    elif p["Time on ice"] >= 500:

        report.append(
            "Regularly deployed in meaningful game situations."
        )

    # =========================
    # DISPLAY REPORT
    # =========================

    for sentence in report:

        st.markdown(
            f"- {sentence}"
        )
