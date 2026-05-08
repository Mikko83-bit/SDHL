import streamlit as st
import pandas as pd

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Scouting Report",
    layout="wide"
)

st.title("📝 Scouting Report")

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
# RECALCULATE PUCK MOVEMENT SCORE
# ==================================================

puck_metrics = [

    "Breakouts via pass/60",
    "Breakouts via stickhandling/60",
    "Puck touches/60",
    "OZ possession/60"

]

for stat in puck_metrics:

    percentile_col = f"{stat} Percentile"

    df[percentile_col] = (

        df.groupby("Position")[stat]
        .rank(pct=True) * 100

    )

df["Puck Movement Score"] = (

    df[
        [f"{x} Percentile" for x in puck_metrics]
    ].mean(axis=1)

)

# ==================================================
# POSITION-SPECIFIC OVERALL SCORE
# ==================================================

df["Overall Score"] = 0.0

# FORWARDS

forward_mask = df["Position"] == "F"

df.loc[forward_mask, "Overall Score"] = (

    df.loc[forward_mask, "Shooting Score"] * 0.25 +

    df.loc[forward_mask, "Playmaking Score"] * 0.25 +

    df.loc[forward_mask, "Transition Score"] * 0.25 +

    df.loc[forward_mask, "Puck Movement Score"] * 0.10 +

    df.loc[forward_mask, "Defense Score"] * 0.05 +

    df.loc[forward_mask, "Impact Score"] * 0.10

)

# DEFENSEMEN

defense_mask = df["Position"] == "D"

df.loc[defense_mask, "Overall Score"] = (

    df.loc[defense_mask, "Shooting Score"] * 0.10 +

    df.loc[defense_mask, "Playmaking Score"] * 0.15 +

    df.loc[defense_mask, "Transition Score"] * 0.25 +

    df.loc[defense_mask, "Puck Movement Score"] * 0.25 +

    df.loc[defense_mask, "Defense Score"] * 0.15 +

    df.loc[defense_mask, "Impact Score"] * 0.10

)

# ==================================================
# OVERALL PERCENTILE
# ==================================================

df["Overall Percentile"] = (

    df.groupby("Position")[
        "Overall Score"
    ].rank(pct=True) * 100

)

# ==================================================
# ROUND VALUES
# ==================================================

numeric_cols = df.select_dtypes(
    include="number"
).columns

df[numeric_cols] = df[numeric_cols].round(1)

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
# PLAYER
# ==================================================

p = filtered_df[
    filtered_df["Player"] == selected_player
].iloc[0]

# ==================================================
# PLAYER OVERVIEW
# ==================================================

st.subheader("🏒 Player Overview")

col1, col2 = st.columns([1,3])

# ==================================================
# LEFT SIDE
# ==================================================

with col1:

    if p["Team"] in team_logos:

        st.image(
            team_logos[p["Team"]],
            width=120
        )

# ==================================================
# RIGHT SIDE
# ==================================================

with col2:

    st.markdown(
        f"## {selected_player}"
    )

    st.markdown(
        f"### {p['Team']} | {p['Position']}"
    )

    st.markdown("---")

    st.markdown(
        f"### Overall Score: {p['Overall Score']}"
    )

    st.markdown(
        f"### League Percentile: {int(round(p['Overall Percentile']))}th"
    )

# ==================================================
# ROLE DETECTION
# ==================================================

role = "Balanced Player"

if (
    p["Transition Score"] >= 75
    and
    p["Playmaking Score"] >= 65
):

    role = "Transition Playmaker"

elif (
    p["Shooting Score"] >= 75
):

    role = "Finishing Forward"

elif (
    p["Defense Score"] >= 75
    and
    p["Impact Score"] >= 70
):

    role = "Two-Way Player"

elif (
    p["Puck Movement Score"] >= 75
):

    role = "Puck Moving Defender"

elif (
    p["Playmaking Score"] >= 75
):

    role = "Offensive Playmaker"

st.markdown(
    f"### Role: {role}"
)

# ==================================================
# STRENGTHS & WEAKNESSES
# ==================================================

st.markdown("---")

strength_col, weakness_col = st.columns(2)

# ==================================================
# STRENGTHS
# ==================================================

with strength_col:

    st.subheader("✅ Strengths")

    strengths = []

    if p["Transition Score"] >= 80:

        strengths.append(
            "Elite transition ability"
        )

    elif p["Transition Score"] >= 65:

        strengths.append(
            "Strong transition game"
        )

    if p["Puck Movement Score"] >= 80:

        strengths.append(
            "Excellent puck movement under pressure"
        )

    elif p["Puck Movement Score"] >= 65:

        strengths.append(
            "Reliable puck moving ability"
        )

    if p["Playmaking Score"] >= 80:

        strengths.append(
            "Elite offensive playmaking"
        )

    elif p["Playmaking Score"] >= 65:

        strengths.append(
            "Strong offensive creation"
        )

    if p["Shooting Score"] >= 80:

        strengths.append(
            "High-end finishing ability"
        )

    elif p["Shooting Score"] >= 65:

        strengths.append(
            "Consistent scoring threat"
        )

    if p["Defense Score"] >= 80:

        strengths.append(
            "Excellent defensive impact"
        )

    elif p["Defense Score"] >= 65:

        strengths.append(
            "Reliable defensive play"
        )

    if p["Impact Score"] >= 80:

        strengths.append(
            "Drives positive overall team impact"
        )

    elif p["Impact Score"] >= 65:

        strengths.append(
            "Positive on-ice impact profile"
        )

    if len(strengths) == 0:

        strengths.append(
            "No clearly elite strengths identified."
        )

    for item in strengths:

        st.markdown(f"• {item}")

# ==================================================
# WEAKNESSES
# ==================================================

with weakness_col:

    st.subheader("❌ Weaknesses")

    weaknesses = []

    if p["Transition Score"] <= 35:

        weaknesses.append(
            "Limited transition impact"
        )

    if p["Puck Movement Score"] <= 35:

        weaknesses.append(
            "Limited puck moving ability"
        )

    if p["Playmaking Score"] <= 35:

        weaknesses.append(
            "Limited offensive creation"
        )

    if p["Shooting Score"] <= 35:

        weaknesses.append(
            "Below average finishing ability"
        )

    if p["Defense Score"] <= 35:

        weaknesses.append(
            "Below average defensive impact"
        )

    if p["Impact Score"] <= 35:

        weaknesses.append(
            "Limited positive on-ice impact"
        )

    if len(weaknesses) == 0:

        weaknesses.append(
            "No major statistical weaknesses identified."
        )

    for item in weaknesses:

        st.markdown(f"• {item}")
