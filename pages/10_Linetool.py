import streamlit as st
import pandas as pd

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Line Chemistry",
    layout="wide"
)

st.title("⚡ Line Chemistry")

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
# CREATE ADVANCED METRICS
# ==================================================

# GOALS FOR %

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

# GOALS / 60

df["Goals/60"] = (

    df["Goals"] /
    df["Time on ice"]

) * 60

# GOALS AGAINST / 60

df["GA/60"] = (

    df["Opponent's goals"] /
    df["Time on ice"]

) * 60

# SHOTS / 60

df["Shots/60"] = (

    df["Shots"] /
    df["Time on ice"]

) * 60

# SHOTS AGAINST / 60

df["Shots Against/60"] = (

    df["Opponent shots total"] /
    df["Time on ice"]

) * 60

# ==================================================
# ROUND
# ==================================================

round_cols = df.select_dtypes(
    include="number"
).columns

df[round_cols] = df[round_cols].round(2)

# ==================================================
# SIDEBAR FILTERS
# ==================================================

st.sidebar.header("Filters")

# MINIMUM TOI

min_toi = st.sidebar.slider(

    "Minimum TOI",

    min_value=0,

    max_value=int(df["Time on ice"].max()),

    value=20,

    step=5

)

# FILTER

filtered_df = df[
    df["Time on ice"] >= min_toi
]

# SORT OPTION

sort_options = [

    "GF%",
    "CORSI %",
    "Goals/60",
    "Shot Share %",
    "Shots/60",
    "Plus/Minus",
    "Time on ice"

]

selected_sort = st.sidebar.selectbox(
    "Sort By",
    sort_options
)

filtered_df = filtered_df.sort_values(
    by=selected_sort,
    ascending=False
)

# ==================================================
# COLOR FUNCTIONS
# ==================================================

def get_color(value):

    if value >= 60:
        return "#1E8E3E"

    elif value >= 52:
        return "#4CAF50"

    elif value >= 48:
        return "#FBC02D"

    else:
        return "#C62828"

# ==================================================
# LINE CARD
# ==================================================

def line_card(row):

    corsi_color = get_color(
        row["CORSI %"]
    )

    gf_color = get_color(
        row["GF%"]
    )

    shot_color = get_color(
        row["Shot Share %"]
    )

    st.markdown(

        f"""
        <div style="
            background:#111827;
            padding:18px;
            border-radius:14px;
            margin-bottom:18px;
            border:1px solid #2A3441;
        ">

            <div style="
                font-size:22px;
                font-weight:800;
                color:white;
                margin-bottom:10px;
            ">
                {row['Line']}
            </div>

            <div style="
                color:#D1D5DB;
                font-size:14px;
                margin-bottom:14px;
            ">
                TOI: {row['Time on ice']} min |
                Shifts: {int(row['Numbers of shifts'])} |
                +/-: {int(row['Plus/Minus'])}
            </div>

            <div style="
                display:flex;
                gap:12px;
                flex-wrap:wrap;
            ">

                <div style="
                    background:{gf_color};
                    padding:10px;
                    border-radius:10px;
                    width:150px;
                ">

                    <div style="
                        font-size:12px;
                        color:white;
                        font-weight:700;
                    ">
                        GF%
                    </div>

                    <div style="
                        font-size:28px;
                        font-weight:800;
                        color:white;
                    ">
                        {row['GF%']}%
                    </div>

                </div>

                <div style="
                    background:{corsi_color};
                    padding:10px;
                    border-radius:10px;
                    width:150px;
                ">

                    <div style="
                        font-size:12px;
                        color:white;
                        font-weight:700;
                    ">
                        CORSI %
                    </div>

                    <div style="
                        font-size:28px;
                        font-weight:800;
                        color:white;
                    ">
                        {row['CORSI %']}%
                    </div>

                </div>

                <div style="
                    background:{shot_color};
                    padding:10px;
                    border-radius:10px;
                    width:150px;
                ">

                    <div style="
                        font-size:12px;
                        color:white;
                        font-weight:700;
                    ">
                        Shot Share %
                    </div>

                    <div style="
                        font-size:28px;
                        font-weight:800;
                        color:white;
                    ">
                        {row['Shot Share %']}%
                    </div>

                </div>

                <div style="
                    background:#2563EB;
                    padding:10px;
                    border-radius:10px;
                    width:150px;
                ">

                    <div style="
                        font-size:12px;
                        color:white;
                        font-weight:700;
                    ">
                        Goals/60
                    </div>

                    <div style="
                        font-size:28px;
                        font-weight:800;
                        color:white;
                    ">
                        {row['Goals/60']}
                    </div>

                </div>

                <div style="
                    background:#7C3AED;
                    padding:10px;
                    border-radius:10px;
                    width:150px;
                ">

                    <div style="
                        font-size:12px;
                        color:white;
                        font-weight:700;
                    ">
                        Shots/60
                    </div>

                    <div style="
                        font-size:28px;
                        font-weight:800;
                        color:white;
                    ">
                        {row['Shots/60']}
                    </div>

                </div>

            </div>

        </div>
        """,

        unsafe_allow_html=True

    )

# ==================================================
# TOP LINES
# ==================================================

st.subheader("🔥 Best Line Combinations")

for _, row in filtered_df.iterrows():

    line_card(row)

# ==================================================
# RAW DATA
# ==================================================

st.markdown("---")

with st.expander("View Raw Data"):

    st.dataframe(
        filtered_df,
        use_container_width=True
    )
