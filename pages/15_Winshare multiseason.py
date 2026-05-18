# =====================================================
# PLAYER CAREER TREND
# ADD THIS TO THE VERY END OF THE FILE
# =====================================================

st.divider()

st.header("Player Career Trend")

# =====================================================
# PLAYER SELECT
# =====================================================

players_list = sorted(
    final_df["Player"].dropna().unique()
)

selected_player = st.selectbox(
    "Choose Player",
    players_list
)

# =====================================================
# PLAYER DATA
# =====================================================

player_df = final_df[
    final_df["Player"] == selected_player
].copy()

player_df = player_df.sort_values(
    "Season"
)

# =====================================================
# CAREER TABLE
# =====================================================

st.subheader(f"{selected_player} Career")

st.dataframe(

    player_df[[
        "Season",
        "Team",
        "Position",
        "OWS",
        "DWS",
        "WS",
        "WS_percentile"
    ]],

    use_container_width=True,
    hide_index=True

)

# =====================================================
# WS GRAPH
# =====================================================

fig = px.line(

    player_df,

    x="Season",
    y="WS",

    markers=True,

    title=f"{selected_player} - Win Share Trend"

)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================================
# OWS VS DWS GRAPH
# =====================================================

trend_df = player_df.melt(

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

    title=f"{selected_player} - OWS vs DWS"

)

st.plotly_chart(
    fig2,
    use_container_width=True
)
