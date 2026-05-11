import streamlit as st
import pandas as pd

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="xGSA",
    layout="wide"
)

st.title("🥅 Goalie Comparison")

# ==================================================
# LOAD DATA
# ==================================================

df = pd.read_excel(
    "Goalies - Sdhl 2025-2026.xlsx"
)

# ==================================================
# CLEAN COLUMNS
# ==================================================

df.columns = df.columns.str.strip()

# ==================================================
# TOI TO MINUTES
# ==================================================

def toi_to_minutes(toi):

    try:

        parts = str(toi).split(":")

        if len(parts) == 3:

            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])

            return (

                hours * 60 +

                minutes +

                seconds / 60

            )

        elif len(parts) == 2:

            minutes = int(parts[0])
            seconds = int(parts[1])

            return (

                minutes +

                seconds / 60

            )

        return 0

    except:

        return 0

# ==================================================
# TOI MINUTES
# ==================================================

df["TOI Minutes"] = df[
    "Time on ice"
].apply(toi_to_minutes)

# ==================================================
# NUMERIC COLUMNS
# ==================================================

numeric_cols = [

    "Games played",
    "xGSA",
    "Goals against",
    "Shots on goal",
    "Saves",
    "xG conceded",
    "xG per shot taken"

]

for col in numeric_cols:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# ==================================================
# SAVE %
# ==================================================

df["Save %"] = (

    df["Saves"] /

    df["Shots on goal"]

) * 100

# ==================================================
# PER 60 STATS
# ==================================================

df["GA/60"] = (

    df["Goals against"] /

    df["TOI Minutes"]

) * 60

df["Saves/60"] = (

    df["Saves"] /

    df["TOI Minutes"]

) * 60

df["Shots Against/60"] = (

    df["Shots on goal"] /

    df["TOI Minutes"]

) * 60

df["xGA/60"] = (

    df["xG conceded"] /

    df["TOI Minutes"]

) * 60

# ==================================================
# ROUND VALUES
# ==================================================

num_cols = df.select_dtypes(
    include="number"
).columns

df[num_cols] = df[
    num_cols
].round(2)

# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.header("Filters")

min_games = st.sidebar.slider(

    "Minimum Games Played",

    min_value=1,

    max_value=int(df["Games played"].max()),

    value=5

)

filtered_df = df[
    df["Games played"] >= min_games
]

# ==================================================
# GOALIE SELECT
# ==================================================

goalies = sorted(
    filtered_df["Player"].unique()
)

col1, col2 = st.columns(2)

with col1:

    goalie1 = st.selectbox(
        "Goalie 1",
        goalies
    )

with col2:

    goalie2 = st.selectbox(
        "Goalie 2",
        goalies,
        index=1
    )

# ==================================================
# PLAYER ROWS
# ==================================================

p1 = filtered_df[
    filtered_df["Player"] == goalie1
].iloc[0]

p2 = filtered_df[
    filtered_df["Player"] == goalie2
].iloc[0]

# ==================================================
# METRICS
# ==================================================

comparison_metrics = [

    ("xGSA", "xGSA"),
    ("Save %", "Save %"),
    ("GA/60", "GA/60"),
    ("Saves/60", "Saves/60"),
    ("Shots Against/60", "Shots Against/60"),
    ("xGA/60", "xGA/60"),
    ("xG per shot", "xG per shot taken")

]

# ==================================================
# LOWER BETTER METRICS
# ==================================================

lower_better = [

    "GA/60",
    "xGA/60",
    "xG per shot"

]

# ==================================================
# COLOR FUNCTION
# ==================================================

def get_colors(metric, value1, value2):

    if metric in lower_better:

        if value1 < value2:

            return "#16A34A", "#DC2626"

        elif value2 < value1:

            return "#DC2626", "#16A34A"

    else:

        if value1 > value2:

            return "#16A34A", "#DC2626"

        elif value2 > value1:

            return "#DC2626", "#16A34A"

    return "#374151", "#374151"

# ==================================================
# COMPARISON TABLE
# ==================================================

st.markdown("---")

for metric_name, column_name in comparison_metrics:

    value1 = round(
        float(p1[column_name]),
        2
    )

    value2 = round(
        float(p2[column_name]),
        2
    )

    color1, color2 = get_colors(
        metric_name,
        value1,
        value2
    )

    c1, c2, c3 = st.columns([1.2, 2, 2])

    # ==================================================
    # METRIC
    # ==================================================

    with c1:

        st.markdown(
            f"""
            <div style="
                background:#0F172A;
                border-radius:12px;
                height:85px;
                display:flex;
                justify-content:center;
                align-items:center;
                font-size:18px;
                font-weight:700;
                color:white;
                margin-bottom:10px;
            ">
                {metric_name}
            </div>
            """,
            unsafe_allow_html=True
        )

    # ==================================================
    # GOALIE 1
    # ==================================================

    with c2:

        st.markdown(
            f"""
            <div style="
                background:{color1};
                border-radius:12px;
                padding:12px;
                height:85px;
                margin-bottom:10px;
            ">

                <div style="
                    font-size:13px;
                    color:white;
                    font-weight:700;
                ">
                    {goalie1}
                </div>

                <div style="
                    font-size:34px;
                    font-weight:800;
                    color:white;
                    line-height:1;
                    margin-top:8px;
                ">
                    {value1}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    # ==================================================
    # GOALIE 2
    # ==================================================

    with c3:

        st.markdown(
            f"""
            <div style="
                background:{color2};
                border-radius:12px;
                padding:12px;
                height:85px;
                margin-bottom:10px;
            ">

                <div style="
                    font-size:13px;
                    color:white;
                    font-weight:700;
                ">
                    {goalie2}
                </div>

                <div style="
                    font-size:34px;
                    font-weight:800;
                    color:white;
                    line-height:1;
                    margin-top:8px;
                ">
                    {value2}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )
