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

st.title("🏒 Advanced Player Profile")

# =========================
# TEAM LOGOS
# =========================

logo_size = 120

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
# PERCENTILES
# =========================

df["Goals_pct"] = (
    df["Goals/60"]
    .rank(pct=True) * 100
)

df["Assists_pct"] = (
    df["Assists/60"]
    .rank(pct=True) * 100
)

df["xG_pct"] = (
    df["xG/60"]
    .rank(pct=True) * 100
)

df["NetxG_pct"] = (
    df["Net xG"]
    .rank(pct=True) * 100
)

df["GameScore_pct"] = (
    df["Game Score"]
    .rank(pct=True) * 100
)

# =========================
# SIDEBAR FILTERS
# =========================

st.sidebar.header("Filters")

positions = sorted(
    df["Position"].unique()
)

selected_position = st.sidebar.selectbox(
    "Position",
    positions
)

filtered_df = df[
    df["Position"] == selected_position
]

teams = sorted(
    filtered_df["Team"].unique()
)

selected_team = st.sidebar.selectbox(
    "Team",
    teams
)

players = sorted(
    filtered_df[
        filtered_df["Team"] == selected_team
    ]["Player"].unique()
)

selected_player = st.sidebar.selectbox(
    "Player",
    players
)

# =========================
# PLAYER DATA
# =========================

p = filtered_df[
    filtered_df["Player"] == selected_player
].iloc[0]

# =========================
# PLAYER ARCHETYPE
# =========================

archetype = "Balanced Player"

description = (
    "Balanced player profile without one dominant offensive trait."
)

# ELITE FINISHER

if (
    p["Goals/60"] >= 1.0
    and
    p["xG/60"] >= 0.9
):

    archetype = "Elite Finisher"

    description = (
        "Dangerous offensive scorer with elite finishing ability and strong shot generation."
    )

# PLAYMAKER

elif (
    p["Assists/60"] >= 1.0
):

    archetype = "Offensive Playmaker"

    description = (
        "Creative offensive player who drives offense through passing and puck movement."
    )

# TWO-WAY

elif (
    p["Net xG"] >= 2
    and
    p["Game Score"] >= 5
):

    archetype = "Two-Way Impact Player"

    description = (
        "Reliable impact player who positively affects overall on-ice results."
    )

# SHOT CREATOR

elif (
    p["xG/60"] >= 1.0
):

    archetype = "Shot Creator"

    description = (
        "Creates dangerous scoring opportunities consistently through shot generation."
    )

# =========================
# PAGE LAYOUT
# =========================

left_col, right_col = st.columns([1, 2])

# =========================
# LEFT SIDE
# =========================

with left_col:

    # TEAM LOGO

    if p["Team"] in team_logos:

        st.image(
            team_logos[p["Team"]],
            width=logo_size
        )

    # PLAYER NAME

    st.markdown(
        f"# {selected_player}"
    )

    st.markdown(
        f"### {p['Team']} | {p['Position']}"
    )

    # ARCHETYPE

    st.subheader("🧬 Archetype")

    st.success(archetype)

    st.write(description)

    # KEY STATS

    st.subheader("📊 Key Stats")

    st.metric(
        "Game Score",
        round(p["Game Score"], 2)
    )

    st.metric(
        "Goals/60",
        round(p["Goals/60"], 2)
    )

    st.metric(
        "Assists/60",
        round(p["Assists/60"], 2)
    )

    st.metric(
        "xG/60",
        round(p["xG/60"], 2)
    )

    st.metric(
        "Net xG",
        round(p["Net xG"], 2)
    )

# =========================
# RIGHT SIDE
# =========================

with right_col:

    # =========================
    # PERCENTILE PROFILE
    # =========================

    st.subheader("📈 Percentile Profile")

    percentile_metrics = {
        "Goals/60": round(p["Goals_pct"]),
        "Assists/60": round(p["Assists_pct"]),
        "xG/60": round(p["xG_pct"]),
        "Net xG": round(p["NetxG_pct"]),
        "Game Score": round(p["GameScore_pct"])
    }

    for metric, percentile in percentile_metrics.items():

        st.markdown(
            f"### {metric} — {percentile}th Percentile"
        )

        st.progress(
            percentile / 100
        )

    # =========================
    # RADAR CHART
    # =========================

    st.subheader("🕸️ Player Radar")

    radar_metrics = [
        "Goals/60",
        "Assists/60",
        "xG/60",
        "Net xG",
        "Game Score"
    ]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(

        r=[p[m] for m in radar_metrics],

        theta=radar_metrics,

        fill='toself',

        name=selected_player,

        line=dict(
            color='#00E5FF',
            width=4
        ),

        fillcolor='rgba(0,229,255,0.30)'
    ))

    max_value = max(
        [p[m] for m in radar_metrics]
    ) * 1.15

    fig.update_layout(

        template="plotly_dark",

        polar=dict(

            bgcolor="#111111",

            radialaxis=dict(

                visible=True,

                range=[0, max_value],

                gridcolor="gray",

                linecolor="gray"
            )
        ),

        paper_bgcolor="#111111",

        plot_bgcolor="#111111",

        font=dict(
            color="white"
        ),

        height=650,

        showlegend=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =========================
# AUTOMATED SCOUTING REPORT
# =========================

st.subheader("🔍 Automated Scouting Report")

report = []

# SCORING

if p["Goals_pct"] >= 90:

    report.append(
        "Elite-level scoring profile relative to league peers."
    )

elif p["Goals_pct"] >= 70:

    report.append(
        "Above-average scoring ability."
    )

else:

    report.append(
        "Limited finishing production relative to league average."
    )

# PLAYMAKING

if p["Assists_pct"] >= 90:

    report.append(
        "High-end offensive playmaking profile."
    )

elif p["Assists_pct"] >= 70:

    report.append(
        "Strong offensive creation ability."
    )

# xG

if p["xG_pct"] >= 90:

    report.append(
        "Excellent ability to generate dangerous scoring chances."
    )

elif p["xG_pct"] >= 70:

    report.append(
        "Consistently creates quality offensive opportunities."
    )

# IMPACT

if p["NetxG_pct"] >= 90:

    report.append(
        "Elite positive on-ice impact profile."
    )

elif p["NetxG_pct"] >= 70:

    report.append(
        "Strong positive overall impact."
    )

# GAME SCORE

if p["GameScore_pct"] >= 90:

    report.append(
        "Projects as a top-tier offensive SDHL player."
    )

elif p["GameScore_pct"] >= 70:

    report.append(
        "Projects as a strong top-line contributor."
    )

# DISPLAY REPORT

for sentence in report:

    st.markdown(
        f"- {sentence}"
    )
