import streamlit as st
import pandas as pd

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Player Style Metrics",
    layout="wide"
)

st.title("📊 Player Style Metrics")

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
# SIDEBAR
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
# PLAYER
# ==================================================

p = filtered_df[
    filtered_df["Player"] == selected_player
].iloc[0]

# ==================================================
# HELPERS
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

def percentile_label(value):

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
# METRIC TILE
# ==================================================

def metric_tile(title, value, percentile):

    if pd.isna(value):
        value = 0

    if pd.isna(percentile):
        percentile = 0

    color = percentile_color(percentile)

    label = percentile_label(percentile)

    st.markdown(

        f"""
        <div style="
            background:{color};
            padding:14px;
            border-radius:10px;
            margin-bottom:10px;
        ">

            <div style="
                font-size:15px;
                font-weight:700;
                color:white;
            ">
                {title}
            </div>

            <div style="
                font-size:32px;
                font-weight:800;
                color:white;
                margin-top:5px;
            ">
                {round(value,2)}
            </div>

            <div style="
                font-size:14px;
                color:white;
                margin-top:4px;
            ">
                {round(percentile)}th percentile
            </div>

            <div style="
                font-size:12px;
                color:white;
                letter-spacing:1px;
                margin-top:2px;
            ">
                {label}
            </div>

        </div>
        """,

        unsafe_allow_html=True

    )

# ==================================================
# HEADER
# ==================================================

st.markdown("---")

c1, c2, c3 = st.columns([2,2,2])

with c1:

    st.metric(
        "Overall Score",
        round(p["Overall Score"],1)
    )

with c2:

    st.metric(
        "Overall Percentile",
        f"{round(p['Overall Score Percentile'])}th"
    )

with c3:

    st.metric(
        "TOI",
        round(p["Time on ice"],1)
    )

# ==================================================
# SHOOTING
# ==================================================

st.markdown("---")

st.subheader("🎯 Shooting")

s1, s2, s3, s4 = st.columns(4)

with s1:

    metric_tile(
        "Goals/60",
        p["Goals/60"],
        p["Goals/60 Percentile"]
    )

with s2:

    metric_tile(
        "Shots/60",
        p["Shots/60"],
        p["Shots/60 Percentile"]
    )

with s3:

    metric_tile(
        "xG/60",
        p["xG (Expected goals)/60"],
        p["xG (Expected goals)/60 Percentile"]
    )

with s4:

    metric_tile(
        "Inner Slot Shots/60",
        p["Inner slot shots - total/60"],
        p["Inner slot shots - total/60 Percentile"]
    )

# ==================================================
# PLAYMAKING
# ==================================================

st.markdown("---")

st.subheader("🎯 Playmaking")

p1, p2, p3, p4 = st.columns(4)

with p1:

    metric_tile(
        "Pre-Shot Passes/60",
        p["Pre-shots passes/60"],
        p["Pre-shots passes/60 Percentile"]
    )

with p2:

    metric_tile(
        "Slot Passes/60",
        p["Passes to the slot/60"],
        p["Passes to the slot/60 Percentile"]
    )

with p3:

    metric_tile(
        "First Assists/60",
        p["First assist/60"],
        p["First assist/60 Percentile"]
    )

with p4:

    metric_tile(
        "Accurate Passes/60",
        p["Accurate passes/60"],
        p["Accurate passes/60 Percentile"]
    )

# ==================================================
# TRANSITION
# ==================================================

st.markdown("---")

st.subheader("🚀 Transition")

t1, t2, t3, t4 = st.columns(4)

with t1:

    metric_tile(
        "Entries Carry/60",
        p["Entries via stickhandling/60"],
        p["Entries via stickhandling/60 Percentile"]
    )

with t2:

    metric_tile(
        "Entries Pass/60",
        p["Entries via pass/60"],
        p["Entries via pass/60 Percentile"]
    )

with t3:

    metric_tile(
        "Breakouts Carry/60",
        p["Breakouts via stickhandling/60"],
        p["Breakouts via stickhandling/60 Percentile"]
    )

with t4:

    metric_tile(
        "Breakouts Pass/60",
        p["Breakouts via pass/60"],
        p["Breakouts via pass/60 Percentile"]
    )

# ==================================================
# POSSESSION
# ==================================================

st.markdown("---")

st.subheader("🏒 Possession")

o1, o2, o3 = st.columns(3)

with o1:

    metric_tile(
        "Puck Touches/60",
        p["Puck touches/60"],
        p["Puck touches/60 Percentile"]
    )

with o2:

    metric_tile(
        "OZ Possession/60",
        p["OZ possession/60"],
        p["OZ possession/60 Percentile"]
    )

with o3:

    metric_tile(
        "Puck Control Time/60",
        p["Puck control time/60"],
        p["Puck control time/60 Percentile"]
    )

# ==================================================
# DEFENSE
# ==================================================

st.markdown("---")

st.subheader("🛡️ Defense")

d1, d2, d3, d4 = st.columns(4)

with d1:

    metric_tile(
        "Takeaways/60",
        p["Takeaways/60"],
        p["Takeaways/60 Percentile"]
    )

with d2:

    metric_tile(
        "DZ Takeaways",
        p["Takeaways in DZ"],
        p["Takeaways in DZ Percentile"]
    )

with d3:

    metric_tile(
        "Opponent xG On-Ice",
        p["Opponent's xG when on ice"],
        p["Opponent's xG when on ice Percentile"]
    )

with d4:

    metric_tile(
        "Puck Losses/60",
        p["Puck losses/60"],
        100 - p["Puck losses/60 Percentile"]
    )

# ==================================================
# IMPACT
# ==================================================

st.markdown("---")

st.subheader("📈 Impact")

i1, i2, i3, i4 = st.columns(4)

with i1:

    metric_tile(
        "Net xG",
        p["Net xG (xG player on - opp. team's xG)"],
        p["Net xG (xG player on - opp. team's xG) Percentile"]
    )

with i2:

    metric_tile(
        "Team xG On-Ice",
        p["Team xG when on ice"],
        p["Team xG when on ice Percentile"]
    )

with i3:

    metric_tile(
        "Overall Score",
        p["Overall Score"],
        p["Overall Score Percentile"]
    )

with i4:

    metric_tile(
        "Impact Score",
        p["Impact Score"],
        p["Impact Score"]
    )
