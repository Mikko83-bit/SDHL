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

st.title("⚔️ Player Comparison")

# =========================
# LOAD DATA
# =========================

df_value = pd.read_excel(
    "SDHL_Player_Value_Model.xlsx"
)

df_gamescore = pd.read_excel(
    "SDHL_ZScore_GameScore_Final.xlsx"
)

# =========================
# MERGE DATA
# =========================

df = pd.merge(
    df_value,
    df_gamescore,
    on=["Player", "Team", "Position"],
    how="inner"
)

# =========================
# CLEAN DATA
# =========================

numeric_columns = [
    "Value",
    "Value_pct",
    "Creation Score",
    "Shot Quality",
    "Puck Control",
    "Net xG /60",
    "Game Score",
    "Adjusted Game Score"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=numeric_columns)

# =========================
# TEAM COLORS
# =========================

team_colors = {
    "Brynas": "#C9A227",
    "Lulea/MSSK": "#D72638",
    "Frolunda": "#1B5E20",
    "SDE HF": "#1976D2",
    "MODO": "#7B1FA2",
    "Djurgarden": "#0D47A1",
    "Farjestad": "#2E7D32",
    "Linkoping": "#1565C0",
    "Skelleftea": "#F57C00"
}

# =========================
# TEAM FILTERS
# =========================

st.subheader("🏒 Team Selection")

teams = sorted(df["Team"].unique())

col1, col2 = st.columns(2)

with col1:
    team1 = st.selectbox(
        "Select Team 1",
        teams
    )

with col2:
    team2 = st.selectbox(
        "Select Team 2",
        teams
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

st.subheader("👥 Player Selection")

col1, col2 = st.columns(2)

with col1:
    player1 = st.selectbox(
        "Select Player 1",
        players_team1
    )

with col2:
    player2 = st.selectbox(
        "Select Player 2",
        players_team2
    )

# =========================
# PLAYER DATA
# =========================

p1 = df[df["Player"] == player1].iloc[0]
p2 = df[df["Player"] == player2].iloc[0]

# =========================
# TEAM COLORS
# =========================

color1 = team_colors.get(team1, "#00BFFF")
color2 = team_colors.get(team2, "#FF4C4C")

# =========================
# RADAR METRICS
# =========================

metrics = [
    "Creation Score",
    "Shot Quality",
    "Puck Control",
    "Net xG /60",
    "Game Score",
    "Adjusted Game Score"
]

# =========================
# RADAR CHART
# =========================

st.subheader("📊 Radar Comparison")

fig = go.Figure()

fig.add_trace(go.Scatterpolar(
    r=[p1[m] for m in metrics],
    theta=metrics,
    fill='toself',
    name=player1,
    line=dict(
        color=color1,
        width=3
    ),
    fillcolor='rgba(0,191,255,0.30)'
))

fig.add_trace(go.Scatterpolar(
    r=[p2[m] for m in metrics],
    theta=metrics,
    fill='toself',
    name=player2,
    line=dict(
        color=color2,
        width=3
    ),
    fillcolor='rgba(255,76,76,0.30)'
))

fig.update_layout(
    template="plotly_dark",
    polar=dict(
        bgcolor="#111111",
        radialaxis=dict(
            visible=True,
            range=[0, 15],
            gridcolor="gray",
            linecolor="gray",
            tickfont=dict(color="white")
        ),
        angularaxis=dict(
            gridcolor="gray",
            linecolor="gray",
            tickfont=dict(
                color="white",
                size=12
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
# PLAYER INFORMATION
# =========================

st.subheader("📋 Player Information")

info_col1, info_col2 = st.columns(2)

with info_col1:
    st.markdown(f"### {player1}")

    st.write({
        "Team": p1["Team"],
        "Position": p1["Position"],
        "Value": round(p1["Value"], 2),
        "Value %": round(p1["Value_pct"], 1),
        "Game Score": round(p1["Game Score"], 2),
        "Adjusted GS": round(p1["Adjusted Game Score"], 2)
    })

with info_col2:
    st.markdown(f"### {player2}")

    st.write({
        "Team": p2["Team"],
        "Position": p2["Position"],
        "Value": round(p2["Value"], 2),
        "Value %": round(p2["Value_pct"], 1),
        "Game Score": round(p2["Game Score"], 2),
        "Adjusted GS": round(p2["Adjusted Game Score"], 2)
    })

# =========================
# COMPARISON TABLE
# =========================

st.subheader("📈 Comparison Table")

comparison_metrics = [
    "Creation Score",
    "Shot Quality",
    "Puck Control",
    "Net xG /60",
    "Game Score",
    "Adjusted Game Score",
    "Value",
    "Value_pct"
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
