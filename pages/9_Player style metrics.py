import streamlit as st
import pandas as pd

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Player Style Metrics",
    layout="wide"
)

st.title("📊 Player Style Profile")

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
# FIX OZ POSSESSION /60
# ==================================================

df["OZ possession/60"] = (

    df["OZ possession"] /
    df["Time on ice"]

) * 60

# ==================================================
# ROUND VALUES
# ==================================================

numeric_cols = df.select_dtypes(
    include="number"
).columns

df[numeric_cols] = df[numeric_cols].round(2)

# ==================================================
# SIDEBAR FILTERS
# ==================================================

st.sidebar.header("Filters")

# POSITION

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

# TEAM

teams = sorted(
    filtered_df["Team"].dropna().unique()
)

selected_team = st.sidebar.selectbox(
    "Team",
    teams
)

# PLAYER

players = sorted(
    filtered_df[
        filtered_df["Team"] == selected_team
    ]["Player"].dropna().unique()
)

selected_player = st.sidebar.selectbox(
    "Player",
    players
)

# ==================================================
# PLAYER ROW
# ==================================================

p = filtered_df[
    filtered_df["Player"] == selected_player
].iloc[0]

# ==================================================
# HEADER
# ==================================================

header1, header2 = st.columns([1,4])

with header1:

    if p["Team"] in team_logos:

        st.image(
            team_logos[p["Team"]],
            width=90
        )

with header2:

    st.markdown(
        f"## {selected_player}"
    )

    st.markdown(
        f"### {p['Team']} | {p['Position']}"
    )

    info1, info2, info3 = st.columns(3)

    with info1:

        st.metric(
            "TOI",
            round(p["Time on ice"],1)
        )

    with info2:

        st.metric(
            "Games",
            int(p["Games played"])
        )

    with info3:

        st.metric(
            "Points",
            int(p["Points"])
        )

st.markdown("---")

# ==================================================
# COLOR FUNCTION
# ==================================================

def percentile_color(value):

    if value >= 90:
        return "#0B5ED7"

    elif value >= 75:
        return "#3D8BFD"

    elif value >= 60:
        return "#74A7FF"

    elif value >= 40:
        return "#AFC8FF"

    elif value >= 25:
        return "#FFB3B3"

    else:
        return "#E03131"

# ==================================================
# METRIC BOX
# ==================================================

def metric_box(title, value, percentile):

    if pd.isna(value):
        value = 0

    if pd.isna(percentile):
        percentile = 0

    color = percentile_color(percentile)

    st.markdown(

        f"""
        <div style="
            background:{color};
            padding:8px;
            border-radius:8px;
            margin-bottom:8px;
            height:95px;
        ">

            <div style="
                font-size:11px;
                color:white;
                font-weight:700;
            ">
                {title}
            </div>

            <div style="
                font-size:24px;
                color:white;
                font-weight:800;
                margin-top:2px;
            ">
                {round(value,2)}
            </div>

            <div style="
                font-size:11px;
                color:white;
                margin-top:2px;
            ">
                {round(percentile)}th percentile
            </div>

        </div>
        """,

        unsafe_allow_html=True

    )

# ==================================================
# SHOOTING
# ==================================================

st.subheader("🔥 Shooting")

s1, s2, s3, s4, s5 = st.columns(5)

with s1:

    metric_box(
        "Goals/60",
        p["Goals/60"],
        p["Goals/60 Percentile"]
    )

with s2:

    metric_box(
        "Shots/60",
        p["Shots/60"],
        p["Shots/60 Percentile"]
    )

with s3:

    metric_box(
        "xG/60",
        p["xG (Expected goals)/60"],
        p["xG (Expected goals)/60 Percentile"]
    )

with s4:

    metric_box(
        "Inner Slot Shots/60",
        p["Inner slot shots - total/60"],
        p["Inner slot shots - total/60 Percentile"]
    )

with s5:

    metric_box(
        "Scoring Chances/60",
        p["Scoring chances - total/60"],
        p["Scoring chances - total/60 Percentile"]
    )

# ==================================================
# PLAYMAKING
# ==================================================

st.markdown("---")

st.subheader("🎯 Playmaking")

p1, p2, p3 = st.columns(3)

with p1:

    metric_box(
        "Pre-Shot Passes/60",
        p["Pre-shots passes/60"],
        p["Pre-shots passes/60 Percentile"]
    )

with p2:

    metric_box(
        "Slot Passes/60",
        p["Passes to the slot/60"],
        p["Passes to the slot/60 Percentile"]
    )

with p3:

    metric_box(
        "First Assists/60",
        p["First assist/60"],
        p["First assist/60 Percentile"]
    )

# ==================================================
# TRANSITION
# ==================================================

st.markdown("---")

st.subheader("🚀 Transition")

t1, t2, t3, t4, t5 = st.columns(5)

with t1:

    metric_box(
        "Entries Carry/60",
        p["Entries via stickhandling/60"],
        p["Entries via stickhandling/60 Percentile"]
    )

with t2:

    metric_box(
        "Entries Pass/60",
        p["Entries via pass/60"],
        p["Entries via pass/60 Percentile"]
    )

with t3:

    metric_box(
        "Breakouts Carry/60",
        p["Breakouts via stickhandling/60"],
        p["Breakouts via stickhandling/60 Percentile"]
    )

with t4:

    metric_box(
        "Breakouts Pass/60",
        p["Breakouts via pass/60"],
        p["Breakouts via pass/60 Percentile"]
    )

with t5:

    metric_box(
        "Breakouts/60",
        p["Breakouts/60"],
        p["Breakouts/60 Percentile"]
    )

# ==================================================
# POSSESSION
# ==================================================

st.markdown("---")

st.subheader("🏒 Possession")

o1, o2 = st.columns(2)

with o1:

    metric_box(
        "Puck Touches/60",
        p["Puck touches/60"],
        p["Puck touches/60 Percentile"]
    )

with o2:

    metric_box(
        "OZ Possession/60",
        p["OZ possession/60"],
        p["OZ possession/60 Percentile"]
    )

# ==================================================
# DEFENSE
# ==================================================

st.markdown("---")

st.subheader("🛡️ Defense")

d1, d2, d3, d4 = st.columns(4)

with d1:

    metric_box(
        "Takeaways/60",
        p["Takeaways/60"],
        p["Takeaways/60 Percentile"]
    )

with d2:

    metric_box(
        "DZ Takeaways",
        p["Takeaways in DZ"],
        p["Takeaways in DZ Percentile"]
    )

with d3:

    metric_box(
        "Opponent xG",
        p["Opponent's xG when on ice"],
        p["Opponent's xG when on ice Percentile"]
    )

with d4:

    metric_box(
        "Puck Losses/60",
        p["Puck losses/60"],
        100 - p["Puck losses/60 Percentile"]
    )

# ==================================================
# IMPACT
# ==================================================

st.markdown("---")

st.subheader("📈 Impact")

i1, i2, i3 = st.columns(3)

with i1:

    metric_box(
        "Net xG",
        p["Net xG (xG player on - opp. team's xG)"],
        p["Net xG (xG player on - opp. team's xG) Percentile"]
    )

with i2:

    metric_box(
        "Team xG On-Ice",
        p["Team xG when on ice"],
        p["Team xG when on ice Percentile"]
    )

with i3:

    metric_box(
        "Overall Score",
        p["Overall Score"],
        p["Overall Score Percentile"]
    )
