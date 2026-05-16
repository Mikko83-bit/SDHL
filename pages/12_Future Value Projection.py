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
Simple scouting dashboard using a weighted 3-year model.

Weights:
- 2025-2026 → 50%
- 2024-2025 → 30%
- 2023-2024 → 20%
""")

# ==================================================
# LOAD DATA
# ==================================================

df = pd.read_excel(
    "Sdhl_2023_2026_complete.xlsx"
)

# ==================================================
# CLEAN COLUMNS
# ==================================================

df.columns = df.columns.str.strip()

# ==================================================
# CLEAN TEXT COLUMNS
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

numeric_metrics = [

    "Goals/60",
    "Assists/60",
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
    "Points",
    "xG (Expected goals)",

    "Time on ice"

]

for col in numeric_metrics:

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
# FILTER VALID SEASONS
# ==================================================

if "Season" in df.columns:

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

# KEEP ONLY EXISTING

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

    agg_dict[
        f"Weighted {metric}"
    ] = "sum"

if "Time on ice" in df.columns:

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
# ROUND NUMBERS
# ==================================================

numeric_cols = player_df.select_dtypes(
    include="number"
).columns

player_df[numeric_cols] = player_df[
    numeric_cols
].round(2)

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

# MINIMUM TOI

min_toi = st.sidebar.slider(
    "Minimum TOI",
    min_value=0,
    max_value=3000,
    value=500,
    step=50
)

if "Time on ice" in filtered_df.columns:

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

# KEEP ONLY EXISTING COLUMNS

existing_percentile_metrics = []

for metric in percentile_metrics:

    if metric in filtered_df.columns:

        existing_percentile_metrics.append(metric)

# ==================================================
# CREATE PERCENTILES
# ==================================================

for metric in existing_percentile_metrics:

    filtered_df[
        f"{metric} Percentile"
    ] = (

        filtered_df[metric]
        .rank(pct=True)

        * 100

    )

# ==================================================
# SAFE COLUMN FUNCTION
# ==================================================

def safe_col(column_name):

    if column_name in filtered_df.columns:

        return filtered_df[column_name]

    return 0

# ==================================================
# GEM SCORE
# ==================================================

filtered_df["Gem Score"] = (

    safe_col(
        "xG (Expected goals)/60 Percentile"
    ) * 0.30

    +

    safe_col(
        "Shots/60 Percentile"
    ) * 0.25

    +

    safe_col(
        "Scoring chances - total/60 Percentile"
    ) * 0.20

    +

    safe_col(
        "Transition Score Percentile"
    ) * 0.15

    +

    safe_col(
        "Impact Score Percentile"
    ) * 0.10

    -

    safe_col(
        "Points/60 Percentile"
    ) * 0.40

)

# ==================================================
# FINISHING DELTA
# ==================================================

if (
    "Goals" in filtered_df.columns
    and
    "xG (Expected goals)" in filtered_df.columns
):

    filtered_df["Finishing Delta"] = (

        filtered_df["Goals"]

        -

        filtered_df["xG (Expected goals)"]

    )

else:

    filtered_df["Finishing Delta"] = 0

# ==================================================
# BREAKOUT SCORE
# ==================================================

filtered_df["Breakout Score"] = (

    filtered_df["Gem Score"] * 0.50

    +

    safe_col(
        "Impact Score Percentile"
    ) * 0.20

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

    safe_col(
        "Goals/60 Percentile"
    ) * 0.30

)

# ==================================================
# MARKET INEFFICIENCY
# ==================================================

filtered_df["Market Inefficiency"] = (

    safe_col(
        "Impact Score Percentile"
    ) * 0.40

    +

    safe_col(
        "Transition Score Percentile"
    ) * 0.30

    -

    safe_col(
        "Points/60 Percentile"
    ) * 0.30

)

# ==================================================
# WHY FUNCTION
# ==================================================

def build_reason(row):

    reasons = []

    if row.get(
        "Shots/60 Percentile",
        0
    ) >= 80:

        reasons.append(
            "Elite shot generation"
        )

    if row.get(
        "xG (Expected goals)/60 Percentile",
        0
    ) >= 80:

        reasons.append(
            "Strong xG profile"
        )

    if row.get(
        "Transition Score Percentile",
        0
    ) >= 80:

        reasons.append(
            "Transition driver"
        )

    if row.get(
        "Points/60 Percentile",
        100
    ) <= 40:

        reasons.append(
            "Low production"
        )

    return " | ".join(reasons)

filtered_df["Why"] = filtered_df.apply(
    build_reason,
    axis=1
)

# ==================================================
# SCOUTING CARD
# ==================================================

def scouting_card(row, score_name):

    score = round(
        row[score_name],
        1
    )

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
