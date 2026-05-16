import streamlit as st
import pandas as pd
import numpy as np

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Market Discovery",
    layout="wide"
)

st.title("🔎 Market Discovery")

st.markdown("""
Analytics scouting dashboard for:

- 🚀 Breakout Candidates
- 💎 Hidden Gems
- ⚠️ Regression Risks
- 🧠 Market Inefficiencies
""")

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
# CREATE AGE
# ==================================================

df["Date of birth"] = pd.to_datetime(
    df["Date of birth"],
    errors="coerce"
)

current_year = 2026

df["Age"] = (

    current_year

    -

    df["Date of birth"].dt.year

)

# ==================================================
# CREATE POINTS/60
# ==================================================

if "Points/60" not in df.columns:

    df["Points/60"] = (

        df["Goals/60"]

        +

        df["Assists/60"]

    )

# ==================================================
# NUMERIC CONVERSION
# ==================================================

numeric_cols = [

    "Age",
    "Time on ice",
    "Games played",

    "Goals",
    "Assists",
    "Points",

    "Goals/60",
    "Assists/60",
    "Points/60",

    "Shots/60",
    "xG (Expected goals)/60",

    "Scoring chances - total/60",

    "Shooting Score",
    "Playmaking Score",
    "Transition Score",
    "Puck Movement Score",
    "Defense Score",
    "Impact Score",

    "Overall Score",

    "Net xG (xG player on - opp. team's xG)",

    "xG (Expected goals)"

]

for col in numeric_cols:

    if col in df.columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

# ==================================================
# ROUNDING
# ==================================================

number_cols = df.select_dtypes(
    include="number"
).columns

df[number_cols] = df[
    number_cols
].round(2)

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

# MIN TOI

min_toi = st.sidebar.slider(
    "Minimum TOI",
    min_value=0,
    max_value=1200,
    value=250,
    step=25
)

filtered_df = filtered_df[
    filtered_df["Time on ice"] >= min_toi
]

# AGE FILTER

min_age, max_age = st.sidebar.slider(
    "Age Range",
    min_value=15,
    max_value=45,
    value=(18, 30)
)

filtered_df = filtered_df[

    (filtered_df["Age"] >= min_age)

    &

    (filtered_df["Age"] <= max_age)

]

# ==================================================
# PERCENTILE METRICS
# ==================================================

percentile_metrics = [

    "Goals/60",
    "Points/60",

    "Shots/60",
    "xG (Expected goals)/60",
    "Scoring chances - total/60",

    "Shooting Score",
    "Playmaking Score",
    "Transition Score",
    "Puck Movement Score",
    "Defense Score",
    "Impact Score",

    "Overall Score"

]

# KEEP ONLY EXISTING

percentile_metrics = [

    m for m in percentile_metrics

    if m in filtered_df.columns

]

# ==================================================
# CREATE PERCENTILES
# ==================================================

for metric in percentile_metrics:

    filtered_df[f"{metric} Percentile"] = (

        filtered_df[metric]
        .rank(pct=True)

        * 100

    ).round(1)

# ==================================================
# UNDERLYING SCORE
# ==================================================

filtered_df["Underlying Score"] = (

    filtered_df[
        "xG (Expected goals)/60 Percentile"
    ] * 0.25

    +

    filtered_df[
        "Shots/60 Percentile"
    ] * 0.25

    +

    filtered_df[
        "Scoring chances - total/60 Percentile"
    ] * 0.20

    +

    filtered_df[
        "Transition Score Percentile"
    ] * 0.15

    +

    filtered_df[
        "Impact Score Percentile"
    ] * 0.15

).round(2)

# ==================================================
# PRODUCTION SCORE
# ==================================================

filtered_df["Production Score"] = (

    filtered_df[
        "Goals/60 Percentile"
    ] * 0.50

    +

    filtered_df[
        "Points/60 Percentile"
    ] * 0.50

).round(2)

# ==================================================
# GEM SCORE
# ==================================================

filtered_df["Gem Score"] = (

    filtered_df["Underlying Score"]

    -

    filtered_df["Production Score"]

).round(2)

# ==================================================
# FINISHING DELTA
# ==================================================

filtered_df["Finishing Delta"] = (

    filtered_df["Goals"]

    -

    filtered_df["xG (Expected goals)"]

).round(2)

# ==================================================
# BREAKOUT SCORE
# ==================================================

filtered_df["Breakout Score"] = (

    filtered_df["Gem Score"] * 0.60

    +

    filtered_df[
        "Impact Score Percentile"
    ] * 0.20

    +

    (
        100
        -
        filtered_df["Age"] * 2
    ) * 0.20

).round(2)

# ==================================================
# REGRESSION RISK
# ==================================================

