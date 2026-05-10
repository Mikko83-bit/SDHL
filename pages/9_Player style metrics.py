import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

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
# LEAGUE RANK FUNCTION
# ==================================================

def get_rank(column_name):

    rank_df = filtered_df[
        ["Player", column_name]
    ].copy()

    rank_df = rank_df.sort_values(
        by=column_name,
        ascending=False
    ).reset_index(drop=True)

    rank_df["Rank"] = rank_df.index + 1

    player_rank = rank_df[
        rank_df["Player"] == selected_player
    ]["Rank"].iloc[0]

    return int(player_rank)

# ==================================================
# METRIC BOX
# ==================================================

def metric_box(title, value, percentile, rank):

    if pd.isna(value):
        value = 0

    if pd.isna(percentile):
        percentile = 0

    color = percentile_color(percentile)

    html = f"""
    <div style="
        background:{color};
        padding:8px;
        border-radius:8px;
        height:120px;
        font-family:Arial;
        color:white;
        display:flex;
        flex-direction:column;
        justify-content:center;
    ">

        <div style="
            font-size:11px;
            font-weight:700;
        ">
            {title}
        </div>

        <div style="
            font-size:24px;
            font-weight:800;
            margin-top:4px;
        ">
            {round(value,2)}
        </div>

        <div style="
            font-size:11px;
            margin-top:4px;
        ">
            {round(percentile)}th percentile
        </div>

        <div style="
            font-size:11px;
            margin-top:2px;
            font-weight:700;
        ">
            #{rank} among {selected_position}s
        </div>

    </div>
    """

    components.html(
        html,
        height=130
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
        p["Goals/60 Percentile"],
        get_rank("Goals/60")
    )

with s2:

    metric_box(
        "Shots/60",
        p["Shots/60"],
        p["Shots/60 Percentile"],
        get_rank("Shots/60")
    )

with s3:

    metric_box(
        "xG/60",
        p["xG (Expected goals)/60"],
        p["xG (Expected goals)/60 Percentile"],
        get_rank("xG (Expected goals)/60")
    )

with s4:

    metric_box(
        "Inner Slot Shots/60",
        p["Inner slot shots - total/60"],
        p["Inner slot shots - total/60 Percentile"],
        get_rank("Inner slot shots - total/60")
    )

with s5:

    metric_box(
        "Scoring Chances/60",
        p["Scoring chances - total/60"],
        p["Scoring chances - total/60 Percentile"],
        get_rank("Scoring chances - total/60")
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
        p["Pre-shots passes/60 Percentile"],
        get_rank("Pre-shots passes/60")
    )

with p2:

    metric_box(
        "Slot Passes/60",
        p["Passes to the slot/60"],
        p["Passes to the slot/60 Percentile"],
        get_rank("Passes to the slot/60")
    )

with p3:

    metric_box(
        "First Assists/60",
        p["First assist/60"],
        p["First assist/60 Percentile"],
        get_rank("First assist/60")
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
        p["Entries via stickhandling/60 Percentile"],
        get_rank("Entries via stickhandling/60")
    )

with t2:

    metric_box(
        "Entries Pass/60",
        p["Entries via pass/60"],
        p["Entries via pass/60 Percentile"],
        get_rank("Entries via pass/60")
    )

with t3:

    metric_box(
        "Breakouts Carry/60",
        p["Breakouts via stickhandling/60"],
        p["Breakouts via stickhandling/60 Percentile"],
        get_rank("Breakouts via stickhandling/60")
    )

with t4:

    metric_box(
        "Breakouts Pass/60",
        p["Breakouts via pass/60"],
        p["Breakouts via pass/60 Percentile"],
        get_rank("Breakouts via pass/60")
    )

with t5:

    metric_box(
        "Breakouts/60",
        p["Breakouts/60"],
        p["Breakouts/60 Percentile"],
        get_rank("Breakouts/60")
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
        p["Puck touches/60 Percentile"],
        get_rank("Puck touches/60")
    )

with o2:

    metric_box(
        "OZ Possession/60",
        p["OZ possession/60"],
        p["OZ possession/60 Percentile"],
        get_rank("OZ possession/60")
    )

# ==================================================
# DEFENSE
# ==================================================

st.markdown("---")

st.subheader("🛡️ Defense")

d1, d2, d3 = st.columns(3)

with d1:

    metric_box(
        "Takeaways/60",
        p["Takeaways/60"],
        p["Takeaways/60 Percentile"],
        get_rank("Takeaways/60")
    )

with d2:

    metric_box(
        "DZ Takeaways",
        p["Takeaways in DZ"],
        p["Takeaways in DZ Percentile"],
        get_rank("Takeaways in DZ")
    )

with d3:

    metric_box(
        "Opponent xG",
        p["Opponent's xG when on ice"],
        p["Opponent's xG when on ice Percentile"],
        get_rank("Opponent's xG when on ice")
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
        p["Net xG (xG player on - opp. team's xG) Percentile"],
        get_rank("Net xG (xG player on - opp. team's xG)")
    )

with i2:

    metric_box(
        "Team xG On-Ice",
        p["Team xG when on ice"],
        p["Team xG when on ice Percentile"],
        get_rank("Team xG when on ice")
    )

with i3:

    metric_box(
        "Overall Score",
        p["Overall Score"],
        p["Overall Score Percentile"],
        get_rank("Overall Score")
    )
