import streamlit as st
import pandas as pd
import numpy as np

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Breakout Probability Model",
    layout="wide"
)

# ==================================================
# TITLE
# ==================================================

st.title("🚀 Breakout Probability Model")

st.markdown("""
Predicts which players are most likely to break out offensively.

Model uses:
- Multi-season weighted data
- Underlying metrics
- Age curve
- Transition impact
- Shot generation
- xG trends
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

numeric_cols = [

    "Goals/60",
    "Points/60",

    "Shots/60",
    "xG (Expected goals)/60",

    "Scoring chances - total/60",

    "Transition Score",
    "Impact Score",
    "Playmaking Score",

    "Overall Score",

    "Time on ice"

]

for col in numeric_cols:

    if col in df.columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

# ==================================================
# ACTIVE PLAYERS ONLY
# ==================================================

active_players = df[
    df["Season"] == "2025-2026"
]["Player"].unique()

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

    "Points/60",
    "Shots/60",
    "xG (Expected goals)/60",

    "Scoring chances - total/60",

    "Transition Score",
    "Impact Score",
    "Playmaking Score",

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
# GROUP PLAYERS
# ==================================================

group_cols = [

    "Player",
    "Team",
    "Position",
    "Age"

]

agg_dict = {}

for metric in weighted_metrics:

    agg_dict[
        f"Weighted {metric}"
    ] = "sum"

agg_dict["Time on ice"] = "sum"

player_df = df.groupby(
    group_cols,
    as_index=False
).agg(agg_dict)

# ==================================================
# RENAME WEIGHTED COLUMNS
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
# KEEP ACTIVE PLAYERS
# ==================================================

player_df = player_df[

    player_df["Player"].isin(
        active_players
    )

]

# ==================================================
# FILTERS
# ==================================================

st.sidebar.header("Filters")

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

# TOI FILTER

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
    max_value=40,
    value=(18, 27)
)

filtered_df = filtered_df[

    (filtered_df["Age"] >= min_age)

    &

    (filtered_df["Age"] <= max_age)

]

# ==================================================
# CREATE PERCENTILES
# ==================================================

percentile_metrics = [

    "Points/60",
    "Shots/60",
    "xG (Expected goals)/60",

    "Scoring chances - total/60",

    "Transition Score",
    "Impact Score",
    "Playmaking Score"

]

for metric in percentile_metrics:

    if metric in filtered_df.columns:

        filtered_df[
            f"{metric} Percentile"
        ] = (

            filtered_df[metric]
            .rank(pct=True)

            * 100

        )

# ==================================================
# AGE CURVE SCORE
# ==================================================

filtered_df["Age Curve Score"] = np.where(

    filtered_df["Age"] <= 21,
    100,

    np.where(
        filtered_df["Age"] <= 24,
        85,

        np.where(
            filtered_df["Age"] <= 27,
            70,
            50
        )
    )
)

# ==================================================
# BREAKOUT PROBABILITY
# ==================================================

filtered_df["Breakout Probability"] = (

    filtered_df[
        "xG (Expected goals)/60 Percentile"
    ] * 0.25

    +

    filtered_df[
        "Shots/60 Percentile"
    ] * 0.20

    +

    filtered_df[
        "Transition Score Percentile"
    ] * 0.15

    +

    filtered_df[
        "Impact Score Percentile"
    ] * 0.15

    +

    filtered_df[
        "Playmaking Score Percentile"
    ] * 0.10

    +

    filtered_df[
        "Scoring chances - total/60 Percentile"
    ] * 0.05

    +

    filtered_df[
        "Age Curve Score"
    ] * 0.10

)

filtered_df["Breakout Probability"] = (

    filtered_df[
        "Breakout Probability"
    ]
    .clip(0, 100)
    .round(1)

)

# ==================================================
# BUILD REASON
# ==================================================

def breakout_reason(row):

    reasons = []

    if row.get(
        "xG (Expected goals)/60 Percentile",
        0
    ) >= 80:

        reasons.append(
            "Elite xG profile"
        )

    if row.get(
        "Shots/60 Percentile",
        0
    ) >= 80:

        reasons.append(
            "High shot volume"
        )

    if row.get(
        "Transition Score Percentile",
        0
    ) >= 80:

        reasons.append(
            "Strong transition driver"
        )

    if row.get(
        "Impact Score Percentile",
        0
    ) >= 80:

        reasons.append(
            "Drives team impact"
        )

    if row.get(
        "Age",
        99
    ) <= 22:

        reasons.append(
            "Positive age curve"
        )

    return " | ".join(reasons)

filtered_df["Why"] = filtered_df.apply(
    breakout_reason,
    axis=1
)

# ==================================================
# SORT
# ==================================================

filtered_df = filtered_df.sort_values(
    by="Breakout Probability",
    ascending=False
)

# ==================================================
# PLAYER CARD
# ==================================================

def breakout_card(row):

    probability = row[
        "Breakout Probability"
    ]

    if probability >= 80:

        color = "#22C55E"

    elif probability >= 65:

        color = "#FACC15"

    else:

        color = "#EF4444"

    st.markdown(

        f"""
<div style="
background:#111827;
padding:22px;
border-radius:18px;
margin-bottom:18px;
border-left:8px solid {color};
">

<div style="
font-size:28px;
font-weight:800;
color:white;
">
{row['Player']}
</div>

<div style="
font-size:15px;
color:#D1D5DB;
margin-top:4px;
">
{row['Team']} | {row['Position']} | Age {int(row['Age'])}
</div>

<div style="
font-size:44px;
font-weight:900;
color:{color};
margin-top:16px;
line-height:1;
">
{probability}%
</div>

<div style="
font-size:14px;
font-weight:700;
color:white;
margin-top:4px;
">
Breakout Probability
</div>

<div style="
margin-top:18px;
font-size:15px;
line-height:1.8;
color:white;
">

{row['Why']}

</div>

</div>
""",

        unsafe_allow_html=True

    )

# ==================================================
# TOP BREAKOUTS
# ==================================================

st.markdown("---")

st.subheader("🚀 Most Likely Breakout Players")

top_breakouts = filtered_df.head(12)

for _, row in top_breakouts.iterrows():

    breakout_card(row)

# ==================================================
# TABLE VIEW
# ==================================================

st.markdown("---")

st.subheader("📋 Model Output")

st.dataframe(

    filtered_df[[
        "Player",
        "Team",
        "Age",

        "Breakout Probability",

        "Points/60",
        "Shots/60",

        "xG (Expected goals)/60",

        "Transition Score",
        "Impact Score",

        "Why"
    ]],

    use_container_width=True,
    hide_index=True,
    height=700

)
