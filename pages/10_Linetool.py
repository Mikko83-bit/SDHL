import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

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
    "Plus/Minus",
    "Time on ice"

]

selected_sort = st.sidebar.selectbox(
    "Sort By",
    sort_options
)

# ==================================================
# FILTER DATA
# ==================================================

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
        return "#2563EB"

    elif value >= 48:
        return "#EAB308"

    else:
        return "#DC2626"

# ==================================================
# TITLE
# ==================================================

st.subheader("🔥 Best Line Combinations")

# ==================================================
# LINE CARDS
# ==================================================

for _, row in filtered_df.iterrows():

    gf_color = get_color(
        row["GF%"]
    )

    corsi_color = get_color(
        row["CORSI %"]
    )

    shot_color = get_color(
        row["Shot Share %"]
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    # ==================================================
    # GF%
    # ==================================================

    with c1:

        components.html(

            f"""
            <div style="
                background:{gf_color};
                border-radius:14px;
                padding:14px;
                height:150px;
                color:white;
                font-family:Arial;
            ">

                <div style="
                    font-size:18px;
                    font-weight:800;
                    margin-bottom:10px;
                ">
                    GF%
                </div>

                <div style="
                    font-size:38px;
                    font-weight:900;
                ">
                    {row['GF%']}%
                </div>

                <div style="
                    font-size:12px;
                    margin-top:10px;
                    line-height:1.4;
                ">
                    {row['Line']}
                </div>

            </div>
            """,

            height=165

        )

    # ==================================================
    # CORSI %
    # ==================================================

    with c2:

        components.html(

            f"""
            <div style="
                background:{corsi_color};
                border-radius:14px;
                padding:14px;
                height:150px;
                color:white;
                font-family:Arial;
            ">

                <div style="
                    font-size:18px;
                    font-weight:800;
                    margin-bottom:10px;
                ">
                    CORSI %
                </div>

                <div style="
                    font-size:38px;
                    font-weight:900;
                ">
                    {row['CORSI %']}%
                </div>

                <div style="
                    font-size:13px;
                    margin-top:10px;
                ">
                    TOI: {row['Time on ice']} min
                </div>

            </div>
            """,

            height=165

        )

    # ==================================================
    # SHOT SHARE
    # ==================================================

    with c3:

        components.html(

            f"""
            <div style="
                background:{shot_color};
                border-radius:14px;
                padding:14px;
                height:150px;
                color:white;
                font-family:Arial;
            ">

                <div style="
                    font-size:18px;
                    font-weight:800;
                    margin-bottom:10px;
                ">
                    Shot Share %
                </div>

                <div style="
                    font-size:38px;
                    font-weight:900;
                ">
                    {row['Shot Share %']}%
                </div>

                <div style="
                    font-size:13px;
                    margin-top:10px;
                ">
                    +/-: {row['Plus/Minus']}
                </div>

            </div>
            """,

            height=165

        )

    # ==================================================
    # GOALS / 60
    # ==================================================

    with c4:

        components.html(

            f"""
            <div style="
                background:#2563EB;
                border-radius:14px;
                padding:14px;
                height:150px;
                color:white;
                font-family:Arial;
            ">

                <div style="
                    font-size:18px;
                    font-weight:800;
                    margin-bottom:10px;
                ">
                    Goals/60
                </div>

                <div style="
                    font-size:38px;
                    font-weight:900;
                ">
                    {row['Goals/60']}
                </div>

                <div style="
                    font-size:13px;
                    margin-top:10px;
                ">
                    Goals: {row['Goals']}
                </div>

            </div>
            """,

            height=165

        )

    # ==================================================
    # SHOTS / 60
    # ==================================================

    with c5:

        components.html(

            f"""
            <div style="
                background:#7C3AED;
                border-radius:14px;
                padding:14px;
                height:150px;
                color:white;
                font-family:Arial;
            ">

                <div style="
                    font-size:18px;
                    font-weight:800;
                    margin-bottom:10px;
                ">
                    Shots/60
                </div>

                <div style="
                    font-size:38px;
                    font-weight:900;
                ">
                    {row['Shots/60']}
                </div>

                <div style="
                    font-size:13px;
                    margin-top:10px;
                ">
                    Shifts: {int(row['Numbers of shifts'])}
                </div>

            </div>
            """,

            height=165

        )

# ==================================================
# RAW DATA
# ==================================================

st.markdown("---")

with st.expander("View Raw Data"):

    st.dataframe(
        filtered_df,
        use_container_width=True
    )
