import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Player Comparison",
    layout="wide"
)

# ==================================================
# TITLE
# ==================================================

st.title("🧠 Advanced Player Comparison")

st.markdown(
    "Modern analytics-based multi-player scouting comparison."
)

# ==================================================
# TEAM LOGOS
# ==================================================

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

# ==================================================
# LOAD DATA
# ==================================================

df = pd.read_excel(
    "SDHL_Processed_2025_2026.xlsx"
)

# ==================================================
# CLEAN DATA
# ==================================================

df.columns = df.columns.str.strip()

text_cols = [
    "Player",
    "Team",
    "Position"
]

for col in text_cols:

    if col in df.columns:

        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
        )

# ==================================================
# NUMERIC CONVERSION
# ==================================================

numeric_cols = df.select_dtypes(
    include="number"
).columns

df[numeric_cols] = df[
    numeric_cols
].round(2)

# ==================================================
# SIDEBAR FILTERS
# ==================================================

st.sidebar.header("Filters")

# POSITION

positions = sorted(
    df["Position"]
    .dropna()
    .unique()
)

selected_position = st.sidebar.selectbox(
    "Position",
    positions
)

filtered_df = df[
    df["Position"] == selected_position
]

# TEAM FILTER

teams = sorted(
    filtered_df["Team"]
    .dropna()
    .unique()
)

selected_teams = st.sidebar.multiselect(
    "Teams",
    teams,
    default=teams
)

filtered_df = filtered_df[
    filtered_df["Team"].isin(
        selected_teams
    )
]

# TOI FILTER

min_toi = st.sidebar.slider(
    "Minimum TOI",
    min_value=0,
    max_value=3000,
    value=300,
    step=50
)

if "Time on ice" in filtered_df.columns:

    filtered_df = filtered_df[
        filtered_df["Time on ice"]
        >= min_toi
    ]

# ==================================================
# PLAYER SELECT
# ==================================================

all_players = sorted(
    filtered_df["Player"]
    .dropna()
    .unique()
)

selected_players = st.multiselect(

    "Select up to 5 players",

    options=all_players,

    default=all_players[:2],

    max_selections=5

)

# ==================================================
# COMPARISON METRICS
# ==================================================

comparison_metrics = [

    ("Points/60", "Points/60"),
    ("Shots/60", "Shots/60"),
    ("xG/60", "xG (Expected goals)/60"),
    ("Scoring Chances/60", "Scoring chances - total/60"),
    ("Slot Passes/60", "Passes to the slot/60")

]

# ==================================================
# CATEGORY RADAR
# ==================================================

radar_metrics = [

    "Shooting Score",
    "Playmaking Score",
    "Transition Score",
    "Puck Movement Score",
    "Defense Score",
    "Impact Score"

]

radar_labels = [

    "Shooting",
    "Playmaking",
    "Transition",
    "Puck Movement",
    "Defense",
    "Impact"

]

# ==================================================
# RADAR CHART
# ==================================================

