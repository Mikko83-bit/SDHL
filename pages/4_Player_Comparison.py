import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Player Comparison",
    layout="wide"
)

# ==================================================
# PAGE TITLE
# ==================================================

st.title("🧠 Advanced Player Comparison")

st.markdown(
    "Modern analytics-based player scouting comparison."
)

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
    "Skelleftea": "images/Skelleftea AIK.png"

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
# NUMERIC CONVERSION
# ==================================================

numeric_cols = df.select_dtypes(
    include="number"
).columns

df[numeric_cols] = df[
    numeric_cols
].round(2)

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

# TEAM 2

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
# CATEGORY SCORES
# ==================================================

radar_metrics = [

    "Shooting Score",
    "Playmaking Score",
    "Transition Score",
    "Puck Movement Score",
    "Defense Score",
    "Impact Score"

]

radar_labels = [

    "Shooting",
    "Playmaking",
    "Transition",
    "Puck Movement",
    "Defense",
    "Impact"

]

# ==================================================
# RADAR CHART
# ==================================================

st.subheader("📊 Player Style Radar")

fig = go.Figure()

# PLAYER 1

fig.add_trace(

    go.Scatterpolar(

        r=[p1[m] for m in radar_metrics],

        theta=radar_labels,

        fill='toself',

        name=player1,

        line=dict(
            color='#00E5FF',
            width=4
        ),

        fillcolor='rgba(0,229,255,0.25)'

    )

)

# PLAYER 2

fig.add_trace(

    go.Scatterpolar(

        r=[p2[m] for m in radar_metrics],

        theta=radar_labels,

        fill='toself',

        name=player2,

        line=dict(
            color='#FF5252',
            width=4
        ),

        fillcolor='rgba(255,82,82,0.25)'

    )

)

# ==================================================
# LAYOUT
# ==================================================

fig.update_layout(

    template="plotly_dark",

    polar=dict(

        radialaxis=dict(

            visible=True,

            range=[0, 100],

            gridcolor="gray",

            linecolor="gray"

        )

    ),

    paper_bgcolor="#111111",

    plot_bgcolor="#111111",

    font=dict(
        color="white"
    ),

    height=750

)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==================================================
# PLAYER HEADER CARDS
# ==================================================

st.markdown("---")

card1, card2 = st.columns(2)

# ==================================================
# PLAYER 1
# ==================================================

with card1:

    if p1["Team"] in team_logos:

        st.image(
            team_logos[p1["Team"]],
            width=100
        )

    st.markdown(
        f"## {player1}"
    )

    st.markdown(
        f"### {p1['Team']} | {p1['Position']}"
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Overall Score",
            round(p1["Overall Score"],1)
        )

    with c2:

        st.metric(
            "League Percentile",
            round(p1["Overall Score Percentile"])
        )

    with c3:

        st.metric(
            "TOI",
            round(p1["Time on ice"],1)
        )

# ==================================================
# PLAYER 2
# ==================================================

with card2:

    if p2["Team"] in team_logos:

        st.image(
            team_logos[p2["Team"]],
            width=100
        )

    st.markdown(
        f"## {player2}"
    )

    st.markdown(
        f"### {p2['Team']} | {p2['Position']}"
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Overall Score",
            round(p2["Overall Score"],1)
        )

    with c2:

        st.metric(
            "League Percentile",
            round(p2["Overall Score Percentile"])
        )

    with c3:

        st.metric(
            "TOI",
            round(p2["Time on ice"],1)
        )

# ==================================================
# LEAGUE RANK FUNCTION
# ==================================================

def get_rank(player_name, metric):

    temp_df = filtered_df.sort_values(
        by=metric,
        ascending=False
    ).reset_index(drop=True)

    rank = temp_df[
        temp_df["Player"] == player_name
    ].index[0] + 1

    return rank

# ==================================================
# COMPARISON METRICS
# ==================================================

comparison_metrics = [

    ("Goals/60", "Goals/60"),
    ("Assists/60", "Assists/60"),
    ("xG/60", "xG (Expected goals)/60"),
    ("Shots/60", "Shots/60"),
    ("Entries Carry/60", "Entries via stickhandling/60"),
    ("Entries Pass/60", "Entries via pass/60"),
    ("Breakouts/60", "Breakouts/60"),
    ("Slot Passes/60", "Passes to the slot/60"),
    ("Pre-Shot Passes/60", "Pre-shots passes/60"),
    ("Puck Touches/60", "Puck touches/60"),
    ("Takeaways/60", "Takeaways/60"),
    ("Net xG", "Net xG (xG player on - opp. team's xG)")

]

# ==================================================
# COMPARISON TABLE
# ==================================================

st.markdown("---")

st.subheader("📈 Advanced Comparison")

for metric_name, col_name in comparison_metrics:

    value1 = round(float(p1[col_name]),2)
    value2 = round(float(p2[col_name]),2)

    rank1 = get_rank(player1, col_name)
    rank2 = get_rank(player2, col_name)

    percentile_col = f"{col_name} Percentile"

    percentile1 = 0
    percentile2 = 0

    if percentile_col in df.columns:

        percentile1 = round(
            float(p1[percentile_col])
        )

        percentile2 = round(
            float(p2[percentile_col])
        )

    # COLORS

    if value1 > value2:

        color1 = "#16A34A"
        color2 = "#DC2626"

    elif value2 > value1:

        color1 = "#DC2626"
        color2 = "#16A34A"

    else:

        color1 = "#374151"
        color2 = "#374151"

    c1, c2, c3 = st.columns([1.2,2,2])

    # ==================================================
    # METRIC
    # ==================================================

    with c1:

        st.markdown(

            f"""
<div style="
background:#0F172A;
border-radius:12px;
height:110px;
display:flex;
justify-content:center;
align-items:center;
font-size:18px;
font-weight:700;
color:white;
margin-bottom:10px;
text-align:center;
padding:8px;
">
{metric_name}
</div>
""",

            unsafe_allow_html=True

        )

    # ==================================================
    # PLAYER 1
    # ==================================================

    with c2:

        st.markdown(

            f"""
<div style="
background:{color1};
border-radius:12px;
padding:12px;
height:110px;
margin-bottom:10px;
">

<div style="
font-size:13px;
color:white;
font-weight:700;
">
{player1}
</div>

<div style="
font-size:30px;
font-weight:800;
color:white;
line-height:1;
margin-top:6px;
">
{value1}
</div>

<div style="
font-size:12px;
color:white;
margin-top:6px;
">
{percentile1}th percentile
</div>

<div style="
font-size:12px;
color:white;
">
#{rank1} among {selected_position}
</div>

</div>
""",

            unsafe_allow_html=True

        )

    # ==================================================
    # PLAYER 2
    # ==================================================

    with c3:

        st.markdown(

            f"""
<div style="
background:{color2};
border-radius:12px;
padding:12px;
height:110px;
margin-bottom:10px;
">

<div style="
font-size:13px;
color:white;
font-weight:700;
">
{player2}
</div>

<div style="
font-size:30px;
font-weight:800;
color:white;
line-height:1;
margin-top:6px;
">
{value2}
</div>

<div style="
font-size:12px;
color:white;
margin-top:6px;
">
{percentile2}th percentile
</div>

<div style="
font-size:12px;
color:white;
">
#{rank2} among {selected_position}
</div>

</div>
""",

            unsafe_allow_html=True

        )
