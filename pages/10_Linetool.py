import streamlit as st
import pandas as pd
import numpy as np

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Linetool",
    layout="wide"
)

st.title("⚡ WOWY Tool")
st.markdown(
    "With Or Without You analysis for 5v5 line chemistry."
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
    "Opponent shots total",
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

df["GA/60"] = (

    df["Opponent's goals"] /
    df["Time on ice"]

) * 60

df["Shots/60"] = (

    df["Shots"] /
    df["Time on ice"]

) * 60

# ==================================================
# ROUND
# ==================================================

num_cols = df.select_dtypes(
    include="number"
).columns

df[num_cols] = df[num_cols].round(2)

# ==================================================
# PARSE PLAYERS
# ==================================================

df["Players"] = df["Line"].apply(

    lambda x: [

        p.strip()

        for p in str(x).split(",")

    ]

)

# ==================================================
# ALL PLAYERS
# ==================================================

all_players = sorted(

    list(

        set(

            player

            for sublist in df["Players"]

            for player in sublist

        )

    )

)

# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.header("WOWY Filters")

selected_player = st.sidebar.selectbox(
    "Select Player",
    all_players
)

min_toi = st.sidebar.slider(

    "Minimum TOI",

    min_value=0,

    max_value=int(df["Time on ice"].max()),

    value=30,

    step=5

)

# ==================================================
# FILTER TOI
# ==================================================

df = df[
    df["Time on ice"] >= min_toi
]

# ==================================================
# WITH PLAYER
# ==================================================

with_player = df[

    df["Players"].apply(

        lambda x:

        selected_player in x

    )

]

# ==================================================
# WITHOUT PLAYER
# ==================================================

without_player = df[

    ~df["Players"].apply(

        lambda x:

        selected_player in x

    )

]

# ==================================================
# PLAYER SUMMARY
# ==================================================

st.subheader(f"🏒 {selected_player}")

summary1, summary2, summary3, summary4 = st.columns(4)

with summary1:

    st.metric(
        "Lines Played",
        len(with_player)
    )

with summary2:

    st.metric(
        "TOI",
        round(
            with_player["Time on ice"].sum(),
            1
        )
    )

with summary3:

    st.metric(
        "GF%",
        round(
            with_player["GF%"].mean(),
            1
        )
    )

with summary4:

    st.metric(
        "CORSI %",
        round(
            with_player["CORSI %"].mean(),
            1
        )
    )

st.markdown("---")

# ==================================================
# TEAMMATE CHEMISTRY
# ==================================================

teammate_results = []

for teammate in all_players:

    if teammate == selected_player:
        continue

    pair_df = with_player[

        with_player["Players"].apply(

            lambda x:

            teammate in x

        )

    ]

    if len(pair_df) == 0:
        continue

    toi = pair_df["Time on ice"].sum()

    gf = pair_df["GF%"].mean()

    corsi = pair_df["CORSI %"].mean()

    goals60 = pair_df["Goals/60"].mean()

    chemistry_score = (

        gf * 0.4 +

        corsi * 0.4 +

        goals60 * 5 +

        min(toi, 200) * 0.05

    )

    teammate_results.append({

        "Teammate": teammate,
        "TOI": round(toi,1),
        "GF%": round(gf,1),
        "CORSI %": round(corsi,1),
        "Goals/60": round(goals60,2),
        "Chemistry Score": round(chemistry_score,1)

    })

chem_df = pd.DataFrame(
    teammate_results
)

if not chem_df.empty:

    chem_df = chem_df.sort_values(
        by="Chemistry Score",
        ascending=False
    )

# ==================================================
# BEST TEAMMATES
# ==================================================

st.subheader("🔥 Best Teammates")

st.dataframe(

    chem_df,

    use_container_width=True,

    height=450

)

# ==================================================
# WITH VS WITHOUT
# ==================================================

st.markdown("---")

st.subheader("📊 With vs Without")

with_metrics = {

    "GF%":

        round(
            with_player["GF%"].mean(),
            1
        ),

    "CORSI %":

        round(
            with_player["CORSI %"].mean(),
            1
        ),

    "Goals/60":

        round(
            with_player["Goals/60"].mean(),
            2
        ),

    "Shots/60":

        round(
            with_player["Shots/60"].mean(),
            2
        )

}

without_metrics = {

    "GF%":

        round(
            without_player["GF%"].mean(),
            1
        ),

    "CORSI %":

        round(
            without_player["CORSI %"].mean(),
            1
        ),

    "Goals/60":

        round(
            without_player["Goals/60"].mean(),
            2
        ),

    "Shots/60":

        round(
            without_player["Shots/60"].mean(),
            2
        )

}

compare_df = pd.DataFrame({

    "Metric": list(with_metrics.keys()),

    "WITH Player": list(with_metrics.values()),

    "WITHOUT Player": list(without_metrics.values())

})

st.dataframe(

    compare_df,

    use_container_width=True

)

# ==================================================
# MOST USED LINES
# ==================================================

st.markdown("---")

st.subheader("⏱ Most Used Lines")

top_lines = with_player.sort_values(

    by="Time on ice",

    ascending=False

)[

    [

        "Line",
        "Time on ice",
        "Goals",
        "Opponent's goals",
        "GF%",
        "CORSI %",
        "Goals/60"

    ]

]

st.dataframe(

    top_lines,

    use_container_width=True,

    height=350

)
