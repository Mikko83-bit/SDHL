import streamlit as st
import pandas as pd
import numpy as np

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
    """
Find players with a similar STYLE profile.

This model compares:
- shooting tendencies
- playmaking profile
- transition impact
- puck movement
- defensive style
- overall impact

while also adjusting for overall player quality.
"""
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
# CLEAN
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
# METRICS USED
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
# NUMERIC
# ==================================================

for col in similarity_metrics + ["Overall Score"]:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

df = df.dropna(
    subset=similarity_metrics
)

# ==================================================
# ROUNDING
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

teams = sorted(
    filtered_df["Team"].dropna().unique()
)

selected_team = st.sidebar.selectbox(
    "Team",
    teams
)

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

player_row = filtered_df[
    filtered_df["Player"] == selected_player
].iloc[0]

# ==================================================
# PLAYER HEADER
# ==================================================

c1, c2 = st.columns([1,4])

with c1:

    if player_row["Team"] in team_logos:

        st.image(
            team_logos[player_row["Team"]],
            width=110
        )

with c2:

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
            "Percentile",
            round(player_row["Overall Score Percentile"])
        )

    with m3:

        st.metric(
            "TOI",
            round(player_row["Time on ice"],1)
        )

# ==================================================
# STYLE PROFILE
# ==================================================

style_df = filtered_df.copy()

# ==================================================
# CONVERT TO STYLE SHAPE
# ==================================================

style_vectors = []

for _, row in style_df.iterrows():

    values = np.array([

        row["Shooting Score"],
        row["Playmaking Score"],
        row["Transition Score"],
        row["Puck Movement Score"],
        row["Defense Score"],
        row["Impact Score"]

    ])

    # PREVENT DIV BY ZERO

    total = values.sum()

    if total == 0:

        normalized = np.zeros(len(values))

    else:

        normalized = values / total

    style_vectors.append(normalized)

style_matrix = np.array(style_vectors)

# ==================================================
# COSINE SIMILARITY
# ==================================================

norms = np.linalg.norm(
    style_matrix,
    axis=1,
    keepdims=True
)

normalized_matrix = (
    style_matrix / norms
)

similarity_matrix = np.dot(
    normalized_matrix,
    normalized_matrix.T
)

# ==================================================
# PLAYER INDEX
# ==================================================

player_idx = style_df.index[
    style_df["Player"] == selected_player
][0]

matrix_idx = style_df.index.get_loc(
    player_idx
)

similarities = similarity_matrix[
    matrix_idx
]

# ==================================================
# ADD SIMILARITY
# ==================================================

style_df["Style Similarity"] = similarities

# ==================================================
# OVERALL SCORE DIFFERENCE PENALTY
# ==================================================

selected_overall = player_row[
    "Overall Score"
]

style_df["Overall Difference"] = abs(

    style_df["Overall Score"]
    -
    selected_overall

)

# ==================================================
# FINAL HYBRID SCORE
# ==================================================

style_df["Final Similarity"] = (

    style_df["Style Similarity"] * 0.75

    +

    (
        1
        -
        (
            style_df["Overall Difference"]
            / 100
        )
    ) * 0.25

)

# ==================================================
# REMOVE SAME PLAYER
# ==================================================

style_df = style_df[
    style_df["Player"] != selected_player
]

# ==================================================
# SORT
# ==================================================

style_df = style_df.sort_values(

    by="Final Similarity",

    ascending=False

)

top_matches = style_df.head(5)

# ==================================================
# SECTION
# ==================================================

st.markdown("---")

st.subheader("🧬 Most Similar Player Profiles")

# ==================================================
# PLAYER CARDS
# ==================================================

for i, (_, row) in enumerate(top_matches.iterrows(), start=1):

    similarity_pct = round(
        row["Final Similarity"] * 100,
        1
    )

    left, right = st.columns([1,5])

    # ==================================================
    # LOGO
    # ==================================================

    with left:

        if row["Team"] in team_logos:

            st.image(
                team_logos[row["Team"]],
                width=90
            )

    # ==================================================
    # CARD
    # ==================================================

    with right:

        st.markdown(

            f"""
<div style="
background:#111827;
padding:18px;
border-radius:14px;
margin-bottom:14px;
border:1px solid #1F2937;
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
{similarity_pct}% Profile Match
</div>

<div style="
margin-top:10px;
font-size:14px;
color:white;
line-height:1.8;
">

• Shooting: {round(row['Shooting Score'],1)}<br>
• Playmaking: {round(row['Playmaking Score'],1)}<br>
• Transition: {round(row['Transition Score'],1)}<br>
• Puck Movement: {round(row['Puck Movement Score'],1)}<br>
• Defense: {round(row['Defense Score'],1)}<br>
• Impact: {round(row['Impact Score'],1)}<br>
• Overall Score: {round(row['Overall Score'],1)}

</div>

</div>
""",

            unsafe_allow_html=True

        )

# ==================================================
# PROFILE TABLE
# ==================================================

st.markdown("---")

st.subheader("📊 Style Profile Comparison")

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

comparison_df = pd.concat([

    style_df[
        style_df["Player"] == selected_player
    ][comparison_cols],

    top_matches[
        comparison_cols
    ]

])

st.dataframe(

    comparison_df,

    use_container_width=True,

    hide_index=True,

    height=350

)

# ==================================================
# ARCHETYPE
# ==================================================

st.markdown("---")

st.subheader("🧠 Player Archetype")

archetype = "Balanced Player"

if (

    player_row["Transition Score"] >= 80

    and

    player_row["Playmaking Score"] >= 75

):

    archetype = "Transition Playmaker"

elif (

    player_row["Shooting Score"] >= 90

):

    archetype = "Elite Goal Scorer"

elif (

    player_row["Defense Score"] >= 75

    and

    player_row["Impact Score"] >= 75

):

    archetype = "Two-Way Impact Player"

elif (

    player_row["Puck Movement Score"] >= 85

):

    archetype = "Possession Driver"

elif (

    player_row["Playmaking Score"] >= 85

):

    archetype = "Elite Playmaker"

st.info(archetype)
