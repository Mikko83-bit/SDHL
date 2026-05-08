import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="SDHL Player Comparison",
    layout="wide"
)

# ==================================================
# LOAD DATA
# ==================================================

df = pd.read_excel(
    "SDHL_Processed_2025_2026.xlsx"
)

# ==================================================
# CLEAN DATA
# ==================================================

df.columns = df.columns.str.strip()

df["Position"] = (
    df["Position"]
    .astype(str)
    .str.strip()
)

df["Team"] = (
    df["Team"]
    .astype(str)
    .str.strip()
)

# ==================================================
# POSITION-SPECIFIC OVERALL SCORE
# ==================================================

df["Overall Score"] = 0.0

# FORWARDS

forward_mask = df["Position"] == "F"

df.loc[forward_mask, "Overall Score"] = (

    df.loc[forward_mask, "Shooting Score"] * 0.25 +

    df.loc[forward_mask, "Playmaking Score"] * 0.25 +

    df.loc[forward_mask, "Transition Score"] * 0.25 +

    df.loc[forward_mask, "Puck Movement Score"] * 0.10 +

    df.loc[forward_mask, "Defense Score"] * 0.05 +

    df.loc[forward_mask, "Impact Score"] * 0.10

)

# DEFENSEMEN

defense_mask = df["Position"] == "D"

df.loc[defense_mask, "Overall Score"] = (

    df.loc[defense_mask, "Shooting Score"] * 0.10 +

    df.loc[defense_mask, "Playmaking Score"] * 0.15 +

    df.loc[defense_mask, "Transition Score"] * 0.25 +

    df.loc[defense_mask, "Puck Movement Score"] * 0.25 +

    df.loc[defense_mask, "Defense Score"] * 0.15 +

    df.loc[defense_mask, "Impact Score"] * 0.10

)

# ==================================================
# OVERALL PERCENTILE
# ==================================================

df["Overall Score Percentile"] = (

    df.groupby("Position")[
        "Overall Score"
    ].rank(pct=True) * 100

)

# ==================================================
# ROUND VALUES
# ==================================================

numeric_cols = df.select_dtypes(
    include="number"
).columns

df[numeric_cols] = df[numeric_cols].round(1)

# ==================================================
# TEAM LOGOS
# ==================================================

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
    "Skelleftea AIK": "images/Skelleftea AIK.png"

}

# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.header("Filters")

# TOI FILTER

min_toi = st.sidebar.slider(
    "Minimum TOI",
    min_value=0,
    max_value=int(df["Time on ice"].max()),
    value=200,
    step=10
)

# GAMES FILTER

min_games = st.sidebar.slider(
    "Minimum Games",
    min_value=0,
    max_value=int(df["Games played"].max()),
    value=5,
    step=1
)

# APPLY FILTERS

df = df[
    (df["Time on ice"] >= min_toi) &
    (df["Games played"] >= min_games)
]

# ==================================================
# POSITION FILTER
# ==================================================

positions = sorted(
    df["Position"].dropna().unique()
)

selected_position = st.sidebar.selectbox(
    "Position",
    positions
)

filtered_df = df[
    df["Position"] == selected_position
]

# ==================================================
# TEAM FILTERS
# ==================================================

teams = sorted(
    filtered_df["Team"].dropna().unique()
)

team1 = st.sidebar.selectbox(
    "Team 1",
    teams
)

team2 = st.sidebar.selectbox(
    "Team 2",
    teams,
    index=min(1, len(teams)-1)
)

# ==================================================
# PLAYER FILTERS
# ==================================================

team1_players = sorted(
    filtered_df[
        filtered_df["Team"] == team1
    ]["Player"].dropna().unique()
)

team2_players = sorted(
    filtered_df[
        filtered_df["Team"] == team2
    ]["Player"].dropna().unique()
)

st.sidebar.markdown("---")

player1 = st.sidebar.selectbox(
    "Player 1",
    team1_players
)

player2 = st.sidebar.selectbox(
    "Player 2",
    team2_players
)

# ==================================================
# PLAYER ROWS
# ==================================================

p1 = filtered_df[
    filtered_df["Player"] == player1
].iloc[0]

p2 = filtered_df[
    filtered_df["Player"] == player2
].iloc[0]

# ==================================================
# COLOR FUNCTION
# ==================================================

