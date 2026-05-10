import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Player Style Comparison",
    layout="wide"
)

st.title("⚔️ Player Style Comparison")

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

# TEAM 1

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

# PLAYER 1

players1 = sorted(
    filtered_df[
        filtered_df["Team"] == team1
    ]["Player"].dropna().unique()
)

player1 = st.sidebar.selectbox(
    "Player 1",
    players1
)

# PLAYER 2

players2 = sorted(
    filtered_df[
        filtered_df["Team"] == team2
    ]["Player"].dropna().unique()
)

player2 = st.sidebar.selectbox(
    "Player 2",
    players2
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
# HEADER
# ==================================================

h1, h2, h3 = st.columns([5,1,5])

with h1:

    if p1["Team"] in team_logos:

        st.image(
            team_logos[p1["Team"]],
            width=90
        )

    st.markdown(f"## {player1}")
    st.markdown(f"### {p1['Team']} | {p1['Position']}")

    toi_game = p1["Time on ice"] / p1["Games played"]

    st.markdown(
        f"""
        TOI/Game: {round(toi_game,1)} min  
        Points: {int(p1['Points'])}
        """
    )

with h2:

    st.markdown("## VS")

with h3:

    if p2["Team"] in team_logos:

        st.image(
            team_logos[p2["Team"]],
            width=90
        )

    st.markdown(f"## {player2}")
    st.markdown(f"### {p2['Team']} | {p2['Position']}")

    toi_game = p2["Time on ice"] / p2["Games played"]

    st.markdown(
        f"""
        TOI/Game: {round(toi_game,1)} min  
        Points: {int(p2['Points'])}
        """
    )

st.markdown("---")

# ==================================================
# COLOR FUNCTIONS
# ==================================================

def left_color(a, b):

    if a > b:
        return "#1E8E3E"

    elif a < b:
        return "#C62828"

    else:
        return "#4B5563"

def right_color(a, b):

    if b > a:
        return "#1E8E3E"

    elif b < a:
        return "#C62828"

    else:
        return "#4B5563"

# ==================================================
# COMPARISON BOX
# ==================================================

def comparison_box(
    title,
    val1,
    val2,
    pct1,
    pct2
):

    color1 = left_color(pct1, pct2)
    color2 = right_color(pct1, pct2)

    c1, c2, c3 = st.columns([4,2,4])

    with c1:

        html1 = f"""
        <div style="
            background:{color1};
            padding:10px;
            border-radius:8px;
            height:105px;
            color:white;
            font-family:Arial;
        ">

            <div style="
                font-size:12px;
                font-weight:700;
            ">
                {title}
            </div>

            <div style="
                font-size:28px;
                font-weight:800;
                margin-top:6px;
            ">
                {round(val1,2)}
            </div>

            <div style="
                font-size:12px;
                margin-top:4px;
            ">
                {round(pct1)}th percentile
            </div>

        </div>
        """

        components.html(
            html1,
            height=115
        )

    with c2:

        st.markdown("")

    with c3:

        html2 = f"""
        <div style="
            background:{color2};
            padding:10px;
            border-radius:8px;
            height:105px;
            color:white;
            font-family:Arial;
        ">

            <div style="
                font-size:12px;
                font-weight:700;
            ">
                {title}
            </div>

            <div style="
                font-size:28px;
                font-weight:800;
                margin-top:6px;
            ">
                {round(val2,2)}
            </div>

            <div style="
                font-size:12px;
                margin-top:4px;
            ">
                {round(pct2)}th percentile
            </div>

        </div>
        """

        components.html(
            html2,
            height=115
        )

# ==================================================
# SHOOTING
# ==================================================

st.subheader("🔥 Shooting")

shooting_metrics = [

    (
        "Goals/60",
        "Goals/60",
        "Goals/60 Percentile"
    ),

    (
        "Shots/60",
        "Shots/60",
        "Shots/60 Percentile"
    ),

    (
        "xG/60",
        "xG (Expected goals)/60",
        "xG (Expected goals)/60 Percentile"
    ),

    (
        "Scoring Chances/60",
        "Scoring chances - total/60",
        "Scoring chances - total/60 Percentile"
    )

]

for title, stat, pct in shooting_metrics:

    comparison_box(
        title,
        p1[stat],
        p2[stat],
        p1[pct],
        p2[pct]
    )

# ==================================================
# PLAYMAKING
# ==================================================

st.markdown("---")
st.subheader("🎯 Playmaking")

playmaking_metrics = [

    (
        "Pre-Shot Passes/60",
        "Pre-shots passes/60",
        "Pre-shots passes/60 Percentile"
    ),

    (
        "Slot Passes/60",
        "Passes to the slot/60",
        "Passes to the slot/60 Percentile"
    ),

    (
        "First Assists/60",
        "First assist/60",
        "First assist/60 Percentile"
    )

]

for title, stat, pct in playmaking_metrics:

    comparison_box(
        title,
        p1[stat],
        p2[stat],
        p1[pct],
        p2[pct]
    )

# ==================================================
# TRANSITION
# ==================================================

st.markdown("---")
st.subheader("🚀 Transition")

transition_metrics = [

    (
        "Entries Carry/60",
        "Entries via stickhandling/60",
        "Entries via stickhandling/60 Percentile"
    ),

    (
        "Entries Pass/60",
        "Entries via pass/60",
        "Entries via pass/60 Percentile"
    ),

    (
        "Breakouts Carry/60",
        "Breakouts via stickhandling/60",
        "Breakouts via stickhandling/60 Percentile"
    ),

    (
        "Breakouts Pass/60",
        "Breakouts via pass/60",
        "Breakouts via pass/60 Percentile"
    )

]

for title, stat, pct in transition_metrics:

    comparison_box(
        title,
        p1[stat],
        p2[stat],
        p1[pct],
        p2[pct]
    )

# ==================================================
# POSSESSION
# ==================================================

st.markdown("---")
st.subheader("🏒 Possession")

possession_metrics = [

    (
        "Puck Touches/60",
        "Puck touches/60",
        "Puck touches/60 Percentile"
    ),

    (
        "OZ Possession/60",
        "OZ possession/60",
        "OZ possession/60 Percentile"
    )

]

for title, stat, pct in possession_metrics:

    comparison_box(
        title,
        p1[stat],
        p2[stat],
        p1[pct],
        p2[pct]
    )

# ==================================================
# DEFENSE
# ==================================================

st.markdown("---")
st.subheader("🛡️ Defense")

defense_metrics = [

    (
        "Takeaways/60",
        "Takeaways/60",
        "Takeaways/60 Percentile"
    ),

    (
        "DZ Takeaways",
        "Takeaways in DZ",
        "Takeaways in DZ Percentile"
    )

]

for title, stat, pct in defense_metrics:

    comparison_box(
        title,
        p1[stat],
        p2[stat],
        p1[pct],
        p2[pct]
    )

# ==================================================
# IMPACT
# ==================================================

st.markdown("---")
st.subheader("📈 Impact")

impact_metrics = [

    (
        "Net xG",
        "Net xG (xG player on - opp. team's xG)",
        "Net xG (xG player on - opp. team's xG) Percentile"
    ),

    (
        "Overall Score",
        "Overall Score",
        "Overall Score Percentile"
    )

]

for title, stat, pct in impact_metrics:

    comparison_box(
        title,
        p1[stat],
        p2[stat],
        p1[pct],
        p2[pct]
    )
