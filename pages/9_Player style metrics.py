import streamlit as st
import pandas as pd

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Player Style Metrics",
    layout="wide"
)

st.title("📊 Player Style Profile")

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

df["Position"] = (
    df["Position"]
    .astype(str)
    .str.strip()
)

df["Team"] = (
    df["Team"]
    .astype(str)
    .str.strip()
)

# ==================================================
# FIX OZ POSSESSION /60
# ==================================================

df["OZ possession/60"] = (

    df["OZ possession"] /
    df["Time on ice"]

) * 60

# ==================================================
# ROUND NUMBERS
# ==================================================

numeric_cols = df.select_dtypes(
    include="number"
).columns

df[numeric_cols] = df[numeric_cols].round(2)

# ==================================================
# SIDEBAR FILTERS
# ==================================================

st.sidebar.header("Filters")

# POSITION

positions = sorted(
    df["Position"].dropna().unique()
)

selected_position = st.sidebar.selectbox(
    "Position",
    positions
)

filtered_df = df[
    df["Position"] == selected_position
]

# TEAM

teams = sorted(
    filtered_df["Team"].dropna().unique()
)

selected_team = st.sidebar.selectbox(
    "Team",
    teams
)

# PLAYER

players = sorted(
    filtered_df[
        filtered_df["Team"] == selected_team
    ]["Player"].dropna().unique()
)

selected_player = st.sidebar.selectbox(
    "Player",
    players
)

# ==================================================
# PLAYER ROW
# ==================================================

p = filtered_df[
    filtered_df["Player"] == selected_player
].iloc[0]

# ==================================================
# HEADER
# ==================================================

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Player",
        selected_player
    )

with col2:

    st.metric(
        "Team",
        p["Team"]
    )

with col3:

    st.metric(
        "Position",
        p["Position"]
    )

st.markdown("---")

# ==================================================
# TABLE BUILDER
# ==================================================

def create_metric_table(metrics):

    rows = []

    for label, value_col, percentile_col in metrics:

        value = p.get(value_col, 0)

        percentile = p.get(percentile_col, 0)

        rows.append({

            "Metric": label,

            "Value": round(float(value), 2),

            "Percentile": round(float(percentile), 1)

        })

    metric_df = pd.DataFrame(rows)

    return metric_df

# ==================================================
# SHOOTING
# ==================================================

st.subheader("🔥 Shooting")

shooting_metrics = [

    (
        "Goals/60",
        "Goals/60",
        "Goals/60 Percentile"
    ),

    (
        "Shots/60",
        "Shots/60",
        "Shots/60 Percentile"
    ),

    (
        "xG/60",
        "xG (Expected goals)/60",
        "xG (Expected goals)/60 Percentile"
    ),

    (
        "Inner Slot Shots/60",
        "Inner slot shots - total/60",
        "Inner slot shots - total/60 Percentile"
    ),

    (
        "Scoring Chances/60",
        "Scoring chances - total/60",
        "Scoring chances - total/60 Percentile"
    )

]

shooting_df = create_metric_table(
    shooting_metrics
)

st.dataframe(
    shooting_df,
    use_container_width=True,
    hide_index=True
)

# ==================================================
# PLAYMAKING
# ==================================================

st.markdown("---")

st.subheader("🎯 Playmaking")

playmaking_metrics = [

    (
        "Pre-Shot Passes/60",
        "Pre-shots passes/60",
        "Pre-shots passes/60 Percentile"
    ),

    (
        "Slot Passes/60",
        "Passes to the slot/60",
        "Passes to the slot/60 Percentile"
    ),

    (
        "First Assists/60",
        "First assist/60",
        "First assist/60 Percentile"
    )

]

playmaking_df = create_metric_table(
    playmaking_metrics
)

st.dataframe(
    playmaking_df,
    use_container_width=True,
    hide_index=True
)

# ==================================================
# TRANSITION
# ==================================================

st.markdown("---")

st.subheader("🚀 Transition")

transition_metrics = [

    (
        "Entries via Carry/60",
        "Entries via stickhandling/60",
        "Entries via stickhandling/60 Percentile"
    ),

    (
        "Entries via Pass/60",
        "Entries via pass/60",
        "Entries via pass/60 Percentile"
    ),

    (
        "Breakouts via Carry/60",
        "Breakouts via stickhandling/60",
        "Breakouts via stickhandling/60 Percentile"
    ),

    (
        "Breakouts via Pass/60",
        "Breakouts via pass/60",
        "Breakouts via pass/60 Percentile"
    ),

    (
        "Breakouts/60",
        "Breakouts/60",
        "Breakouts/60 Percentile"
    )

]

transition_df = create_metric_table(
    transition_metrics
)

st.dataframe(
    transition_df,
    use_container_width=True,
    hide_index=True
)

# ==================================================
# POSSESSION
# ==================================================

st.markdown("---")

st.subheader("🏒 Possession")

possession_metrics = [

    (
        "Puck Touches/60",
        "Puck touches/60",
        "Puck touches/60 Percentile"
    ),

    (
        "OZ Possession/60",
        "OZ possession/60",
        "OZ possession/60 Percentile"
    )

]

possession_df = create_metric_table(
    possession_metrics
)

st.dataframe(
    possession_df,
    use_container_width=True,
    hide_index=True
)

# ==================================================
# DEFENSE
# ==================================================

st.markdown("---")

st.subheader("🛡️ Defense")

defense_metrics = [

    (
        "Takeaways/60",
        "Takeaways/60",
        "Takeaways/60 Percentile"
    ),

    (
        "DZ Takeaways",
        "Takeaways in DZ",
        "Takeaways in DZ Percentile"
    ),

    (
        "Opponent xG On-Ice",
        "Opponent's xG when on ice",
        "Opponent's xG when on ice Percentile"
    ),

    (
        "Puck Losses/60",
        "Puck losses/60",
        100 - p.get("Puck losses/60 Percentile", 0)
    )

]

# ==================================================
# SPECIAL DEFENSE TABLE
# ==================================================

defense_rows = []

for item in defense_metrics:

    if len(item) == 3 and isinstance(item[2], str):

        label, value_col, percentile_col = item

        percentile = p.get(percentile_col, 0)

    else:

        label, value_col, percentile = item

    defense_rows.append({

        "Metric": label,

        "Value": round(float(p.get(value_col, 0)), 2),

        "Percentile": round(float(percentile), 1)

    })

defense_df = pd.DataFrame(
    defense_rows
)

st.dataframe(
    defense_df,
    use_container_width=True,
    hide_index=True
)

# ==================================================
# IMPACT
# ==================================================

st.markdown("---")

st.subheader("📈 Impact")

impact_metrics = [

    (
        "Net xG",
        "Net xG (xG player on - opp. team's xG)",
        "Net xG (xG player on - opp. team's xG) Percentile"
    ),

    (
        "Team xG On-Ice",
        "Team xG when on ice",
        "Team xG when on ice Percentile"
    ),

    (
        "Overall Score",
        "Overall Score",
        "Overall Score Percentile"
    )

]

impact_df = create_metric_table(
    impact_metrics
)

st.dataframe(
    impact_df,
    use_container_width=True,
    hide_index=True
)
