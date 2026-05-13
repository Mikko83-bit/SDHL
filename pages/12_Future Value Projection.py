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

    "Goals": "Goals",
    "xG (Expected goals)": "xG",

    "Shots/60": "Shots_60",
    "Shots on goal/60": "Shots_On_Goal_60"
})

# -----------------------------------
# CURRENT VALUE
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
    pd.to_numeric(df["Goals"], errors="coerce").fillna(0)
    -
    pd.to_numeric(df["xG"], errors="coerce").fillna(0)
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
# WEIGHTED VALUE
# -----------------------------------

weights = [0.2, 0.3, 0.5]

values = player_df["Current Value"].tolist()

# Jos vähemmän kuin 3 kautta
if len(values) == 1:

    weighted_value = values[-1]

elif len(values) == 2:

    weighted_value = (
        values[0] * 0.4
        +
        values[1] * 0.6
    )

else:

    weighted_value = (

        values[-3] * 0.2
        +
        values[-2] * 0.3
        +
        values[-1] * 0.5
    )

weighted_value = round(
    weighted_value,
    2
)

# -----------------------------------
# PLAYER INFO
# -----------------------------------

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
# FINISHING REGRESSION
# -----------------------------------

finishing_delta = latest["Finishing Delta"]

# Aliperformannut -> pieni boost
if finishing_delta <= -3:

    finishing_adjustment = 0.20

# Yliperformannut -> pieni regressio
elif finishing_delta >= 3:

    finishing_adjustment = -0.20

else:

    finishing_adjustment = 0

# -----------------------------------
# FINAL FUTURE VALUE
# -----------------------------------

current_value = latest["Current Value"]

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
# METRICS
# -----------------------------------

col1, col2, col3, col4, col5 = st.columns(5)

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
    finishing_delta
)

col5.metric(
    "Age",
    age
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
