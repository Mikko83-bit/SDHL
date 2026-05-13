import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="Future Value Projection",
    layout="wide"
)

st.title("📈 Future Value Projection")

# -----------------------------------
# LOAD DATA
# -----------------------------------

df = pd.read_excel(
    "Sdhl_2023_2026_complete.xlsx"
)

# -----------------------------------
# RENAME IMPORTANT COLUMNS
# -----------------------------------

df = df.rename(columns={

    "Goals/60": "Goals_60",
    "Assists/60": "Assists_60",
    "Points/60": "Points_60",
    "xG (Expected goals)/60": "xG_60",

    "Shots/60": "Shots_60",
    "Shots on goal/60": "Shots_On_Goal_60",

    "Net xG (xG player on 0 opp. team's xG)": "Net_xG",

    "xG (Expected goals)": "xG"
})

# -----------------------------------
# TOI FILTER
# -----------------------------------

st.sidebar.header("Filters")

min_toi = st.sidebar.slider(
    "Minimum TOI Minutes",
    min_value=0,
    max_value=1000,
    value=200,
    step=25
)

# FILTER MINIMUM TOI

df = df[
    df["TOI_minutes"] >= min_toi
]

# -----------------------------------
# POSITION FILTER
# -----------------------------------

positions = sorted(
    df["Position"]
    .dropna()
    .unique()
)

selected_position = st.sidebar.selectbox(
    "Select Position",
    positions
)

filtered_df = df[
    df["Position"] == selected_position
]

# -----------------------------------
# CREATE CURRENT VALUE
# -----------------------------------

df["Current Value"] = (

    df["Goals_60"].fillna(0) * 0.30

    +

    df["Assists_60"].fillna(0) * 0.25

    +

    df["xG_60"].fillna(0) * 0.25

    +

    df["Points_60"].fillna(0) * 0.20

).round(2)

# -----------------------------------
# FINISHING DELTA
# -----------------------------------

df["Finishing Delta"] = (

    pd.to_numeric(
        df["Goals"],
        errors="coerce"
    ).fillna(0)

    -

    pd.to_numeric(
        df["xG"],
        errors="coerce"
    ).fillna(0)

).round(2)

# -----------------------------------
# PLAYER FILTER
# -----------------------------------

players = sorted(
    filtered_df["Player"]
    .dropna()
    .unique()
)

selected_player = st.sidebar.selectbox(
    "Select Player",
    players
)

# -----------------------------------
# PLAYER DATA
# -----------------------------------

player_df = (
    df[df["Player"] == selected_player]
    .sort_values("Season")
)

latest = player_df.iloc[-1]

# -----------------------------------
# PLAYER INFO
# -----------------------------------

age = latest["Age"]
team = latest["Team"]
position = latest["Position"]

current_value = latest["Current Value"]

# -----------------------------------
# WEIGHTED VALUE
# -----------------------------------

values = player_df["Current Value"].tolist()

if len(values) == 1:

    weighted_value = values[-1]

elif len(values) == 2:

    weighted_value = (

        values[0] * 0.40

        +

        values[1] * 0.60
    )

else:

    weighted_value = (

        values[-3] * 0.20

        +

        values[-2] * 0.30

        +

        values[-1] * 0.50
    )

weighted_value = round(
    weighted_value,
    2
)

# -----------------------------------
# SMOOTH AGE MULTIPLIER
# -----------------------------------

age_multiplier = (
    1.20
    -
    ((age - 21) * 0.015)
)

# LIMITS

age_multiplier = max(
    0.90,
    min(age_multiplier, 1.25)
)

# -----------------------------------
# TREND ADJUSTMENT
# -----------------------------------

if len(player_df) >= 2:

    previous_value = (
        player_df.iloc[-2]["Current Value"]
    )

    trend_adjustment = (

        current_value
        - previous_value

    ) * 0.25

else:

    trend_adjustment = 0

# -----------------------------------
# FINISHING REGRESSION
# -----------------------------------

finishing_delta = latest["Finishing Delta"]

if finishing_delta <= -3:

    finishing_adjustment = 0.20

elif finishing_delta >= 3:

    finishing_adjustment = -0.20

else:

    finishing_adjustment = 0

# -----------------------------------
# FUTURE VALUE
# -----------------------------------

future_value = (

    weighted_value
    * age_multiplier

    +

    trend_adjustment

    +

    finishing_adjustment

)

future_value = round(
    future_value,
    2
)

# -----------------------------------
# CONFIDENCE LEVEL
# -----------------------------------

toi = latest["TOI_minutes"]

if toi >= 700:
    confidence = "High"

elif toi >= 400:
    confidence = "Medium"

else:
    confidence = "Low"

# -----------------------------------
# METRICS
# -----------------------------------

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric(
    "Current Value",
    round(current_value, 2)
)

col2.metric(
    "Weighted Value",
    weighted_value
)

col3.metric(
    "Projected Future Value",
    future_value
)

col4.metric(
    "Finishing Delta",
    round(finishing_delta, 2)
)

col5.metric(
    "Age",
    age
)

col6.metric(
    "Projection Confidence",
    confidence
)

# -----------------------------------
# PLAYER INFO
# -----------------------------------

st.markdown(f"""
### Player Information

- **Current Team:** {team}
- **Position:** {position}
- **Latest Season:** {latest['Season']}
- **TOI Minutes:** {round(toi, 1)}
""")

# -----------------------------------
# DEVELOPMENT GRAPH
# -----------------------------------

graph_metrics = [

    "Goals_60",
    "Assists_60",
    "Points_60",
    "xG_60",

    "Current Value",

    "Finishing Delta"
]

metric_choice = st.selectbox(
    "Select Development Metric",
    graph_metrics
)

fig = px.line(
    player_df,
    x="Season",
    y=metric_choice,
    color="Team",
    markers=True,
    title=f"{selected_player} — {metric_choice}",
    hover_data=[
        "Team",
        "Age",
        "Games played",
        "TOI_minutes"
    ]
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# -----------------------------------
# RAW DATA
# -----------------------------------

st.subheader("Raw Data Behind Projection")

raw_columns = [

    "Season",
    "Team",
    "Age",

    "Games played",
    "TOI_minutes",

    "Goals",
    "Assists",
    "Points",

    "Shots",
    "Shots on goal",

    "xG",

    "Goals_60",
    "Assists_60",
    "Points_60",
    "xG_60",

    "Current Value",

    "Finishing Delta"
]

available_columns = [
    c for c in raw_columns
    if c in player_df.columns
]

st.dataframe(
    player_df[available_columns],
    use_container_width=True
)
