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

# ==================================================
# TITLE
# ==================================================

st.title("🔎 Market Discovery")

st.markdown("""
Simple scouting dashboard focused on:
- 💎 Hidden Gems
- 🚀 Breakout Players
- ⚠️ Regression Risks
- 🧠 Market Inefficiencies
""")

# ==================================================
# LOAD DATA
# ==================================================

df = pd.read_excel(
    "Sdhl_2023_2026_complete.xlsx"
)

# ==================================================
# CLEAN DATA
# ==================================================

df.columns = df.columns.str.strip()

# ==================================================
# CLEAN TEXT
# ==================================================

text_cols = [
    "Player",
    "Team",
    "Position",
    "Season"
]

for col in text_cols:

    if col in df.columns:

        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
        )

# ==================================================
# CREATE AGE
# ==================================================

if "Date of birth" in df.columns:

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

if (
    "Points/60" not in df.columns
    and
    "Goals/60" in df.columns
    and
    "Assists/60" in df.columns
):

    df["Points/60"] = (

        pd.to_numeric(
            df["Goals/60"],
            errors="coerce"
        )

        +

        pd.to_numeric(
            df["Assists/60"],
            errors="coerce"
        )

    )

# ==================================================
# NUMERIC CONVERSION
# ==================================================

metrics = [

    "Goals/60",
    "Points/60",

    "Shots/60",
    "xG (Expected goals)/60",
    "Scoring chances - total/60",

    "Shooting Score",
    "Playmaking Score",
    "Transition Score",
    "Impact Score",

    "Overall Score",

    "Goals",
    "xG (Expected goals)",

    "Time on ice"

]

for col in metrics:

    if col in df.columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

# ==================================================
# SEASON WEIGHTS
# ==================================================

season_weights = {

    "2025-2026": 0.50,
    "2024-2025": 0.30,
    "2023-2024": 0.20

}

# ==================================================
# FILTER SEASONS
# ==================================================

df = df[
    df["Season"].isin(
        season_weights.keys()
    )
]

# ==================================================
# APPLY WEIGHTS
# ==================================================

df["Season Weight"] = df[
    "Season"
].map(season_weights)

# ==================================================
# WEIGHTED METRICS
# ==================================================

weighted_metrics = [

    "Goals/60",
    "Points/60",

    "Shots/60",
    "xG (Expected goals)/60",
    "Scoring chances - total/60",

    "Shooting Score",
    "Playmaking Score",
    "Transition Score",
    "Impact Score",

    "Overall Score"

]

weighted_metrics = [

    metric for metric in weighted_metrics

    if metric in df.columns

]

# ==================================================
# CREATE WEIGHTED VALUES
# ==================================================

for metric in weighted_metrics:

    df[f"Weighted {metric}"] = (

        df[metric]

        *

        df["Season Weight"]

    )

# ==================================================
# GROUP PLAYER DATA
# ==================================================

group_cols = [

    "Player",
    "Team",
    "Position",
    "Age"

]

agg_dict = {}

for metric in weighted_metrics:

    agg_dict[f"Weighted {metric}"] = "sum"

agg_dict["Time on ice"] = "sum"

player_df = df.groupby(
    group_cols,
    as_index=False
).agg(agg_dict)

# ==================================================
# RENAME COLUMNS
# ==================================================

rename_dict = {}

for metric in weighted_metrics:

    rename_dict[
        f"Weighted {metric}"
    ] = metric

player_df = player_df.rename(
    columns=rename_dict
)

# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.header("Filters")

# POSITION

positions = sorted(
    player_df["Position"]
    .dropna()
    .unique()
)

selected_position = st.sidebar.selectbox(
    "Position",
    positions
)

filtered_df = player_df[
    player_df["Position"]
    == selected_position
]

# MIN TOI

min_toi = st.sidebar.slider(
    "Minimum TOI",
    min_value=0,
    max_value=3000,
    value=500,
    step=50
)

filtered_df = filtered_df[
    filtered_df["Time on ice"]
    >= min_toi
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
# PERCENTILES
# ==================================================

percentile_metrics = [

    "Goals/60",
    "Points/60",

    "Shots/60",
    "xG (Expected goals)/60",
    "Scoring chances - total/60",

    "Transition Score",
    "Impact Score"

]

for metric in percentile_metrics:

    filtered_df[f"{metric} Percentile"] = (

        filtered_df[metric]
        .rank(pct=True)

        * 100

    )

# ==================================================
# GEM SCORE
# ==================================================

filtered_df["Gem Score"] = (

    filtered_df[
        "xG (Expected goals)/60 Percentile"
    ] * 0.30

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
    ] * 0.10

    -

    filtered_df[
        "Points/60 Percentile"
    ] * 0.40

)

