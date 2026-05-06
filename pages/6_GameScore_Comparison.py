import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(layout="wide")

# =========================
# PAGE TITLE
# =========================

st.title("🧠 Game Score Comparison")

# =========================
# LOAD DATA
# =========================

df = pd.read_excel(
    "SDHL_ZScore_GameScore_Final.xlsx"
)

# =========================
# CLEAN DATA
# =========================

numeric_columns = [
    "Goals/60",
    "Assists/60",
    "xG/60",
    "Net xG",
    "Game Score",
    "Adjusted Game Score"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=numeric_columns)

# =========================
# SIDEBAR FILTERS
# =========================

st.sidebar.header("Filters")

teams = sorted(df["Team"].unique())

team1 = st.sidebar.selectbox(
    "Select Team 1",
    teams
)

team2 = st.sidebar.selectbox(
    "Select Team 2",
    teams,
    index=1 if len(teams) > 1 else 0
)

# =========================
# PLAYER FILTERS
# =========================

players_team1 = sorted(
    df[df["Team"] == team1]["Player"].unique()
)

players_team2 = sorted(
    df[df["Team"] == team2]["Player"].unique()
)

player1 = st.sidebar.selectbox(
    "Select Player 1",
    players_team1
)

player2 = st.sidebar.selectbox(
    "Select Player 2",
    players_team2
)

# =========================
# PLAYER DATA
# =========================

p1 = df[df["Player"] == player1].iloc[0]
p2 = df[df["Player"] == player2].iloc[0]

# =========================
# RADAR METRICS
# =========================

metrics = [
    "Goals/60",
    "Assists/60",
    "xG/60",
    "Net xG",
    "Game Score",
    "Adjusted Game Score"
]

# =========================
# AUTO SCALE
# =========================

max_value = max(
    max([p1[m] for m in metrics]),
    max([p2[m] for m in metrics])
) * 1.15

# =========================
# RADAR COMPARISON
# =========================

st.subheader("📊 Advanced Analytics Radar")

fig = go.Figure()

# PLAYER 1

fig.add_trace(go.Scatterpolar(
    r=[p1[m] for m in metrics],
    theta=metrics,
    fill='toself',
    name=player1,
    line=dict(
        color='#00E5FF',
        width=4
    ),
    fillcolor='rgba(0,229,255,0.30)'
))

# PLAYER 2

fig.add_trace(go.Scatterpolar(
    r=[p2[m] for m in metrics],
    theta=metrics,
    fill='toself',
    name=player2,
    line=dict(
        color='#FF5252',
        width=4
    ),
    fillcolor='rgba(255,82,82,0.30)'
))

# =========================
# RADAR LAYOUT
# =========================

fig.update_layout(
    template="plotly_dark",
    polar=dict(
        bgcolor="#111111",
        radialaxis=dict(
            visible=True,
            range=[0, max_value],
            gridcolor="gray",
            linecolor="gray",
            tickfont=dict(
                color="white"
            )
        ),
        angularaxis=dict(
            gridcolor="gray",
            linecolor="gray",
            tickfont=dict(
                color="white",
                size=13
            )
        )
    ),
    paper_bgcolor="#111111",
    plot_bgcolor="#111111",
    font=dict(
        color="white"
    ),
    showlegend=True,
    height=750
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =========================
# PLAYER CARDS
# =========================

st.subheader("🏒 Player Cards")

card_col1, card_col2 = st.columns(2)

# =========================
# PLAYER 1 CARD
# =========================

with card_col1:

    st.markdown(f"## {player1}")

    st.markdown(
        f"### {p1['Team']} | {p1['Position']}"
    )

    st.metric(
        "Game Score",
        round(p1["Game Score"], 2)
    )

    st.metric(
        "Adjusted GS",
        round(p1["Adjusted Game Score"], 2)
    )

    st.metric(
        "Goals/60",
        round(p1["Goals/60"], 2)
    )

    st.metric(
        "xG/60",
        round(p1["xG/60"], 2)
    )

# =========================
# PLAYER 2 CARD
# =========================

with card_col2:

    st.markdown(f"## {player2}")

    st.markdown(
        f"### {p2['Team']} | {p2['Position']}"
    )

    st.metric(
        "Game Score",
        round(p2["Game Score"], 2)
    )

    st.metric(
        "Adjusted GS",
        round(p2["Adjusted Game Score"], 2)
    )

    st.metric(
        "Goals/60",
        round(p2["Goals/60"], 2)
    )

    st.metric(
        "xG/60",
        round(p2["xG/60"], 2)
    )

# =========================
# COMPARISON TABLE
# =========================

st.subheader("📈 Comparison Table")

comparison_metrics = [
    "Goals/60",
    "Assists/60",
    "xG/60",
    "Net xG",
    "Game Score",
    "Adjusted Game Score"
]

comparison_df = pd.DataFrame({
    "Metric": comparison_metrics,
    player1: [
        round(p1[m], 2)
        for m in comparison_metrics
    ],
    player2: [
        round(p2[m], 2)
        for m in comparison_metrics
    ]
})

st.dataframe(
    comparison_df,
    use_container_width=True
)
