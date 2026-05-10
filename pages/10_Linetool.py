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

df["GF%"] = (

    df["Goals"] /

    (
        df["Goals"] +
        df["Opponent's goals"]
    )

) * 100

df["Shot Share %"] = (

    df["Shots"] /

    (
        df["Shots"] +
        df["Opponent shots total"]
    )

) * 100

df["CORSI %"] = (

    df["CORSI+"] /

    (
        df["CORSI+"] +
        df["CORSI-"]
    )

) * 100

df["Goals/60"] = (

    df["Goals"] /
    df["Time on ice"]

) * 60

df["Shots/60"] = (

    df["Shots"] /
    df["Time on ice"]

) * 60

df["Shots Against/60"] = (

    df["Opponent shots total"] /
    df["Time on ice"]

) * 60

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

min_toi = st.sidebar.slider(

    "Minimum TOI",

    min_value=0,

    max_value=int(df["Time on ice"].max()),

    value=20,

    step=5

)

min_shifts = st.sidebar.slider(

    "Minimum Shifts",

    min_value=0,

    max_value=int(df["Numbers of shifts"].max()),

    value=50,

    step=10

)

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
        return "#3B82F6"

    elif value >= 48:
        return "#FACC15"

    else:
        return "#DC2626"

# ==================================================
# LINE CARDS
# ==================================================

st.subheader("🔥 Best Line Combinations")

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

    col1, col2, col3, col4, col5 = st.columns(5)

    # GF%

    with col1:

        st.markdown(
            f"""
            <div style="
                background:{gf_color};
                padding:14px;
                border-radius:12px;
                height:140px;
            ">

                <div style="
                    font-size:18px;
                    font-weight:800;
                    color:white;
                    margin-bottom:10px;
                ">
                    GF%
                </div>

                <div style="
                    font-size:36px;
                    font-weight:900;
                    color:white;
                ">
                    {row['GF%']}%
                </div>

                <div style="
                    font-size:13px;
                    color:white;
                    margin-top:8px;
                ">
                    {row['Line']}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    # CORSI

    with col2:

        st.markdown(
            f"""
            <div style="
                background:{corsi_color};
                padding:14px;
                border-radius:12px;
                height:140px;
            ">

                <div style="
                    font-size:18px;
                    font-weight:800;
                    color:white;
                    margin-bottom:10px;
                ">
                    CORSI %
                </div>

                <div style="
                    font-size:36px;
                    font-weight:900;
                    color:white;
                ">
                    {row['CORSI %']}%
                </div>

                <div style="
                    font-size:13px;
                    color:white;
                    margin-top:8px;
                ">
                    TOI: {row['Time on ice']} min
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    # SHOT SHARE

    with col3:

        st.markdown(
            f"""
            <div style="
                background:{shot_color};
                padding:14px;
                border-radius:12px;
                height:140px;
            ">

                <div style="
                    font-size:18px;
                    font-weight:800;
                    color:white;
                    margin-bottom:10px;
                ">
                    Shot Share %
                </div>

                <div style="
                    font-size:36px;
                    font-weight:900;
                    color:white;
                ">
                    {row['Shot Share %']}%
                </div>

                <div style="
                    font-size:13px;
                    color:white;
                    margin-top:8px;
                ">
                    +/-: {row['Plus/Minus']}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    # GOALS / 60

    with col4:

        st.markdown(
            f"""
            <div style="
                background:#2563EB;
                padding:14px;
                border-radius:12px;
                height:140px;
            ">

                <div style="
                    font-size:18px;
                    font-weight:800;
                    color:white;
                    margin-bottom:10px;
                ">
                    Goals/60
                </div>

                <div style="
                    font-size:36px;
                    font-weight:900;
                    color:white;
                ">
                    {row['Goals/60']}
                </div>

                <div style="
                    font-size:13px;
                    color:white;
                    margin-top:8px;
                ">
                    Goals: {row['Goals']}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    # SHOTS / 60

    with col5:

        st.markdown(
            f"""
            <div style="
                background:#7C3AED;
                padding:14px;
                border-radius:12px;
                height:140px;
            ">

                <div style="
                    font-size:18px;
                    font-weight:800;
                    color:white;
                    margin-bottom:10px;
                ">
                    Shots/60
                </div>

                <div style="
                    font-size:36px;
                    font-weight:900;
                    color:white;
                ">
                    {row['Shots/60']}
                </div>

                <div style="
                    font-size:13px;
                    color:white;
                    margin-top:8px;
                ">
                    Shifts: {int(row['Numbers of shifts'])}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("")

# ==================================================
# RAW DATA
# ==================================================

st.markdown("---")

with st.expander("View Raw Data"):

    st.dataframe(
        filtered_df,
        use_container_width=True
    )
