import streamlit as st
import pandas as pd
import plotly.express as px

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="xGSA",
    layout="wide"
)

st.title("🥅 xGSA Dashboard")

st.markdown(
    "Advanced SDHL goalie analytics dashboard."
)

# ==================================================
# LOAD DATA
# ==================================================

df = pd.read_excel(
    "Goalies - Sdhl 2025-2026.xlsx"
)

# ==================================================
# CLEAN DATA
# ==================================================

df.columns = df.columns.str.strip()

# ==================================================
# FIX TIME ON ICE
# ==================================================

def toi_to_minutes(toi):

    try:

        parts = str(toi).split(":")

        hours = int(parts[0])

        minutes = int(parts[1])

        seconds = int(parts[2])

        total_minutes = (

            hours * 60 +

            minutes +

            seconds / 60

        )

        return round(total_minutes,2)

    except:

        return 0

df["TOI Minutes"] = df[
    "Time on ice"
].apply(toi_to_minutes)

# ==================================================
# CONVERT NUMERIC
# ==================================================

numeric_cols = [

    "Games played",
    "xGSA",
    "Goals against",
    "Shots on goal",
    "Saves",
    "xG conceded",
    "xG per shot taken",
    "xG per goal conceded",
    "xG per shot saved",
    "Age"

]

for col in numeric_cols:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# ==================================================
# SAVE %
# ==================================================

df["Save %"] = (

    df["Saves"] /

    df["Shots on goal"]

) * 100

# ==================================================
# GOALS AGAINST /60
# ==================================================

df["GA/60"] = (

    df["Goals against"] /

    df["TOI Minutes"]

) * 60

# ==================================================
# SAVES /60
# ==================================================

df["Saves/60"] = (

    df["Saves"] /

    df["TOI Minutes"]

) * 60

# ==================================================
# xGA /60
# ==================================================

df["xGA/60"] = (

    df["xG conceded"] /

    df["TOI Minutes"]

) * 60

# ==================================================
# ROUND VALUES
# ==================================================

num_cols = df.select_dtypes(
    include="number"
).columns

df[num_cols] = df[
    num_cols
].round(2)

# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.header("Filters")

# MIN GP

min_gp = st.sidebar.slider(

    "Minimum Games Played",

    min_value=1,

    max_value=int(df["Games played"].max()),

    value=5,

    step=1

)

# TEAM FILTER

teams = sorted(
    df["Team"].dropna().unique()
)

selected_teams = st.sidebar.multiselect(

    "Teams",

    teams,

    default=teams

)

# SORT OPTION

sort_options = [

    "xGSA",
    "Save %",
    "GA/60",
    "xGA/60",
    "Saves/60",
    "xG per shot taken"

]

selected_sort = st.sidebar.selectbox(
    "Sort By",
    sort_options
)

# ==================================================
# FILTER DATA
# ==================================================

filtered_df = df[

    (df["Games played"] >= min_gp) &

    (df["Team"].isin(selected_teams))

]

filtered_df = filtered_df.sort_values(

    by=selected_sort,

    ascending=False

)

# ==================================================
# TOP METRICS
# ==================================================

top1, top2, top3, top4 = st.columns(4)

with top1:

    st.metric(
        "Goalies",
        len(filtered_df)
    )

with top2:

    st.metric(
        "Best xGSA",
        round(filtered_df["xGSA"].max(),1)
    )

with top3:

    st.metric(
        "Best Save %",
        round(filtered_df["Save %"].max(),1)
    )

with top4:

    st.metric(
        "Lowest GA/60",
        round(filtered_df["GA/60"].min(),2)
    )

st.markdown("---")

# ==================================================
# xGSA BAR CHART
# ==================================================

st.subheader("📊 xGSA Rankings")

chart_df = filtered_df.sort_values(
    by="xGSA",
    ascending=True
)

fig = px.bar(

    chart_df,

    x="xGSA",

    y="Player",

    orientation="h",

    color="xGSA",

    hover_data=[

        "Team",
        "Games played",
        "Save %",
        "xG conceded"

    ]

)

fig.update_layout(

    height=700,

    template="plotly_dark",

    yaxis_title="",

    xaxis_title="xGSA",

    font=dict(size=15)

)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==================================================
# SCATTER PLOT
# ==================================================

st.markdown("---")

st.subheader("🎯 Workload vs Efficiency")

scatter_fig = px.scatter(

    filtered_df,

    x="xG conceded",

    y="Save %",

    size="Shots on goal",

    color="xGSA",

    hover_name="Player",

    hover_data=[

        "Team",
        "Games played",
        "GA/60"

    ]

)

scatter_fig.update_layout(

    height=700,

    template="plotly_dark",

    xaxis_title="Expected Goals Against",

    yaxis_title="Save %"

)

st.plotly_chart(
    scatter_fig,
    use_container_width=True
)

# ==================================================
# GOALIE TABLE
# ==================================================

st.markdown("---")

st.subheader("📋 Goalie Leaderboard")

display_cols = [

    "Player",
    "Team",
    "Games played",
    "TOI Minutes",
    "xGSA",
    "Save %",
    "Goals against",
    "Shots on goal",
    "Saves",
    "GA/60",
    "Saves/60",
    "xGA/60",
    "xG conceded",
    "xG per shot taken",
    "Age"

]

st.dataframe(

    filtered_df[
        display_cols
    ],

    use_container_width=True,

    height=700

)

# ==================================================
# GOALIE COMPARISON
# ==================================================

st.markdown("---")

st.subheader("⚔️ Goalie Comparison")

goalie_names = sorted(
    filtered_df["Player"].unique()
)

g1, g2 = st.columns(2)

with g1:

    goalie1 = st.selectbox(
        "Goalie 1",
        goalie_names,
        key="g1"
    )

with g2:

    goalie2 = st.selectbox(
        "Goalie 2",
        goalie_names,
        index=min(1, len(goalie_names)-1),
        key="g2"
    )

p1 = filtered_df[
    filtered_df["Player"] == goalie1
].iloc[0]

p2 = filtered_df[
    filtered_df["Player"] == goalie2
].iloc[0]

compare_df = pd.DataFrame({

    "Metric": [

        "xGSA",
        "Save %",
        "GA/60",
        "Saves/60",
        "xGA/60",
        "xG per shot taken"

    ],

    goalie1: [

        p1["xGSA"],
        p1["Save %"],
        p1["GA/60"],
        p1["Saves/60"],
        p1["xGA/60"],
        p1["xG per shot taken"]

    ],

    goalie2: [

        p2["xGSA"],
        p2["Save %"],
        p2["GA/60"],
        p2["Saves/60"],
        p2["xGA/60"],
        p2["xG per shot taken"]

    ]

})

st.dataframe(

    compare_df,

    use_container_width=True

)
