import streamlit as st
import pandas as pd

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Linetool",
    layout="wide"
)

st.title("⚡ Linetool")

st.markdown(
    "Modern 5v5 line chemistry and lineup impact dashboard."
)

# ==================================================
# LOAD DATA
# ==================================================

df = pd.read_excel(
    "Lines - Lulea HF 2025-2026.xlsx"
)

# ==================================================
# CLEAN DATA
# ==================================================

df.columns = df.columns.str.strip()

numeric_cols = [

    "Plus/Minus",
    "Numbers of shifts",
    "Time on ice",
    "Goals",
    "Opponent's goals",
    "Shots",
    "Shots on goal",
    "Opponent shots total",
    "Shots on goal against",
    "CORSI",
    "CORSI+",
    "CORSI-"

]

for col in numeric_cols:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# ==================================================
# ADVANCED METRICS
# ==================================================

# GF%

df["GF%"] = (

    df["Goals"] /

    (
        df["Goals"] +
        df["Opponent's goals"]
    )

) * 100

# SHOT SHARE %

df["Shot Share %"] = (

    df["Shots"] /

    (
        df["Shots"] +
        df["Opponent shots total"]
    )

) * 100

# CORSI %

df["CORSI %"] = (

    df["CORSI+"] /

    (
        df["CORSI+"] +
        df["CORSI-"]
    )

) * 100

# GOALS/60

df["Goals/60"] = (

    df["Goals"] /
    df["Time on ice"]

) * 60

# GA/60

df["GA/60"] = (

    df["Opponent's goals"] /
    df["Time on ice"]

) * 60

# SHOTS/60

df["Shots/60"] = (

    df["Shots"] /
    df["Time on ice"]

) * 60

# SHOTS AGAINST/60

df["Shots Against/60"] = (

    df["Opponent shots total"] /
    df["Time on ice"]

) * 60

# NET GOALS

df["Goal Differential"] = (

    df["Goals"] -
    df["Opponent's goals"]

)

# ==================================================
# ROUND
# ==================================================

numeric_round = df.select_dtypes(
    include="number"
).columns

df[numeric_round] = df[
    numeric_round
].round(2)

# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.header("Filters")

# TOI FILTER

min_toi = st.sidebar.slider(

    "Minimum TOI",

    min_value=0,

    max_value=int(df["Time on ice"].max()),

    value=50,

    step=5

)

# SHIFTS FILTER

min_shifts = st.sidebar.slider(

    "Minimum Shifts",

    min_value=0,

    max_value=int(df["Numbers of shifts"].max()),

    value=100,

    step=10

)

# SEARCH PLAYER

search_player = st.sidebar.text_input(
    "Search Player"
)

# SORT OPTION

sort_options = [

    "GF%",
    "CORSI %",
    "Shot Share %",
    "Goals/60",
    "Shots/60",
    "Goal Differential",
    "Plus/Minus",
    "Time on ice"

]

selected_sort = st.sidebar.selectbox(
    "Sort By",
    sort_options
)

# ==================================================
# APPLY FILTERS
# ==================================================

filtered_df = df[

    (df["Time on ice"] >= min_toi) &
    (df["Numbers of shifts"] >= min_shifts)

]

# PLAYER SEARCH

if search_player:

    filtered_df = filtered_df[

        filtered_df["Line"]
        .str.contains(
            search_player,
            case=False,
            na=False
        )

    ]

# SORT

filtered_df = filtered_df.sort_values(
    by=selected_sort,
    ascending=False
)

# ==================================================
# DISPLAY TABLE
# ==================================================

display_cols = [

    "Line",
    "Time on ice",
    "Numbers of shifts",
    "Goals",
    "Opponent's goals",
    "Goal Differential",
    "GF%",
    "CORSI %",
    "Shot Share %",
    "Goals/60",
    "GA/60",
    "Shots/60",
    "Shots Against/60",
    "Plus/Minus"

]

table_df = filtered_df[
    display_cols
].copy()

# ==================================================
# STYLE FUNCTION
# ==================================================

def color_scale(val):

    if pd.isna(val):
        return ""

    # ELITE

    if val >= 60:
        return "background-color: #15803D; color: white"

    # GOOD

    elif val >= 52:
        return "background-color: #2563EB; color: white"

    # AVERAGE

    elif val >= 48:
        return "background-color: #CA8A04; color: white"

    # BAD

    else:
        return "background-color: #DC2626; color: white"

# ==================================================
# STYLED TABLE
# ==================================================

styled_table = table_df.style.map(

    color_scale,

    subset=[

        "GF%",
        "CORSI %",
        "Shot Share %"

    ]

)

# ==================================================
# TOP STATS
# ==================================================

top1, top2, top3, top4 = st.columns(4)

with top1:

    st.metric(
        "Lines",
        len(filtered_df)
    )

with top2:

    st.metric(
        "Best GF%",
        round(filtered_df["GF%"].max(),1)
    )

with top3:

    st.metric(
        "Best CORSI %",
        round(filtered_df["CORSI %"].max(),1)
    )

with top4:

    st.metric(
        "Highest TOI",
        round(filtered_df["Time on ice"].max(),1)
    )

st.markdown("---")

# ==================================================
# MAIN TABLE
# ==================================================

st.subheader("🔥 Line Combination Rankings")

st.dataframe(

    styled_table,

    use_container_width=True,

    height=900

)

# ==================================================
# RAW DATA
# ==================================================

with st.expander("View Full Raw Data"):

    st.dataframe(
        filtered_df,
        use_container_width=True
    )
