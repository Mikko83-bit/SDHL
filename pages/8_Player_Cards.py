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

# MINIMUM TOI

min_toi = st.sidebar.slider(
    "Minimum TOI",
    min_value=0,
    max_value=int(df["Time on ice"].max()),
    value=200,
    step=10
)

# MINIMUM GAMES

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

# POSITION FILTER

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

# PLAYER FILTER

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

    elif value >= 50:
        return "#9BC7F2"

    elif value >= 30:
        return "#F4B6B6"

    else:
        return "#D94B4B"

# ==================================================
# TILE FUNCTION
# ==================================================

def stat_tile(title, value):

    if pd.isna(value):
        value = 0

    value = int(round(value))

    color = get_color(value)

    html = f"""
    <div style="
        background:{color};
        border-radius:10px;
        height:110px;
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
            font-size:38px;
            font-weight:800;
            line-height:1;
        ">
            {value}
        </div>

    </div>
    """

    components.html(
        html,
        height=120
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

    stat_tile(
        "Shooting",
        p["Shooting Score"]
    )

with c2:

    stat_tile(
        "Playmaking",
        p["Playmaking Score"]
    )

with c3:

    stat_tile(
        "Transition",
        p["Transition Score"]
    )

c4, c5, c6 = st.columns(3)

with c4:

    stat_tile(
        "Puck Movement",
        p["Puck Movement Score"]
    )

with c5:

    stat_tile(
        "Defense",
        p["Defense Score"]
    )

with c6:

    stat_tile(
        "Impact",
        p["Impact Score"]
    )

# ==================================================
# OVERALL SECTION
# ==================================================

st.markdown("## Overall")

o1, o2 = st.columns(2)

with o1:

    stat_tile(
        "Overall Score",
        p["Overall Score"]
    )

with o2:

    stat_tile(
        "Overall Percentile",
        p["Overall Score Percentile"]
    )

# ==================================================
# RAW STATS
# ==================================================

st.markdown("## Raw Production")

r1, r2, r3, r4 = st.columns(4)

with r1:

    stat_tile(
        "Points",
        p["Points"]
    )

with r2:

    stat_tile(
        "Goals",
        p["Goals"]
    )

with r3:

    stat_tile(
        "Assists",
        p["Assists"]
    )

with r4:

    stat_tile(
        "xG",
        p["xG (Expected goals)"]
    )
