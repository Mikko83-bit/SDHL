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
# RENAME COLUMNS
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
# SIDEBAR FILTERS
# -----------------------------------

st.sidebar.header("Filters")

# TEAM FILTER

teams = sorted(
    df["Team"]
    .dropna()
    .unique()
)

selected_team = st.sidebar.selectbox(
    "Select Team",
    teams
)

# FILTER TEAM DATA

team_df = df[
    df["Team"] == selected_team
]

# PLAYER FILTER

players = sorted(
    team_df["Player"]
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
    team_df[
        team_df["Player"] == selected_player
    ]
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
# AGE BONUS
# -----------------------------------

if age <= 21:
    age_bonus = 8

elif age <= 24:
    age_bonus = 5

elif age <= 27:
    age_bonus = 2

elif age <= 30:
    age_bonus = 0

else:
    age_bonus = -4

# -----------------------------------
# TREND BONUS
# -----------------------------------

if len(player_df) >= 2:

    previous_value = (
        player_df.iloc[-2]["Current Value"]
    )

    trend_bonus = (
        current_value
        - previous_value
    ) * 2

else:
    trend_bonus = 0

# -----------------------------------
# FINAL PROJECTION
# -----------------------------------

future_value = (
    current_value
    + age_bonus
    + trend_bonus
)

future_value = round(
    future_value,
    1
)

# -----------------------------------
# METRICS
# -----------------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Current Value",
    round(current_value, 1)
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
    "Trend Bonus",
    round(trend_bonus, 1)
)

# -----------------------------------
# PLAYER INFO
# -----------------------------------

st.markdown(f"""
### Player Information

- **Team:** {team}
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
    markers=True,
    title=f"{selected_player} — {metric_choice}"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# -----------------------------------
# RAW DATA SECTION
# -----------------------------------

st.subheader("Raw Data Behind Projection")

raw_columns = [

    "Season",
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

available_raw_columns = [
    c for c in raw_columns
    if c in player_df.columns
]

st.dataframe(
    player_df[available_raw_columns],
    use_container_width=True
)
