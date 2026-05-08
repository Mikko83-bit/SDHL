import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="SDHL Player Cards",
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

# ==================================================
# SIDEBAR FILTERS
# ==================================================

st.sidebar.header("Filters")

# ==================================================
# MINIMUM TOI
# ==================================================

min_toi = st.sidebar.slider(
    "Minimum TOI",
    min_value=0,
    max_value=int(df["Time on ice"].max()),
    value=200,
    step=10
)

# ==================================================
# MINIMUM GAMES
# ==================================================

min_games = st.sidebar.slider(
    "Minimum Games",
    min_value=0,
    max_value=int(df["Games played"].max()),
    value=5,
    step=1
)

# ==================================================
# APPLY FILTERS
# ==================================================

df = df[
    (df["Time on ice"] >= min_toi) &
    (df["Games played"] >= min_games)
]

# ==================================================
# TEAM FILTER
# ==================================================

teams = sorted(
    df["Team"].dropna().unique()
)

selected_team = st.sidebar.selectbox(
    "Team",
    ["All Teams"] + teams
)

if selected_team != "All Teams":

    df = df[
        df["Team"] == selected_team
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
# PLAYER FILTER
# ==================================================

players = sorted(
    filtered_df["Player"].dropna().unique()
)

selected_player = st.sidebar.selectbox(
    "Player",
    players
)

# ==================================================
# PLAYER DATA
# ==================================================

p = filtered_df[
    filtered_df["Player"] == selected_player
].iloc[0]

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
# PAGE TITLE
# ==================================================

st.title("🏒 SDHL Player Cards")

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
# PERCENTILE TILE
# ==================================================

def stat_tile(title, value):

    if pd.isna(value):
        value = 0

    value = int(round(value))

    color = get_color(value)

    label = get_label(value)

    html = f"""
    <div style="
        background:{color};
        border-radius:12px;
        height:125px;
        padding:10px;
        display:flex;
        flex-direction:column;
        justify-content:center;
        align-items:center;
        font-family:Arial;
        color:black;
        margin-bottom:10px;
    ">

        <div style="
            font-size:14px;
            font-weight:700;
            text-align:center;
            margin-bottom:8px;
        ">
            {title}
        </div>

        <div style="
            font-size:40px;
            font-weight:800;
            line-height:1;
        ">
            {value}
        </div>

        <div style="
            font-size:12px;
            font-weight:700;
            margin-top:8px;
            letter-spacing:1px;
        ">
            {label}
        </div>

    </div>
    """

    components.html(
        html,
        height=135
    )

# ==================================================
# RAW STAT TILE
# ==================================================

def raw_stat_tile(title, value):

    if pd.isna(value):
        value = 0

    value = round(float(value), 1)

    html = f"""
    <div style="
        background:#1B1F2A;
        border-radius:12px;
        height:125px;
        padding:10px;
        display:flex;
        flex-direction:column;
        justify-content:center;
        align-items:center;
        font-family:Arial;
        color:white;
        margin-bottom:10px;
        border:1px solid #2D3748;
    ">

        <div style="
            font-size:14px;
            font-weight:700;
            text-align:center;
            margin-bottom:8px;
            color:#C7D0E0;
        ">
            {title}
        </div>

        <div style="
            font-size:42px;
            font-weight:800;
            line-height:1;
            color:white;
        ">
            {value}
        </div>

    </div>
    """

    components.html(
        html,
        height=135
    )

# ==================================================
# HEADER
# ==================================================

header1, header2 = st.columns([1, 5])

with header1:

    if p["Team"] in team_logos:

        st.image(
            team_logos[p["Team"]],
            width=120
        )

with header2:

    st.markdown(
        f"# {selected_player}"
    )

    st.markdown(
        f"### {p['Team']} | {p['Position']}"
    )

    st.markdown(
        f"""
        **GP:** {int(p['Games played'])}
        |
        **TOI:** {round(p['Time on ice'])}
        """
    )

# ==================================================
# SKILL PROFILE
# ==================================================

st.markdown("## Skill Profile")

c1, c2, c3 = st.columns(3)

with c1:
    stat_tile("Shooting", p["Shooting Score"])

with c2:
    stat_tile("Playmaking", p["Playmaking Score"])

with c3:
    stat_tile("Transition", p["Transition Score"])

c4, c5, c6 = st.columns(3)

with c4:
    stat_tile("Puck Movement", p["Puck Movement Score"])

with c5:
    stat_tile("Defense", p["Defense Score"])

with c6:
    stat_tile("Impact", p["Impact Score"])

# ==================================================
# OVERALL
# ==================================================

st.markdown("## Overall")

o1, o2 = st.columns(2)

with o1:
    stat_tile("Overall Score", p["Overall Score"])

with o2:
    stat_tile(
        "Overall Percentile",
        p["Overall Score Percentile"]
    )

# ==================================================
# RAW PRODUCTION
# ==================================================

st.markdown("## Raw Production")

r1, r2, r3, r4 = st.columns(4)

with r1:
    raw_stat_tile("Points", p["Points"])

with r2:
    raw_stat_tile("Goals", p["Goals"])

with r3:
    raw_stat_tile("Assists", p["Assists"])

with r4:
    raw_stat_tile("xG", p["xG (Expected goals)"])
