# ==================================================
# GOALIE COMPARISON
# ==================================================

st.markdown("---")

st.subheader("⚔️ Goalie Comparison")

goalie_names = sorted(
    filtered_df["Player"].unique()
)

# ==================================================
# SELECT GOALIES
# ==================================================

g1, g2 = st.columns(2)

with g1:

    goalie1 = st.selectbox(
        "Goalie 1",
        goalie_names,
        key="goalie1_compare"
    )

with g2:

    goalie2 = st.selectbox(
        "Goalie 2",
        goalie_names,
        index=min(1, len(goalie_names)-1),
        key="goalie2_compare"
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
    ("xG per shot taken", "xG per shot taken")

]

# ==================================================
# LOWER IS BETTER
# ==================================================

lower_better = [

    "GA/60",
    "xGA/60",
    "xG per shot taken"

]

# ==================================================
# COLOR FUNCTION
# ==================================================

def get_colors(metric_name, value1, value2):

    if metric_name in lower_better:

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
# DISPLAY
# ==================================================

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
    # METRIC NAME
    # ==================================================

    with c1:

        metric_html = f"""
        <div style="
            background:#0F172A;
            border-radius:12px;
            height:85px;
            display:flex;
            align-items:center;
            justify-content:center;
            font-size:20px;
            font-weight:700;
            color:white;
            margin-bottom:10px;
        ">
            {metric_name}
        </div>
        """

        st.markdown(
            metric_html,
            unsafe_allow_html=True
        )

    # ==================================================
    # GOALIE 1
    # ==================================================

    with c2:

        goalie1_html = f"""
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
        """

        st.markdown(
            goalie1_html,
            unsafe_allow_html=True
        )

    # ==================================================
    # GOALIE 2
    # ==================================================

    with c3:

        goalie2_html = f"""
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
        """

        st.markdown(
            goalie2_html,
            unsafe_allow_html=True
        )