# ==================================================
# FINISHING DELTA
# ==================================================

filtered_df["Finishing Delta"] = (

    filtered_df["Goals"]

    -

    filtered_df["xG (Expected goals)"]

)

# ==================================================
# BREAKOUT SCORE
# ==================================================

filtered_df["Breakout Score"] = (

    filtered_df["Gem Score"] * 0.50

    +

    filtered_df[
        "Impact Score Percentile"
    ] * 0.20

    +

    (
        100
        -
        filtered_df["Age"] * 2
    ) * 0.30

)

# ==================================================
# REGRESSION RISK
# ==================================================

filtered_df["Regression Risk"] = (

    filtered_df["Finishing Delta"] * 0.70

    +

    filtered_df[
        "Goals/60 Percentile"
    ] * 0.30

)

# ==================================================
# MARKET INEFFICIENCY
# ==================================================

filtered_df["Market Inefficiency"] = (

    filtered_df[
        "Impact Score Percentile"
    ] * 0.40

    +

    filtered_df[
        "Transition Score Percentile"
    ] * 0.30

    -

    filtered_df[
        "Points/60 Percentile"
    ] * 0.30

)

# ==================================================
# WHY FUNCTION
# ==================================================

def build_reason(row):

    reasons = []

    if row["Shots/60 Percentile"] >= 80:
        reasons.append("Elite shot generation")

    if row["xG (Expected goals)/60 Percentile"] >= 80:
        reasons.append("Strong xG profile")

    if row["Transition Score Percentile"] >= 80:
        reasons.append("Transition driver")

    if row["Points/60 Percentile"] <= 40:
        reasons.append("Low production")

    return " | ".join(reasons)

filtered_df["Why"] = filtered_df.apply(
    build_reason,
    axis=1
)

# ==================================================
# CARD FUNCTION
# ==================================================

def scouting_card(row, score_name):

    score = round(row[score_name], 1)

    st.markdown(

        f"""
<div style="
background:#111827;
padding:18px;
border-radius:16px;
margin-bottom:14px;
border:1px solid #1F2937;
">

<div style="
font-size:24px;
font-weight:800;
color:white;
">
{row['Player']}
</div>

<div style="
font-size:15px;
color:#D1D5DB;
margin-top:2px;
">
{row['Team']} | {row['Position']} | Age {int(row['Age'])}
</div>

<div style="
font-size:18px;
font-weight:700;
color:#00E5FF;
margin-top:12px;
">
{score_name}: {score}
</div>

<div style="
margin-top:12px;
font-size:15px;
color:white;
line-height:1.7;
">

{row['Why']}

</div>

</div>
""",

        unsafe_allow_html=True

    )

# ==================================================
# HIDDEN GEMS
# ==================================================

st.markdown("---")
st.subheader("💎 Hidden Gems")

gem_df = filtered_df.sort_values(
    by="Gem Score",
    ascending=False
).head(8)

for _, row in gem_df.iterrows():

    scouting_card(
        row,
        "Gem Score"
    )

# ==================================================
# BREAKOUT PLAYERS
# ==================================================

st.markdown("---")
st.subheader("🚀 Breakout Players")

breakout_df = filtered_df.sort_values(
    by="Breakout Score",
    ascending=False
).head(8)

for _, row in breakout_df.iterrows():

    scouting_card(
        row,
        "Breakout Score"
    )

# ==================================================
# REGRESSION RISKS
# ==================================================

st.markdown("---")
st.subheader("⚠️ Regression Risks")

regression_df = filtered_df.sort_values(
    by="Regression Risk",
    ascending=False
).head(8)

for _, row in regression_df.iterrows():

    scouting_card(
        row,
        "Regression Risk"
    )

# ==================================================
# MARKET INEFFICIENCIES
# ==================================================

st.markdown("---")
st.subheader("🧠 Market Inefficiencies")

market_df = filtered_df.sort_values(
    by="Market Inefficiency",
    ascending=False
).head(8)

for _, row in market_df.iterrows():

    scouting_card(
        row,
        "Market Inefficiency"
    )