filtered_df["Regression Risk"] = (

    filtered_df["Finishing Delta"] * 0.60

    +

    filtered_df[
        "Goals/60 Percentile"
    ] * 0.20

    -

    filtered_df[
        "xG (Expected goals)/60 Percentile"
    ] * 0.20

).round(2)

# ==================================================
# MARKET INEFFICIENCY
# ==================================================

filtered_df["Market Inefficiency"] = (

    filtered_df[
        "Impact Score Percentile"
    ] * 0.35

    +

    filtered_df[
        "Transition Score Percentile"
    ] * 0.25

    +

    filtered_df[
        "Playmaking Score Percentile"
    ] * 0.20

    -

    filtered_df[
        "Points/60 Percentile"
    ] * 0.20

).round(2)

# ==================================================
# WHY FUNCTION
# ==================================================

def why_player(row):

    reasons = []

    if row["Shots/60 Percentile"] >= 80:
        reasons.append("Elite shot generation")

    if row["xG (Expected goals)/60 Percentile"] >= 80:
        reasons.append("High xG creation")

    if row["Transition Score Percentile"] >= 80:
        reasons.append("Strong transition")

    if row["Impact Score Percentile"] >= 80:
        reasons.append("Drives impact")

    if row["Points/60 Percentile"] <= 40:
        reasons.append("Low production vs process")

    return " | ".join(reasons)

filtered_df["Why"] = filtered_df.apply(
    why_player,
    axis=1
)

# ==================================================
# BREAKOUT CANDIDATES
# ==================================================

st.markdown("---")

st.subheader("🚀 Breakout Candidates")

breakout_df = filtered_df.sort_values(
    by="Breakout Score",
    ascending=False
).head(15)

st.dataframe(

    breakout_df[[
        "Player",
        "Team",
        "Age",

        "Breakout Score",
        "Gem Score",

        "Goals/60",
        "Points/60",

        "Shots/60",
        "xG (Expected goals)/60",

        "Transition Score",
        "Impact Score",

        "Why"
    ]],

    use_container_width=True,
    hide_index=True,
    height=500

)

# ==================================================
# HIDDEN GEMS
# ==================================================

st.markdown("---")

st.subheader("💎 Hidden Gems")

gem_df = filtered_df.sort_values(
    by="Gem Score",
    ascending=False
).head(15)

st.dataframe(

    gem_df[[
        "Player",
        "Team",
        "Age",

        "Gem Score",

        "Goals/60",
        "Points/60",

        "Shots/60",
        "xG (Expected goals)/60",

        "Scoring chances - total/60",

        "Transition Score",
        "Impact Score",

        "Why"
    ]],

    use_container_width=True,
    hide_index=True,
    height=500

)

# ==================================================
# REGRESSION RISKS
# ==================================================

st.markdown("---")

st.subheader("⚠️ Regression Risks")

regression_df = filtered_df.sort_values(
    by="Regression Risk",
    ascending=False
).head(15)

st.dataframe(

    regression_df[[
        "Player",
        "Team",
        "Age",

        "Regression Risk",

        "Goals",
        "xG (Expected goals)",

        "Finishing Delta",

        "Goals/60",
        "xG (Expected goals)/60",

        "Why"
    ]],

    use_container_width=True,
    hide_index=True,
    height=500

)

# ==================================================
# MARKET INEFFICIENCIES
# ==================================================

st.markdown("---")

st.subheader("🧠 Market Inefficiencies")

market_df = filtered_df.sort_values(
    by="Market Inefficiency",
    ascending=False
).head(15)

st.dataframe(

    market_df[[
        "Player",
        "Team",
        "Age",

        "Market Inefficiency",

        "Impact Score",
        "Transition Score",
        "Playmaking Score",

        "Points/60",

        "Net xG (xG player on - opp. team's xG)",

        "Why"
    ]],

    use_container_width=True,
    hide_index=True,
    height=500

)

# ==================================================
# FULL DATABASE
# ==================================================

st.markdown("---")

st.subheader("📋 Full Player Database")

search = st.text_input(
    "Search Player"
)

database_df = filtered_df.copy()

if search:

    database_df = database_df[

        database_df["Player"]
        .str.contains(
            search,
            case=False,
            na=False
        )

    ]

st.dataframe(

    database_df[[
        "Player",
        "Team",
        "Position",
        "Age",

        "Overall Score",

        "Gem Score",
        "Breakout Score",
        "Regression Risk",
        "Market Inefficiency",

        "Goals/60",
        "Points/60",

        "Shots/60",
        "xG (Expected goals)/60",

        "Transition Score",
        "Impact Score"
    ]],

    use_container_width=True,
    hide_index=True,
    height=700

)
