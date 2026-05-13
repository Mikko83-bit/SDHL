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

    "Net xG (xG player on 0 opp. team's xG)": "Net_xG",

    "xG (Expected goals)": "xG"
})

# -----------------------------------
# SIDEBAR
# -----------------------------------

st.sidebar.header("Filters")

# MINIMUM TOI

min_toi = st.sidebar.slider(
    "Minimum TOI Minutes",
    min_value=0,
    max_value=1000,
    value=300,
    step=25
)

# FILTER DATA

df = df[
    df["TOI_minutes"] >= min_toi
]

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

filtered_df = df[
    df["Position"] == selected_position
]

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
# LEAGUE AVERAGE
# -----------------------------------

league_average = (
    df["Current Value"]
    .mean()
)

# -----------------------------------
# FUTURE VALUE FUNCTION
# -----------------------------------

def calculate_future_value(player_history):

    player_history = player_history.sort_values(
        "Season"
    )

    latest = player_history.iloc[-1]

    current_value = latest["Current Value"]

    age = latest["Age"]

    # -----------------------------------
    # WEIGHTED VALUE
    # -----------------------------------

    values = player_history[
        "Current Value"
    ].tolist()

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

    # -----------------------------------
    # AGE MULTIPLIER
    # -----------------------------------

    age_multiplier = (

        1.08

        -

        ((age - 21) * 0.005)

    )

    age_multiplier = max(
        0.95,
        min(age_multiplier, 1.10)
    )

    # -----------------------------------
    # TREND
    # -----------------------------------

    if len(player_history) >= 2:

        previous_value = (
            player_history.iloc[-2]["Current Value"]
        )

        trend_adjustment = (

            current_value
            - previous_value

        ) * 0.15

    else:

        trend_adjustment = 0

    # -----------------------------------
    # FINISHING REGRESSION
    # -----------------------------------

    finishing_delta = latest[
        "Finishing Delta"
    ]

    if finishing_delta <= -3:

        finishing_adjustment = 0.10

    elif finishing_delta >= 3:

        finishing_adjustment = -0.10

    else:

        finishing_adjustment = 0

    # -----------------------------------
    # REGRESSION TO MEAN
    # -----------------------------------

    regression_strength = 0.15

    regressed_value = (

        weighted_value
        * (1 - regression_strength)

        +

        league_average
        * regression_strength
    )

    # -----------------------------------
    # FUTURE VALUE
    # -----------------------------------

    future_value = (

        regressed_value
        * age_multiplier

        +

        trend_adjustment

        +

        finishing_adjustment
    )

    # -----------------------------------
    # CAP EXTREME GROWTH
    # -----------------------------------

    max_growth = (
        current_value * 1.15
    )

    future_value = min(
        future_value,
        max_growth
    )

    future_value = round(
        future_value,
        2
    )

    return future_value

# -----------------------------------
# CALCULATE FUTURE VALUE FOR ALL
# -----------------------------------

future_values = []

for player in df["Player"].unique():

    player_history = (
        df[df["Player"] == player]
        .sort_values("Season")
    )

    future_value = calculate_future_value(
        player_history
    )

    latest_row = player_history.iloc[-1]

    future_values.append({

        "Player": player,
        "Team": latest_row["Team"],
        "Position": latest_row["Position"],
        "Age": latest_row["Age"],

        "Current Value": latest_row["Current Value"],

        "Future Value": future_value,

        "Growth Potential": round(
            future_value
            - latest_row["Current Value"],
            2
        ),

        "Finishing Delta": latest_row[
            "Finishing Delta"
        ],

        "TOI_minutes": latest_row[
            "TOI_minutes"
        ]
    })

# -----------------------------------
# PROJECTION DATAFRAME
# -----------------------------------

projection_df = pd.DataFrame(
    future_values
)

# -----------------------------------
# MERGE FUTURE VALUE BACK TO DF
# -----------------------------------

df = df.merge(

    projection_df[[
        "Player",
        "Future Value",
        "Growth Potential"
    ]],

    on="Player",

    how="left"
)

