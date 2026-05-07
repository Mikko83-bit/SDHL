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
# TEAM LOGOS
# =========================

logo_size = 110

team_logos = {

    "Brynas": "images/Brynas.png",

    "Djurgarden": "images/Djurgarden.png",

    "Farjestad": "images/Farjestad.png",

    "Frolunda": "images/Frolunda.png",

    "HV71": "images/HV71.png",

    "Linkoping": "images/Linkoping.png",

    "Lulea/MSSK": "images/Lulea.png",

    "MODO": "images/MODO.png",

    "SDE HF": "images/SDE HF.png",

    "Skelleftea": "images/Skelleftea AIK.png"
}

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
    "Time on ice"
]

for col in numeric_columns:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

df = df.dropna(subset=numeric_columns)

# =========================
# SIDEBAR FILTERS
# =========================

st.sidebar.header("Filters")

# POSITION FILTER

positions = sorted(
    df["Position"].unique()
)

selected_position = st.sidebar.selectbox(
    "Position",
    positions
)

filtered_position_df = df[
    df["Position"] == selected_position
]

# TEAM FILTERS

teams = sorted(
    filtered_position_df["Team"].unique()
)

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
    filtered_position_df[
        filtered_position_df["Team"] == team1
    ]["Player"].unique()
)

players_team2 = sorted(
    filtered_position_df[
        filtered_position_df["Team"] == team2
    ]["Player"].unique()
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

p1 = filtered_position_df[
    filtered_position_df["Player"] == player1
].iloc[0]

p2 = filtered_position_df[
    filtered_position_df["Player"] == player2
].iloc[0]

# =========================
# RADAR METRICS
# =========================

metrics = [
    "Goals/60",
    "Assists/60",
    "xG/60",
    "Net xG",
    "Game Score"
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

    # TEAM LOGO

    if p1["Team"] in team_logos:

        st.image(
            team_logos[p1["Team"]],
            width=logo_size
        )

    # PLAYER INFO

    st.markdown(
        f"## {player1}"
    )

    st.markdown(
        f"### {p1['Team']} | {p1['Position']}"
    )

    st.metric(
        "Game Score",
        round(p1["Game Score"], 2)
    )

    st.metric(
        "Goals/60",
        round(p1["Goals/60"], 2)
    )

    st.metric(
        "Assists/60",
        round(p1["Assists/60"], 2)
    )

    st.metric(
        "xG/60",
        round(p1["xG/60"], 2)
    )

    st.metric(
        "Net xG",
        round(p1["Net xG"], 2)
    )

    st.metric(
        "TOI",
        round(p1["Time on ice"], 1)
    )

# =========================
# PLAYER 2 CARD
# =========================

with card_col2:

    # TEAM LOGO

    if p2["Team"] in team_logos:

        st.image(
            team_logos[p2["Team"]],
            width=logo_size
        )

    # PLAYER INFO

    st.markdown(
        f"## {player2}"
    )

    st.markdown(
        f"### {p2['Team']} | {p2['Position']}"
    )

    st.metric(
        "Game Score",
        round(p2["Game Score"], 2)
    )

    st.metric(
        "Goals/60",
        round(p2["Goals/60"], 2)
    )

    st.metric(
        "Assists/60",
        round(p2["Assists/60"], 2)
    )

    st.metric(
        "xG/60",
        round(p2["xG/60"], 2)
    )

    st.metric(
        "Net xG",
        round(p2["Net xG"], 2)
    )

    st.metric(
        "TOI",
        round(p2["Time on ice"], 1)
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
    "Time on ice"
]

table_rows = []

for metric in comparison_metrics:

    value1 = round(p1[metric], 2)
    value2 = round(p2[metric], 2)

    # BETTER / WORSE

    if value1 > value2:

        winner1 = "🟢"
        winner2 = "🔴"

    elif value2 > value1:

        winner1 = "🔴"
        winner2 = "🟢"

    else:

        winner1 = "⚪"
        winner2 = "⚪"

    table_rows.append({

        "Metric": metric,

        player1: f"{winner1} {value1}",

        player2: f"{winner2} {value2}"
    })

comparison_df = pd.DataFrame(table_rows)

# =========================
# DISPLAY TABLE
# =========================

st.dataframe(
    comparison_df,
    use_container_width=False,
    hide_index=True
)