if len(selected_players) >= 2:

    st.markdown("---")

    st.subheader("📊 Player Style Radar")

    radar_colors = [

        "#00E5FF",
        "#FF5252",
        "#22C55E",
        "#FACC15",
        "#A855F7"

    ]

    fig = go.Figure()

    for idx, player in enumerate(selected_players):

        player_row = filtered_df[
            filtered_df["Player"] == player
        ].iloc[0]

        radar_values = []

        for metric in radar_metrics:

            if metric in filtered_df.columns:

                radar_values.append(
                    player_row[metric]
                )

            else:

                radar_values.append(0)

        fig.add_trace(

            go.Scatterpolar(

                r=radar_values,

                theta=radar_labels,

                fill='toself',

                name=player,

                line=dict(
                    color=radar_colors[idx],
                    width=3
                ),

                fillcolor=f'rgba(255,255,255,0.05)'

            )

        )

    fig.update_layout(

        template="plotly_dark",

        polar=dict(

            radialaxis=dict(

                visible=True,

                range=[0, 100]

            )

        ),

        paper_bgcolor="#111111",

        plot_bgcolor="#111111",

        font=dict(
            color="white"
        ),

        height=700

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==================================================
# PLAYER HEADER CARDS
# ==================================================

if len(selected_players) >= 1:

    st.markdown("---")

    st.subheader("👤 Player Overview")

    cols = st.columns(
        len(selected_players)
    )

    for idx, player in enumerate(selected_players):

        row = filtered_df[
            filtered_df["Player"] == player
        ].iloc[0]

        with cols[idx]:

            if row["Team"] in team_logos:

                st.image(
                    team_logos[row["Team"]],
                    width=75
                )

            st.markdown(
                f"### {player}"
            )

            st.markdown(
                f"{row['Team']} | {row['Position']}"
            )

            if "Overall Score" in filtered_df.columns:

                st.metric(
                    "Overall Score",
                    round(
                        row["Overall Score"],
                        1
                    )
                )

            if (
                "Overall Score Percentile"
                in filtered_df.columns
            ):

                st.metric(
                    "League Percentile",
                    round(
                        row[
                            "Overall Score Percentile"
                        ]
                    )
                )

# ==================================================
# MULTI PLAYER COMPARISON
# ==================================================

if len(selected_players) >= 2:

    st.markdown("---")

    st.subheader("📈 Per/60 Comparison")

    comparison_rows = []

    for metric_label, metric_col in comparison_metrics:

        if metric_col not in filtered_df.columns:

            continue

        row_data = {}

        row_data["Metric"] = metric_label

        metric_values = []

        for player in selected_players:

            player_row = filtered_df[
                filtered_df["Player"] == player
            ].iloc[0]

            value = round(
                float(player_row[metric_col]),
                2
            )

            metric_values.append(value)

            row_data[player] = value

        max_value = max(metric_values)

        leader = selected_players[
            metric_values.index(max_value)
        ]

        row_data["Leader"] = leader

        comparison_rows.append(
            row_data
        )

    comparison_df = pd.DataFrame(
        comparison_rows
    )

    # ==================================================
    # HIGHLIGHT FUNCTION
    # ==================================================

    def highlight_leader(row):

        styles = []

        leader = row["Leader"]

        for col in comparison_df.columns:

            if col == "Leader":

                styles.append(
                    "background-color:#111827;color:#111827"
                )

            elif col == "Metric":

                styles.append(
                    "background-color:#0F172A;color:white;font-weight:bold"
                )

            elif col == leader:

                styles.append(
                    "background-color:#16A34A;color:white;font-weight:bold"
                )

            elif col in selected_players:

                styles.append(
                    "background-color:#7F1D1D;color:white"
                )

            else:

                styles.append("")

        return styles

    styled_df = comparison_df.style.apply(
        highlight_leader,
        axis=1
    )

    st.dataframe(

        styled_df,

        use_container_width=True,

        hide_index=True,

        height=400

    )

# ==================================================
# STYLE NOTES
# ==================================================

if len(selected_players) >= 1:

    st.markdown("---")

    st.subheader("🧠 Style Notes")

    for player in selected_players:

        row = filtered_df[
            filtered_df["Player"] == player
        ].iloc[0]

        notes = []

        # SHOOTER

        if (
            "Shots/60" in filtered_df.columns
            and
            row["Shots/60"]
            >= filtered_df[
                "Shots/60"
            ].quantile(0.75)
        ):

            notes.append(
                "High-volume shooter"
            )

        # PLAYMAKER

        if (
            "Passes to the slot/60"
            in filtered_df.columns
            and
            row[
                "Passes to the slot/60"
            ]
            >= filtered_df[
                "Passes to the slot/60"
            ].quantile(0.75)
        ):

            notes.append(
                "Strong playmaker"
            )

        # xG

        if (
            "xG (Expected goals)/60"
            in filtered_df.columns
            and
            row[
                "xG (Expected goals)/60"
            ]
            >= filtered_df[
                "xG (Expected goals)/60"
            ].quantile(0.75)
        ):

            notes.append(
                "Creates dangerous chances"
            )

        # SCORING CHANCES

        if (
            "Scoring chances - total/60"
            in filtered_df.columns
            and
            row[
                "Scoring chances - total/60"
            ]
            >= filtered_df[
                "Scoring chances - total/60"
            ].quantile(0.75)
        ):

            notes.append(
                "Constant offensive pressure"
            )

        # TRANSITION

        if (
            "Transition Score"
            in filtered_df.columns
            and
            row["Transition Score"]
            >= filtered_df[
                "Transition Score"
            ].quantile(0.75)
        ):

            notes.append(
                "Excellent transition player"
            )

        # IMPACT

        if (
            "Impact Score"
            in filtered_df.columns
            and
            row["Impact Score"]
            >= filtered_df[
                "Impact Score"
            ].quantile(0.75)
        ):

            notes.append(
                "Drives team impact"
            )

        if len(notes) == 0:

            notes.append(
                "Balanced player profile"
            )

        st.markdown(

            f"""
<div style="
background:#111827;
padding:18px;
border-radius:14px;
margin-bottom:14px;
border-left:6px solid #00E5FF;
">

<div style="
font-size:24px;
font-weight:800;
color:white;
">
{player}
</div>

<div style="
font-size:14px;
color:#D1D5DB;
margin-top:10px;
line-height:1.8;
">
{' | '.join(notes)}
</div>

</div>
""",

            unsafe_allow_html=True

        )

# ==================================================
# RAW TABLE
# ==================================================

if len(selected_players) >= 1:

    st.markdown("---")

    st.subheader("📋 Full Player Data")

    raw_metrics = [

        "Player",
        "Team",
        "Position",

        "Points/60",
        "Shots/60",
        "xG (Expected goals)/60",

        "Scoring chances - total/60",

        "Passes to the slot/60",

        "Transition Score",
        "Impact Score",
        "Overall Score"

    ]

    raw_metrics = [

        col for col in raw_metrics

        if col in filtered_df.columns

    ]

    raw_df = filtered_df[
        filtered_df["Player"].isin(
            selected_players
        )
    ][raw_metrics]

    st.dataframe(

        raw_df,

        use_container_width=True,

        hide_index=True,

        height=350

    )
