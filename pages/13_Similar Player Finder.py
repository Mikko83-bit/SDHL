import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Similar Player Finder",
    layout="wide"
)

# ==================================================
# TITLE
# ==================================================

st.title("🧬 Similar Player Finder")

st.markdown(
    "Find the most stylistically similar players using advanced analytics profiles."
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
# SIMILARITY METRICS
# ==================================================

similarity_metrics = [

    "Shooting Score",
    "Playmaking Score",
    "Transition Score",
    "Puck Movement Score",
    "Defense Score",
    "Impact Score"

]

# ==================================================
# NUMERIC CLEAN
# ==================================================

for col in similarity_metrics:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

df = df.dropna(
    subset=similarity_metrics
)

# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.header("Filters")

# POSITION

positions = sorted(
    df["Position"].unique()
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
    filtered_df["Team"].unique()
)

selected_team = st.sidebar.selectbox(
    "Team",
    teams
)

# PLAYER

players = sorted(

    filtered_df[
        filtered_df["Team"] == selected_team
    ]["Player"].unique()

)

selected_player = st.sidebar.selectbox(
    "Player",
    players
)

# ==================================================
# PLAYER ROW
# ==================================================

player_row = filtered_df[
    filtered_df["Player"] == selected_player
].iloc[0]

# ==================================================
# PLAYER HEADER
# ==================================================

col1, col2 = st.columns([1,4])

with col1:

    if player_row["Team"] in team_logos:

        st.image(
            team_logos[player_row["Team"]],
            width=110
        )

with col2:

    st.markdown(
        f"## {selected_player}"
    )

    st.markdown(
        f"### {player_row['Team']} | {player_row['Position']}"
    )

    m1, m2, m3 = st.columns(3)

    with m1:

        st.metric(
            "Overall Score",
            round(player_row["Overall Score"],1)
        )

    with m2:

        st.metric(
            "League Percentile",
            round(player_row["Overall Score Percentile"])
        )

    with m3:

        st.metric(
            "TOI",
            round(player_row["Time on ice"],1)
        )

# ==================================================
# COSINE SIMILARITY
# ==================================================

metric_matrix = filtered_df[
    similarity_metrics
].values

similarity_matrix = cosine_similarity(
    metric_matrix
)

player_index = filtered_df[
    filtered_df["Player"] == selected_player
].index[0]

real_position = filtered_df.index.get_loc(
    player_index
)

similarities = similarity_matrix[
    real_position
]

# ==================================================
# SIMILARITY DF
# ==================================================

similarity_df = filtered_df.copy()

similarity_df["Similarity"] = similarities

similarity_df = similarity_df[
    similarity_df["Player"] != selected_player
]

similarity_df = similarity_df.sort_values(

    by="Similarity",

    ascending=False

)

top_matches = similarity_df.head(5)

# ==================================================
# TOP MATCHES
# ==================================================

st.markdown("---")

st.subheader("🧬 Most Similar Players")

# ==================================================
# MATCH CARDS
# ==================================================

for i, (_, row) in enumerate(top_matches.iterrows(), start=1):

    similarity_pct = round(
        row["Similarity"] * 100,
        1
    )

    c1, c2 = st.columns([1,5])

    # ==================================================
    # LOGO
    # ==================================================

    with c1:

        if row["Team"] in team_logos:

            st.image(
                team_logos[row["Team"]],
                width=85
            )

    # ==================================================
    # PLAYER CARD
    # ==================================================

    with c2:

        st.markdown(

            f"""
<div style="
background:#111827;
padding:18px;
border-radius:14px;
margin-bottom:12px;
">

<div style="
font-size:24px;
font-weight:800;
color:white;
">
#{i} {row['Player']}
</div>

<div style="
font-size:15px;
color:#D1D5DB;
margin-top:2px;
">
{row['Team']} | {row['Position']}
</div>

<div style="
font-size:18px;
font-weight:700;
color:#00E5FF;
margin-top:12px;
">
{similarity_pct}% Similar
</div>

<div style="
margin-top:10px;
font-size:14px;
color:white;
">

• Shooting: {round(row['Shooting Score'],1)}<br>
• Playmaking: {round(row['Playmaking Score'],1)}<br>
• Transition: {round(row['Transition Score'],1)}<br>
• Puck Movement: {round(row['Puck Movement Score'],1)}<br>
• Defense: {round(row['Defense Score'],1)}<br>
• Impact: {round(row['Impact Score'],1)}

</div>

</div>
""",

            unsafe_allow_html=True

        )

# ==================================================
# PROFILE COMPARISON TABLE
# ==================================================

st.markdown("---")

st.subheader("📊 Profile Comparison")

comparison_cols = [

    "Player",

    "Shooting Score",
    "Playmaking Score",
    "Transition Score",
    "Puck Movement Score",
    "Defense Score",
    "Impact Score",
    "Overall Score"

]

display_df = pd.concat([

    filtered_df[
        filtered_df["Player"] == selected_player
    ][comparison_cols],

    top_matches[
        comparison_cols
    ]

])

st.dataframe(

    display_df,

    use_container_width=True,

    hide_index=True,

    height=350

)

# ==================================================
# PLAYER ARCHETYPE
# ==================================================

st.markdown("---")

st.subheader("🧠 Player Archetype")

archetype = "Balanced Player"

# ==================================================
# ARCHETYPE LOGIC
# ==================================================

if (

    player_row["Transition Score"] >= 80

    and

    player_row["Playmaking Score"] >= 75

):

    archetype = "Transition Playmaker"

elif (

    player_row["Shooting Score"] >= 85

):

    archetype = "Elite Finisher"

elif (

    player_row["Defense Score"] >= 75

    and

    player_row["Impact Score"] >= 75

):

    archetype = "Two-Way Impact Player"

elif (

    player_row["Puck Movement Score"] >= 80

):

    archetype = "Puck Possession Driver"

elif (

    player_row["Playmaking Score"] >= 85

):

    archetype = "Offensive Playmaker"

st.info(
    archetype
)
