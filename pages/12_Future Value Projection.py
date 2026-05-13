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

    "Net xG (xG player on 0 opp. team's xG)": "Net_xG"
})

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
# SIDEBAR
# -----------------------------------

st.sidebar.header("Filters")

# POSITION FILTER

positions = sorted(
    df["Position"]
    .dropna()
    .unique()
)

selected_position = st.sidebar.selectbox(
    "Select Position",
    positions
)

# FILTER POSITION

filtered_df = df[
    df["Position"] == selected_position
]

# PLAYER FILTER

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

current_value = latest["Current Value"]
age = latest["Age"]
team = latest["Team"]
position = latest["Position"]

# -----------------------------------
# AGE MULTIPLIER
# -----------------------------------

if age <= 21:
    age_multiplier = 1.20

elif age <= 24:
    age_multiplier = 1.12

elif age <= 27:
    age_multiplier = 1.05

elif age <= 30:
    age_multiplier = 1.00

else:
    age_multiplier = 0.92

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
# FUTURE VALUE
# -----------------------------------

future_value = (
    current_value
    * age_multiplier
    + trend_adjustment
)

future_value = round(
    future_value,
    2
)

# -----------------------------------
# METRICS
# -----------------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Current Value",
    round(current_value, 2)
)

col2.metric(
    "Projected Future Value",
    future_value
)

col3.metric(
    "Age",
    age
)

col4.metric(
    "Trend Adjustment",
    round(trend_adjustment, 2)
)

# -----------------------------------
# PLAYER INFO
# -----------------------------------

st.markdown(f"""
### Player Information

- **Current Team:** {team}
- **Position:** {position}
- **Latest Season:** {latest['Season']}
""")

# -----------------------------------
# DEVELOPMENT GRAPH
# -----------------------------------

graph_metrics = [
    "Goals_60",
    "Assists_60",
    "Points_60",
    "xG_60",
    "Current Value"
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
        "Games played"
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
    "Time on ice",

    "Goals",
    "Assists",
    "Points",

    "Shots",
    "Shots on goal",

    "xG (Expected goals)",

    "Goals_60",
    "Assists_60",
    "Points_60",
    "xG_60",

    "Current Value"
]

available_columns = [
    c for c in raw_columns
    if c in player_df.columns
]

st.dataframe(
    player_df[available_columns],
    use_container_width=True
)