# -----------------------------------
# PERCENTILES
# FORWARDS & DEFENDERS SEPARATELY
# -----------------------------------

forwards = df[
    df["Position"] == "F"
].copy()

defenders = df[
    df["Position"] == "D"
].copy()

# -----------------------------------
# FORWARD PERCENTILES
# -----------------------------------

forward_metrics = [

    "Goals_60",
    "Assists_60",
    "Points_60",
    "xG_60",

    "Current Value",

    "Future Value",

    "Growth Potential"
]

for metric in forward_metrics:

    forwards[f"{metric} Percentile"] = (

        forwards[metric]
        .rank(pct=True)

        * 100

    ).round(1)

# -----------------------------------
# DEFENDER PERCENTILES
# -----------------------------------

defender_metrics = [

    "Current Value",

    "Future Value",

    "Growth Potential",

    "Net_xG",

    "Takeaways/60",

    "Blocked shots/60"
]

for metric in defender_metrics:

    defenders[f"{metric} Percentile"] = (

        defenders[metric]
        .rank(pct=True)

        * 100

    ).round(1)

# -----------------------------------
# COMBINE BACK
# -----------------------------------

df = pd.concat([
    forwards,
    defenders
])

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
# PLAYER PROJECTION
# -----------------------------------

player_projection = projection_df[
    projection_df["Player"]
    == selected_player
].iloc[0]

# -----------------------------------
# CONFIDENCE
# -----------------------------------

toi = latest["TOI_minutes"]

if toi >= 700:
    confidence = "High"

elif toi >= 400:
    confidence = "Medium"

else:
    confidence = "Low"

# -----------------------------------
# MAIN METRICS
# -----------------------------------

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric(
    "Current Value",
    player_projection["Current Value"]
)

col2.metric(
    "Projected Future Value",
    player_projection["Future Value"]
)

col3.metric(
    "Growth Potential",
    player_projection["Growth Potential"]
)

col4.metric(
    "Finishing Delta",
    player_projection["Finishing Delta"]
)

col5.metric(
    "Age",
    player_projection["Age"]
)

col6.metric(
    "Projection Confidence",
    confidence
)

# -----------------------------------
# PERCENTILES
# -----------------------------------

st.subheader("📊 Percentile Rankings")

p1, p2, p3 = st.columns(3)

p1.metric(
    "Current Value Percentile",
    f"{latest['Current Value Percentile']}th"
)

p2.metric(
    "Future Value Percentile",
    f"{latest['Future Value Percentile']}th"
)

p3.metric(
    "Growth Potential Percentile",
    f"{latest['Growth Potential Percentile']}th"
)

# -----------------------------------
# PERCENTILE BARS
# -----------------------------------

st.progress(
    latest["Current Value Percentile"] / 100
)

st.caption(
    "Current Value Percentile"
)

st.progress(
    latest["Future Value Percentile"] / 100
)

st.caption(
    "Future Value Percentile"
)

# -----------------------------------
# PLAYER INFO
# -----------------------------------

st.markdown(f"""
### Player Information

- **Current Team:** {latest['Team']}
- **Position:** {latest['Position']}
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
# MARKET DISCOVERY
# -----------------------------------

st.header("🔍 Market Discovery (Scouting)")

col_up, col_down = st.columns(2)

with col_up:

    st.subheader("🚀 Top Breakout Candidates")

    top_growth = projection_df.sort_values(
        "Growth Potential",
        ascending=False
    ).head(10)

    st.dataframe(
        top_growth[[
            "Player",
            "Team",
            "Age",
            "Current Value",
            "Future Value",
            "Growth Potential"
        ]],
        use_container_width=True
    )

with col_down:

    st.subheader("⚠️ Regression Risks")

    top_decline = projection_df.sort_values(
        "Growth Potential",
        ascending=True
    ).head(10)

    st.dataframe(
        top_decline[[
            "Player",
            "Team",
            "Age",
            "Current Value",
            "Future Value",
            "Growth Potential"
        ]],
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

    "Future Value",

    "Growth Potential",

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
