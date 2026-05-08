import streamlit as st
import pandas as pd

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Scouting Report",
    layout="wide"
)

st.title("📝 Advanced Scouting Report")

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

forward_mask = df["Position"] == "F"

df.loc[forward_mask, "Overall Score"] = (

    df.loc[forward_mask, "Shooting Score"] * 0.25 +

    df.loc[forward_mask, "Playmaking Score"] * 0.25 +

    df.loc[forward_mask, "Transition Score"] * 0.25 +

    df.loc[forward_mask, "Puck Movement Score"] * 0.10 +

    df.loc[forward_mask, "Defense Score"] * 0.05 +

    df.loc[forward_mask, "Impact Score"] * 0.10

)

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

with col1:

    if p["Team"] in team_logos:

        st.image(
            team_logos[p["Team"]],
            width=120
        )

with col2:

    st.markdown(f"## {selected_player}")

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
# PLAYER IDENTITY ENGINE
# ==================================================

roles = []

# TRANSITION CARRIER

if (

    p["Entries via stickhandling/60 Percentile"] >= 80
    and
    p["Breakouts via stickhandling/60 Percentile"] >= 70

):

    roles.append(
        "Transition Carrier"
    )

# PLAYMAKER

if (

    p["Pre-shots passes/60 Percentile"] >= 75
    and
    p["First assist/60 Percentile"] >= 75

):

    roles.append(
        "Offensive Playmaker"
    )

# FINISHER

if (

    p["Goals/60 Percentile"] >= 80
    and
    p["xG (Expected goals)/60 Percentile"] >= 75

):

    roles.append(
        "Finishing Threat"
    )

# POSSESSION DRIVER

if (

    p["OZ possession/60 Percentile"] >= 80
    and
    p["Puck touches/60 Percentile"] >= 75

):

    roles.append(
        "Possession Driver"
    )

# PUCK MOVING DEFENDER

if (

    p["Puck Movement Score"] >= 75
    and
    p["Breakouts via pass/60 Percentile"] >= 75

):

    roles.append(
        "Puck Moving Defender"
    )

# TWO-WAY DRIVER

if (

    p["Impact Score"] >= 75
    and
    p["Defense Score"] >= 65
    and
    p["Transition Score"] >= 65

):

    roles.append(
        "Two-Way Driver"
    )

# DEFENSIVE DISRUPTOR

if (

    p["Takeaways/60 Percentile"] >= 80
    and
    p["Opponent's xG when on ice Percentile"] >= 70

):

    roles.append(
        "Defensive Disruptor"
    )

# DEFAULT

if len(roles) == 0:

    roles.append(
        "Balanced Player"
    )

# ==================================================
# DISPLAY ROLES
# ==================================================

st.markdown("### 🧬 Player Identity")

for role in roles:

    st.markdown(f"• {role}")

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

    # TRANSITION

    if p["Entries via stickhandling/60 Percentile"] >= 85:

        strengths.append(
            "Elite puck carrying transition ability"
        )

    if p["Breakouts via pass/60 Percentile"] >= 80:

        strengths.append(
            "High-end passing breakout ability"
        )

    # POSSESSION

    if p["OZ possession/60 Percentile"] >= 80:

        strengths.append(
            "Excellent offensive zone possession impact"
        )

    if p["Puck touches/60 Percentile"] >= 80:

        strengths.append(
            "Highly active puck involvement profile"
        )

    # PLAYMAKING

    if p["Pre-shots passes/60 Percentile"] >= 80:

        strengths.append(
            "Elite pre-shot passing creation"
        )

    if p["Passes to the slot/60 Percentile"] >= 80:

        strengths.append(
            "Creates dangerous slot passing opportunities"
        )

    # SHOOTING

    if p["Goals/60 Percentile"] >= 80:

        strengths.append(
            "Strong finishing ability"
        )

    if p["xG (Expected goals)/60 Percentile"] >= 80:

        strengths.append(
            "Consistently attacks dangerous scoring areas"
        )

    # DEFENSE

    if p["Takeaways/60 Percentile"] >= 80:

        strengths.append(
            "Strong defensive puck disruption"
        )

    if p["Defense Score"] >= 75:

        strengths.append(
            "Reliable defensive impact profile"
        )

    # IMPACT

    if p["Impact Score"] >= 80:

        strengths.append(
            "Drives strong positive on-ice impact"
        )

    if len(strengths) == 0:

        strengths.append(
            "No major standout strengths statistically identified."
        )

    for item in strengths:

        st.markdown(f"• {item}")

# ==================================================
# WEAKNESSES
# ==================================================

with weakness_col:

    st.subheader("❌ Weaknesses")

    weaknesses = []

    # TRANSITION

    if p["Transition Score"] <= 35:

        weaknesses.append(
            "Limited transition involvement"
        )

    if p["Breakouts via stickhandling/60 Percentile"] <= 30:

        weaknesses.append(
            "Limited puck carrying breakout ability"
        )

    # PLAYMAKING

    if p["Pre-shots passes/60 Percentile"] <= 30:

        weaknesses.append(
            "Limited offensive chance creation"
        )

    # SHOOTING

    if p["Goals/60 Percentile"] <= 30:

        weaknesses.append(
            "Below average finishing production"
        )

    if p["xG (Expected goals)/60 Percentile"] <= 30:

        weaknesses.append(
            "Does not consistently generate dangerous scoring chances"
        )

    # DEFENSE

    if p["Defense Score"] <= 35:

        weaknesses.append(
            "Limited defensive impact"
        )

    if p["Takeaways/60 Percentile"] <= 30:

        weaknesses.append(
            "Low defensive puck disruption rates"
        )

    # IMPACT

    if p["Impact Score"] <= 35:

        weaknesses.append(
            "Limited positive overall on-ice impact"
        )

    if len(weaknesses) == 0:

        weaknesses.append(
            "No major statistical weaknesses identified."
        )

    for item in weaknesses:

        st.markdown(f"• {item}")
