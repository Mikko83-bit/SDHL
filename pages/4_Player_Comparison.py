import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# =========================
# PAGE TITLE
# =========================

st.title("⚔️ Player Comparison")

# =========================
# LOAD DATA
# =========================

df = pd.read_excel("SDHL_Player_Value_Model.xlsx")

# =========================
# PLAYER SELECTORS
# =========================

players = sorted(df["Player"].unique())

col1, col2 = st.columns(2)

with col1:
    player1 = st.selectbox(
        "Select Player 1",
        players,
        index=0
    )

with col2:
    player2 = st.selectbox(
        "Select Player 2",
        players,
        index=1
    )

# =========================
# PLAYER DATA
# =========================

p1 = df[df["Player"] == player1].iloc[0]
p2 = df[df["Player"] == player2].iloc[0]

# =========================
# RADAR CHART METRICS
# =========================

metrics = [
    "Creation Score",
    "Shot Quality",
    "Puck Control",
    "Net xG /60",
    "Value"
]

# =========================
# RADAR CHART
# =========================

fig = go.Figure()

fig.add_trace(go.Scatterpolar(
    r=[p1[m] for m in metrics],
    theta=metrics,
    fill='toself',
    name=player1
))

fig.add_trace(go.Scatterpolar(
    r=[p2[m] for m in metrics],
    theta=metrics,
    fill='toself',
    name=player2
))

fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True
        )
    ),
    showlegend=True,
    height=700
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =========================
# COMPARISON TABLE
# =========================

st.subheader("📊 Comparison Table")

comparison_df = pd.DataFrame({
    "Metric": metrics,
    player1: [round(p1[m], 2) for m in metrics],
    player2: [round(p2[m], 2) for m in metrics]
})

st.dataframe(
    comparison_df,
    use_container_width=True
)

