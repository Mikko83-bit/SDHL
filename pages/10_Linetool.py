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

# SHOTS ON GOAL / 60

df["Shots on Goal/60"] = (

    df["Shots on goal"] /
    df["Time on ice"]

) * 60

# ==================================================
# ROUND VALUES
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

# MINIMUM TOI

min_toi = st.sidebar.slider(

    "Minimum TOI",

    min_value=0,

    max_value=int(df["Time on ice"].max()),

    value=20,

    step=5

)

# MINIMUM SHIFTS

min_shifts = st.sidebar.slider(

    "Minimum Shifts",

    min_value=0,

    max_value=int(df["Numbers of shifts"].max()),

    value=50,

    step=10

)

# SORT OPTIONS

sort_options = [

    "GF%",
    "CORSI %",
    "Shot Share %",
    "Goals/60",
    "Shots/60",
    "Shots on Goal/60",
    "Plus/Minus",
    "Time on ice"

]

selected_sort = st.sidebar.selectbox(
    "Sort By",
    sort_options
)

# APPLY FILTERS

filtered_df = df[

    (df["Time on ice"] >= min_toi) &
    (df["Numbers of shifts"] >= min_shifts)

]

filtered_df = filtered_df.sort_values(
    by=selected_sort,
    ascending=False
)

# ==================================================
# COLOR FUNCTION
# ==================================================

def get_color(value):

    if value >= 60:
        return "#15803D"

    elif value >= 52:
        return "#4ADE80"

    elif value >= 48:
        return "#FACC15"

    else:
        return "#DC2626"

# ==================================================
# LINE CARD
# ==================================================

def line_card(row):

    gf_color = get_color(
        row["GF%"]
    )

    corsi_color = get_color(
        row["CORSI %"]
    )

    shot_color = get_color(
        row["Shot Share %"]
    )

    st.markdown(

        f"""
        <div style="
            background:#111827;
            padding:20px;
            border-radius:16px;
            margin-bottom:18px;
            border:1px solid #2D3748;
        ">

            <div style="
                font-size:24px;
                font-weight:800;
                color:white;
                margin-bottom:12px;
            ">
                {row['Line']}
            </div>

            <div style="
                font-size:14px;
                color:#CBD5E1;
                margin-bottom:18px;
            ">

                TOI: {row['Time on ice']} min |
                Shifts: {int(row['Numbers of shifts'])} |
                +/-: {int(row['Plus/Minus'])}

            </div>

            <div style="
                display:flex;
                flex-wrap:wrap;
                gap:12px;
            ">

                <div style="
                    background:{gf_color};
                    width:160px;
                    padding:12px;
                    border-radius:10px;
                ">

                    <div style="
                        color:white;
                        font-size:12px;
                        font-weight:700;
                    ">
                        GF%
                    </div>

                    <div style="
                        color:white;
                        font-size:30px;
                        font-weight:800;
                    ">
                        {row['GF%']}%
                    </div>

                </div>

                <div style="
                    background:{corsi_color};
                    width:160px;
                    padding:12px;
                    border-radius:10px;
                ">

                    <div style="
                        color:white;
                        font-size:12px;
                        font-weight:700;
                    ">
                        CORSI %
                    </div>

                    <div style="
                        color:white;
                        font-size:30px;
                        font-weight:800;
                    ">
                        {row['CORSI %']}%
                    </div>

                </div>

                <div style="
                    background:{shot_color};
                    width:160px;
                    padding:12px;
                    border-radius:10px;
                ">

                    <div style="
                        color:white;
                        font-size:12px;
                        font-weight:700;
                    ">
                        Shot Share %
                    </div>

                    <div style="
                        color:white;
                        font-size:30px;
                        font-weight:800;
                    ">
                        {row['Shot Share %']}%
                    </div>

                </div>

                <div style="
                    background:#2563EB;
                    width:160px;
                    padding:12px;
                    border-radius:10px;
                ">

                    <div style="
                        color:white;
                        font-size:12px;
                        font-weight:700;
                    ">
                        Goals/60
                    </div>

                    <div style="
                        color:white;
                        font-size:30px;
                        font-weight:800;
                    ">
                        {row['Goals/60']}
                    </div>

                </div>

                <div style="
                    background:#7C3AED;
                    width:160px;
                    padding:12px;
                    border-radius:10px;
                ">

                    <div style="
                        color:white;
                        font-size:12px;
                        font-weight:700;
                    ">
                        Shots/60
                    </div>

                    <div style="
                        color:white;
                        font-size:30px;
                        font-weight:800;
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
# BEST LINE COMBINATIONS
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