def get_color(value):

    if value >= 90:
        return "#123B6E"

    elif value >= 75:
        return "#2E6DB4"

    elif value >= 60:
        return "#6FA8DC"

    elif value >= 40:
        return "#B7D7F0"

    elif value >= 25:
        return "#F4B6B6"

    else:
        return "#D94B4B"

# ==================================================
# LABEL FUNCTION
# ==================================================

def get_label(value):

    if value >= 90:
        return "ELITE"

    elif value >= 75:
        return "EXCELLENT"

    elif value >= 60:
        return "GOOD"

    elif value >= 40:
        return "AVERAGE"

    elif value >= 25:
        return "BELOW AVG"

    else:
        return "WEAK"

# ==================================================
# COMPACT SKILL TILE
# ==================================================

def comparison_tile(title, value):

    if pd.isna(value):
        value = 0

    value = int(round(value))

    color = get_color(value)

    label = get_label(value)

    html = f"""
    <div style="
        background:{color};
        border-radius:8px;
        height:68px;
        padding:4px;
        display:flex;
        flex-direction:column;
        justify-content:center;
        align-items:center;
        font-family:Arial;
        color:black;
        margin-bottom:4px;
    ">

        <div style="
            font-size:10px;
            font-weight:700;
            text-align:center;
        ">
            {title}
        </div>

        <div style="
            font-size:22px;
            font-weight:800;
            line-height:1;
            margin-top:2px;
        ">
            {value}
        </div>

        <div style="
            font-size:8px;
            font-weight:700;
            margin-top:2px;
            letter-spacing:1px;
        ">
            {label}
        </div>

    </div>
    """

    components.html(
        html,
        height=74
    )

# ==================================================
# COMPACT RAW TILE
# ==================================================

def raw_tile(title, value):

    if pd.isna(value):
        value = 0

    value = round(float(value), 1)

    html = f"""
    <div style="
        background:#1B1F2A;
        border-radius:8px;
        height:68px;
        padding:4px;
        display:flex;
        flex-direction:column;
        justify-content:center;
        align-items:center;
        font-family:Arial;
        color:white;
        margin-bottom:4px;
        border:1px solid #2D3748;
    ">

        <div style="
            font-size:10px;
            font-weight:700;
            color:#C7D0E0;
        ">
            {title}
        </div>

        <div style="
            font-size:22px;
            font-weight:800;
            margin-top:2px;
        ">
            {value}
        </div>

    </div>
    """

    components.html(
        html,
        height=74
    )

# ==================================================
# TITLE
# ==================================================

st.title("🏒 SDHL Player Comparison")

# ==================================================
# PLAYER HEADERS
# ==================================================

h1, h2, h3 = st.columns([5,1,5])

with h1:

    if p1["Team"] in team_logos:

        st.image(
            team_logos[p1["Team"]],
            width=80
        )

    st.markdown(f"### {player1}")

    st.markdown(
        f"{p1['Team']} | {p1['Position']}"
    )

with h2:

    st.markdown("## VS")

with h3:

    if p2["Team"] in team_logos:

        st.image(
            team_logos[p2["Team"]],
            width=80
        )

    st.markdown(f"### {player2}")

    st.markdown(
        f"{p2['Team']} | {p2['Position']}"
    )

# ==================================================
# SKILL COMPARISON
# ==================================================

st.markdown("## Skill Comparison")

skills = [

    ("Shooting", "Shooting Score"),
    ("Playmaking", "Playmaking Score"),
    ("Transition", "Transition Score"),
    ("Puck Movement", "Puck Movement Score"),
    ("Defense", "Defense Score"),
    ("Impact", "Impact Score"),
    ("Overall", "Overall Score")

]

for title, stat in skills:

    c1, c2, c3 = st.columns([5,1,5])

    with c1:
        comparison_tile(title, p1[stat])

    with c2:
        st.markdown("")

    with c3:
        comparison_tile(title, p2[stat])

# ==================================================
# RAW PRODUCTION
# ==================================================

st.markdown("## Raw Production")

raw_stats = [

    ("GP", "Games played"),

    ("TOI", "Time on ice"),

    ("Points", "Points"),

    ("Goals", "Goals"),

    ("Assists", "Assists"),

    ("xG", "xG (Expected goals)")

]

for title, stat in raw_stats:

    c1, c2, c3 = st.columns([5,1,5])

    with c1:
        raw_tile(title, p1[stat])

    with c2:
        st.markdown("")

    with c3:
        raw_tile(title, p2[stat])
