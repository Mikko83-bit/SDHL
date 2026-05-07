import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="SDHL Microstats Cards",
    layout="wide"
)

# ==================================================
# LOAD DATA
# ==================================================

df = pd.read_excel(
    "SDHL_Player_Cards_Data.xlsx"
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
# FIX % COLUMNS
# ==================================================

percent_columns = [

    "Accurate passes, %",
    "Puck battles won, %",
    "CORSI for, %",
    "Fenwick for, %"

]

for col in percent_columns:

    if col in df.columns:

        df[col] = (

            df[col]
            .astype(str)
            .str.replace("%", "")
            .str.replace(",", ".")

        )

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        ).fillna(0)

# ==================================================
# CONVERT NUMERIC
# ==================================================

numeric_columns = [

    "Time on ice",
    "Games played",

    "Goals/60",
    "Assists/60",
    "Shots/60",
    "xG (Expected goals)/60",

    "Scoring chances - total/60",
    "Inner slot shots - total/60",

    "Pre-shots passes/60",
    "Passes to the slot/60",
    "First assist/60",

    "Entries/60",
    "Entries via stickhandling/60",
    "Entries via pass/60",

    "Breakouts/60",
    "Breakouts via stickhandling/60",
    "Breakouts via pass/60",

    "Puck touches/60",
    "Puck control time/60",

    "Takeaways/60",
    "Takeaways in DZ",

    "Opponent's xG when on ice",

    "Net xG (xG player on - opp. team's xG)",
    "Team xG when on ice"

]

for col in numeric_columns:

    if col in df.columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        ).fillna(0)

# ==================================================
# SIDEBAR FILTERS
# ==================================================

st.sidebar.header("Filters")

# SAMPLE FILTERS

st.sidebar.subheader("Sample Filters")

min_toi = st.sidebar.slider(
    "Minimum TOI",
    min_value=0,
    max_value=int(df["Time on ice"].max()),
    value=200,
    step=10
)

min_games = st.sidebar.slider(
    "Minimum Games",
    min_value=0,
    max_value=int(df["Games played"].max()),
    value=5,
    step=1
)

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
# CREATE POSITION-BASED PERCENTILES
# ==================================================

percentile_metrics = [

    "Goals/60",
    "Assists/60",
    "Shots/60",
    "xG (Expected goals)/60",

    "Scoring chances - total/60",
    "Inner slot shots - total/60",

    "Pre-shots passes/60",
    "Passes to the slot/60",
    "First assist/60",
    "Accurate passes, %",

    "Entries/60",
    "Entries via stickhandling/60",
    "Entries via pass/60",

    "Breakouts/60",
    "Breakouts via stickhandling/60",
    "Breakouts via pass/60",

    "Puck touches/60",
    "Puck control time/60",

    "Takeaways/60",
    "Takeaways in DZ",
    "Puck battles won, %",

    "Opponent's xG when on ice",

    "Net xG (xG player on - opp. team's xG)",
    "Team xG when on ice",

    "CORSI for, %",
    "Fenwick for, %"

]

for metric in percentile_metrics:

    if metric in df.columns:

        df[f"{metric} Percentile"] = (

            df.groupby("Position")[metric]
            .rank(pct=True) * 100

        )

# REVERSE NEGATIVE METRIC

if "Opponent's xG when on ice" in df.columns:

    df["Opponent's xG when on ice Percentile"] = (

        100 -

        df.groupby("Position")[
            "Opponent's xG when on ice"
        ].rank(pct=True) * 100

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

    "Lulea/MSSK": "images/Lulea.png",
    "Brynas": "images/Brynas.png",
    "Djurgarden": "images/Djurgarden.png",
    "Farjestad": "images/Farjestad.png",
    "Frolunda": "images/Frolunda.png",
    "HV71": "images/HV71.png",
    "Linkoping": "images/Linkoping.png",
    "MODO": "images/MODO.png",
    "SDE HF": "images/SDE HF.png",
    "Skelleftea AIK": "images/Skelleftea AIK.png"

}

# ==================================================
# PAGE TITLE
# ==================================================

st.title("🏒 SDHL Microstats Cards")

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
            {value}%
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

# ==================================================
# SHOOTING
# ==================================================

st.markdown("## Shooting")

c1, c2, c3, c4 = st.columns(4)

with c1:
    stat_tile("Shots", p["Shots/60 Percentile"])

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
