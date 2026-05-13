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
# REQUIRED COLUMN
# -----------------------------------

# Vaihda tämä myöhemmin omaan overall/value metriikkaan
# jos sellainen löytyy valmiina datasta

if "Overall Score" not in df.columns:

    # Yksinkertainen nykyarvo demo
    df["Overall Score"] = (
        (
            pd.to_numeric(df["Goals/60"], errors="coerce").fillna(0)
            * 0.30
        )
        +
        (
            pd.to_numeric(df["Assists/60"], errors="coerce").fillna(0)
            * 0.25
        )
        +
        (
            pd.to_numeric(df["xG (Expected goals)/60"], errors="coerce").fillna(0)
            * 0.25
        )
        +
        (
            pd.to_numeric(df["Net xG (xG player on - opp. team's xG)/60"], errors="coerce").fillna(0)
            * 0.20
        )
    ).round(2)

# -----------------------------------
# PLAYER SELECT
# -----------------------------------

players = sorted(df["Player"].dropna().unique())

selected_player = st.selectbox(
    "Select Player",
    players
)

# -----------------------------------
# FILTER PLAYER DATA
# -----------------------------------

player_df = (
    df[df["Player"] == selected_player]
    .sort_values("Season")
)

latest = player_df.iloc[-1]

# -----------------------------------
# CURRENT INFO
# -----------------------------------

current_value = latest["Overall Score"]
age = latest["Age"]
team = latest["Team"]
position = latest["Position"]

# -----------------------------------
# SIMPLE PROJECTION MODEL
# -----------------------------------

# AGE BONUS

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

# TREND BONUS

if len(player_df) >= 2:

    previous_value = player_df.iloc[-2]["Overall Score"]

    trend_bonus = (
        current_value
        - previous_value
    ) * 2

else:
    trend_bonus = 0

# FINAL PROJECTION

future_value = (
    current_value
    + age_bonus
    + trend_bonus
)

future_value = round(future_value, 1)

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
    "Goals/60",
    "Assists/60",
    "xG (Expected goals)/60",
    "Overall Score"
]

available_metrics = [
    m for m in graph_metrics
    if m in player_df.columns
]

metric_choice = st.selectbox(
    "Select Metric",
    available_metrics
)

fig = px.line(
    player_df,
    x="Season",
    y=metric_choice,
    markers=True,
    title=f"{selected_player} — {metric_choice} Development"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# -----------------------------------
# RAW DATA
# -----------------------------------

st.subheader("Season Data")

st.dataframe(
    player_df,
    use_container_width=True
)
