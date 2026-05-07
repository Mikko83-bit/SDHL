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
        border-radius:8px;
        height:95px;
        padding:8px;
        display:flex;
        flex-direction:column;
        justify-content:center;
        align-items:center;
        font-family:Arial;
        color:black;
        margin-bottom:10px;
    ">

        <div style="
            font-size:13px;
            font-weight:600;
            text-align:center;
            margin-bottom:6px;
        ">
            {title}
        </div>

        <div style="
            font-size:34px;
            font-weight:800;
            line-height:1;
        ">
            {value}
        </div>

    </div>
    """

    components.html(
        html,
        height=105
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
# SHOOTING
# ==================================================

st.markdown("## Shooting")

c1, c2, c3, c4 = st.columns(4)

with c1:
    stat_tile(
        "Shots",
        p["Shots/60 Percentile"]
    )

with c2:
    stat_tile(
        "Scoring Chances",
        p["Scoring chances - total/60 Percentile"]
    )

with c3:
    stat_tile(
        "Inner Slot",
        p["Inner slot shots - total/60 Percentile"]
    )

with c4:
    stat_tile(
        "Finishing",
        p["Goals/60 Percentile"]
    )

# ==================================================
# PLAYMAKING
# ==================================================

st.markdown("## Playmaking")

c1, c2, c3, c4 = st.columns(4)

with c1:
    stat_tile(
        "Pre-Shot Passes",
        p["Pre-shots passes/60 Percentile"]
    )

with c2:
    stat_tile(
        "Slot Passing",
        p["Passes to the slot/60 Percentile"]
    )

with c3:
    stat_tile(
        "First Assists",
        p["First assist/60 Percentile"]
    )

with c4:
    stat_tile(
        "Pass Accuracy",
        p["Accurate passes, % Percentile"]
    )

# ==================================================
# TRANSITION
# ==================================================

st.markdown("## Transition")

c1, c2, c3, c4 = st.columns(4)

with c1:
    stat_tile(
        "Entries",
        p["Entries/60 Percentile"]
    )

with c2:
    stat_tile(
        "Carry Entries",
        p["Entries via stickhandling/60 Percentile"]
    )

with c3:
    stat_tile(
        "Controlled Entries",
        p["Entries via pass/60 Percentile"]
    )

with c4:
    stat_tile(
        "Breakouts",
        p["Breakouts/60 Percentile"]
    )

# ==================================================
# PUCK MOVEMENT
# ==================================================

st.markdown("## Puck Movement")

c1, c2, c3, c4 = st.columns(4)

with c1:
    stat_tile(
        "Pass Exits",
        p["Breakouts via pass/60 Percentile"]
    )

with c2:
    stat_tile(
        "Carry Exits",
        p["Breakouts via stickhandling/60 Percentile"]
    )

with c3:
    stat_tile(
        "Puck Touches",
        p["Puck touches/60 Percentile"]
    )

with c4:
    stat_tile(
        "Puck Control",
        p["Puck control time/60 Percentile"]
    )

# ==================================================
# DEFENSE
# ==================================================

st.markdown("## Defense")

c1, c2, c3, c4 = st.columns(4)

with c1:
    stat_tile(
        "Takeaways",
        p["Takeaways/60 Percentile"]
    )

with c2:
    stat_tile(
        "DZ Takeaways",
        p["Takeaways in DZ Percentile"]
    )

with c3:
    stat_tile(
        "Battle Win %",
        p["Puck battles won, % Percentile"]
    )

with c4:
    stat_tile(
        "Suppression",
        p["Opponent's xG when on ice Percentile"]
    )

# ==================================================
# IMPACT
# ==================================================

st.markdown("## Impact")

c1, c2, c3, c4 = st.columns(4)

with c1:
    stat_tile(
        "Net xG",
        p["Net xG (xG player on - opp. team's xG) Percentile"]
    )

with c2:
    stat_tile(
        "Team xG",
        p["Team xG when on ice Percentile"]
    )

with c3:
    stat_tile(
        "Corsi",
        p["CORSI for, % Percentile"]
    )

with c4:
    stat_tile(
        "Fenwick",
        p["Fenwick for, % Percentile"]
    )

# ==================================================
# OVERALL
# ==================================================

st.markdown("## Overall")

c1, c2, c3 = st.columns(3)

with c1:
    stat_tile(
        "Overall Score",
        p["Overall Score"]
    )

with c2:
    stat_tile(
        "Overall Percentile",
        p["Overall Score Percentile"]
    )

with c3:
    stat_tile(
        "Puck Movement",
        p["Puck Movement Score"]
    )
