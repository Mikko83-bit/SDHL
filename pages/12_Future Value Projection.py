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

st.title("🔎 Market Discovery (3-Year Weighted Model)")

st.markdown("""
Multi-season scouting model using weighted SDHL data.

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

metrics = [

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

    "Goals",
    "Points",
    "xG (Expected goals)",

    "Net xG (xG player on - opp. team's xG)",

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
# FILTER VALID SEASONS
# ==================================================

if "Season" in df.columns:

    df = df[
        df["Season"].isin(
            season_weights.keys()
        )
    ]

# ==================================================
# CREATE SEASON WEIGHT
# ==================================================

df["Season Weight"] = df[
    "Season"
].map(season_weights)

# ==================================================
# WEIGHTED METRICS
# ==================================================

weighted_metrics = [

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

    "Net xG (xG player on - opp. team's xG)"

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

        pd.to_numeric(
            df[metric],
            errors="coerce"
        )

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

# MIN TOI

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

    metric for metric in percentile_metrics

    if metric in filtered_df.columns

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
# SAFE GET FUNCTION
# ==================================================

def safe_col(col_name):

    if col_name in filtered_df.columns:
        return filtered_df[col_name]

    return 0

# ==================================================
# UNDERLYING SCORE
# ==================================================

filtered_df["Underlying Score"] = (

    safe_col("xG (Expected goals)/60 Percentile") * 0.25

    +

    safe_col("Shots/60 Percentile") * 0.25

    +

    safe_col("Scoring chances - total/60 Percentile") * 0.20

    +

    safe_col("Transition Score Percentile") * 0.15

    +

    safe_col("Impact Score Percentile") * 0.15

).round(2)

# ==================================================
# PRODUCTION SCORE
# ==================================================

filtered_df["Production Score"] = (

    safe_col("Goals/60 Percentile") * 0.50

    +

    safe_col("Points/60 Percentile") * 0.50

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

if (
    "Goals" in filtered_df.columns
    and
    "xG (Expected goals)" in filtered_df.columns
):

    filtered_df["Finishing Delta"] = (

        filtered_df["Goals"]

        -

        filtered_df["xG (Expected goals)"]

    ).round(2)

else:

    filtered_df["Finishing Delta"] = 0

# ==================================================
# TREND SCORE
# ==================================================

if (
    "Season" in df.columns
    and
    "Overall Score" in df.columns
):

    trend_df = df.pivot_table(

        index="Player",

        columns="Season",

        values="Overall Score",

        aggfunc="mean"

    ).reset_index()

    if (
        "2025-2026" in trend_df.columns
        and
        "2024-2025" in trend_df.columns
    ):

        trend_df["Trend Score"] = (

            trend_df["2025-2026"]

            -

            trend_df["2024-2025"]

        )

    else:

        trend_df["Trend Score"] = 0

    filtered_df = filtered_df.merge(

        trend_df[
            ["Player", "Trend Score"]
        ],

        on="Player",

        how="left"

    )

else:

    filtered_df["Trend Score"] = 0

filtered_df["Trend Score"] = (
    filtered_df["Trend Score"]
    .fillna(0)
)

# ==================================================
# BREAKOUT SCORE
# ==================================================

filtered_df["Breakout Score"] = (

    filtered_df["Gem Score"] * 0.45

    +

    filtered_df["Trend Score"] * 0.25

    +

    safe_col("Impact Score Percentile") * 0.15

    +

    (
        100
        -
        filtered_df["Age"] * 2
    ) * 0.15

).round(2)

# ==================================================
# REGRESSION RISK
# ==================================================

filtered_df["Regression Risk"] = (

    filtered_df["Finishing Delta"] * 0.60

    +

    safe_col("Goals/60 Percentile") * 0.20

    -

    safe_col("xG (Expected goals)/60 Percentile") * 0.20

).round(2)

# ==================================================
# MARKET INEFFICIENCY
# ==================================================

filtered_df["Market Inefficiency"] = (

    safe_col("Impact Score Percentile") * 0.35

    +

    safe_col("Transition Score Percentile") * 0.25

    +

    safe_col("Playmaking Score Percentile") * 0.20

    -

    safe_col("Points/60 Percentile") * 0.20

).round(2)

# ==================================================
# WHY FUNCTION
# ==================================================

def why_player(row):

    reasons = []

    if row.get("Shots/60 Percentile", 0) >= 80:
        reasons.append("Elite shot generation")

    if row.get("xG (Expected goals)/60 Percentile", 0) >= 80:
        reasons.append("High xG creation")

    if row.get("Transition Score Percentile", 0) >= 80:
        reasons.append("Strong transition")

    if row.get("Trend Score", 0) >= 5:
        reasons.append("Strong upward trend")

    if row.get("Points/60 Percentile", 100) <= 40:
        reasons.append("Low production vs process")

    return " | ".join(reasons)

filtered_df["Why"] = filtered_df.apply(
    why_player,
    axis=1
)

# ==================================================
# BREAKOUT TABLE
# ==================================================

st.markdown("---")
st.subheader("🚀 Breakout Candidates")

breakout_df = filtered_df.sort_values(
    by="Breakout Score",
    ascending=False
).head(20)

st.dataframe(
    breakout_df,
    use_container_width=True,
    hide_index=True,
    height=600
)

# ==================================================
# GEM TABLE
# ==================================================

st.markdown("---")
st.subheader("💎 Hidden Gems")

gem_df = filtered_df.sort_values(
    by="Gem Score",
    ascending=False
).head(20)

st.dataframe(
    gem_df,
    use_container_width=True,
    hide_index=True,
    height=600
)

# ==================================================
# REGRESSION TABLE
# ==================================================

st.markdown("---")
st.subheader("⚠️ Regression Risks")

regression_df = filtered_df.sort_values(
    by="Regression Risk",
    ascending=False
).head(20)

st.dataframe(
    regression_df,
    use_container_width=True,
    hide_index=True,
    height=600
)

# ==================================================
# MARKET TABLE
# ==================================================

st.markdown("---")
st.subheader("🧠 Market Inefficiencies")

market_df = filtered_df.sort_values(
    by="Market Inefficiency",
    ascending=False
).head(20)

st.dataframe(
    market_df,
    use_container_width=True,
    hide_index=True,
    height=600
)
