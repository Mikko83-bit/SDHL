# =========================================================
# LOAD FINAL DATA
# =========================================================

final_df = load_data()

# =========================================================
# UI
# =========================================================

st.title("🏒 Winshare Multiseason")

c1, c2, c3 = st.columns(3)

with c1:

    season_filter = st.selectbox(
        "Season",
        sorted(final_df["Season"].unique())
    )

with c2:

    team_filter = st.selectbox(
        "Team",
        ["All"] +
        sorted(
            final_df[
                final_df["Season"] == season_filter
            ]["Team"].unique()
        )
    )

with c3:

    position_filter = st.selectbox(
        "Position",
        ["All", "F", "D"]
    )

# =========================================================
# FILTER
# =========================================================

filtered_df = final_df[
    final_df["Season"] == season_filter
]

if team_filter != "All":

    filtered_df = filtered_df[
        filtered_df["Team"] == team_filter
    ]

if position_filter != "All":

    filtered_df = filtered_df[
        filtered_df["Position"] == position_filter
    ]

# =========================================================
# TABLE
# =========================================================

st.subheader(
    f"Top Win Shares - {season_filter}"
)

table = (

    filtered_df[[
        "Player",
        "Team",
        "Position",
        "OWS",
        "DWS",
        "WS",
        "WS_percentile"
    ]]

    .sort_values(
        "WS",
        ascending=False
    )

)

st.dataframe(
    table,
    use_container_width=True,
    hide_index=True
)

# =========================================================
# PLAYER CAREER TREND
# =========================================================

st.subheader("Player Career Trend")

player = st.selectbox(
    "Select Player",
    sorted(final_df["Player"].unique())
)

career_df = (

    final_df[
        final_df["Player"] == player
    ]

    .sort_values("Season")

)

# =========================================================
# CAREER TABLE
# =========================================================

career_table = (

    career_df[[
        "Season",
        "Team",
        "Position",
        "OWS",
        "DWS",
        "WS",
        "WS_percentile"
    ]]

)

st.dataframe(
    career_table,
    use_container_width=True,
    hide_index=True
)

# =========================================================
# WS GRAPH
# =========================================================

fig = px.line(

    career_df,

    x="Season",
    y="WS",

    markers=True,

    title=f"{player} - Win Share Trend"

)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =========================================================
# OWS VS DWS GRAPH
# =========================================================

trend_df = career_df.melt(

    id_vars=["Season"],

    value_vars=["OWS", "DWS"],

    var_name="Metric",
    value_name="Value"

)

fig2 = px.line(

    trend_df,

    x="Season",
    y="Value",
    color="Metric",

    markers=True,

    title=f"{player} - OWS vs DWS"

)

st.plotly_chart(
    fig2,
    use_container_width=True
)
