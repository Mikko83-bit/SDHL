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

st.title("📊 Advanced Player Comparison")

st.markdown(
    "Modern scouting comparison tool with per/60 analytics."
)

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
# NUMERIC ROUNDING
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

# POSITION FILTER

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
# METRICS
# ==================================================

comparison_metrics = [

    ("Points/60", "Points/60"),
    ("Shots/60", "Shots/60"),
    ("xG/60", "xG (Expected goals)/60"),
    ("Scoring Chances/60", "Scoring chances - total/60"),
    ("Slot Passes/60", "Passes to the slot/60")

]

# ==================================================
# RADAR METRICS
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

    st.subheader("🕸️ Style Radar")

    radar_colors = [

        "#00E5FF",
        "#22C55E",
        "#FACC15",
        "#EF4444",
        "#A855F7"

    ]

    fig = go.Figure()

    for idx, player in enumerate(selected_players):

        player_row = filtered_df[
            filtered_df["Player"] == player
        ].iloc[0]

        values = []

        for metric in radar_metrics:

            if metric in filtered_df.columns:

                values.append(
                    player_row[metric]
                )

            else:

                values.append(0)

        fig.add_trace(

            go.Scatterpolar(

                r=values,

                theta=radar_labels,

                fill='toself',

                name=player,

                line=dict(
                    width=3,
                    color=radar_colors[idx]
                ),

                fillcolor='rgba(255,255,255,0.04)'

            )

        )

    fig.update_layout(

        template="plotly_dark",

        paper_bgcolor="#0B1120",

        plot_bgcolor="#0B1120",

        font=dict(
            color="white"
        ),

        polar=dict(

            radialaxis=dict(

                visible=True,

                range=[0, 100]

            )

        ),

        height=650

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==================================================
# PLAYER HEADER
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

            st.markdown(

                f"""
<div style="
background:#111827;
padding:18px;
border-radius:16px;
text-align:center;
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
color:#CBD5E1;
margin-top:4px;
">
{row['Team']} | {row['Position']}
</div>

<div style="
font-size:40px;
font-weight:900;
color:#00E5FF;
margin-top:16px;
line-height:1;
">
{round(row['Overall Score'],1)}
</div>

<div style="
font-size:13px;
font-weight:700;
color:white;
margin-top:4px;
">
Overall Score
</div>

</div>
""",

                unsafe_allow_html=True

            )

# ==================================================
# COMPARISON TABLE
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

                float(
                    player_row[metric_col]
                ),

                1

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

    comparison_df = comparison_df.fillna("")

    # ==================================================
    # STYLE FUNCTION
    # ==================================================

    def highlight_leader(row):

        styles = []

        leader = row["Leader"]

        for col in comparison_df.columns:

            if col == "Leader":

                styles.append(
                    "background-color:#0B1120;color:#0B1120"
                )

            elif col == "Metric":

                styles.append(
                    "background-color:#020617;color:white;font-weight:700"
                )

            elif col == leader:

                styles.append(
                    "background-color:#16A34A;color:white;font-weight:800"
                )

            elif col in selected_players:

                styles.append(
                    "background-color:#1E293B;color:#CBD5E1"
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

        height=230

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

        # TRANSITION

        if (
            "Transition Score"
            in filtered_df.columns
            and
            row[
                "Transition Score"
            ]
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
            row[
                "Impact Score"
            ]
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
border-radius:16px;
margin-bottom:14px;
border-left:6px solid #00E5FF;
">

<div style="
font-size:22px;
font-weight:800;
color:white;
">
{player}
</div>

<div style="
font-size:14px;
color:#CBD5E1;
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
# RAW DATA
# ==================================================

if len(selected_players) >= 1:

    st.markdown("---")

    st.subheader("📋 Full Comparison Data")

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

    raw_df = raw_df.round(1)

    st.dataframe(

        raw_df,

        use_container_width=True,

        hide_index=True,

        height=320

    )
