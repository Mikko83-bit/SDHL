import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="SDHL Microstats Card",
    layout="wide"
)

# =========================
# LOAD DATA
# =========================

df = pd.read_excel(
    "SDHL_Player_Cards_Data.xlsx"
)

df.columns = df.columns.str.strip()

# =========================
# FILTERS
# =========================

st.sidebar.header("Filters")

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

players = sorted(
    filtered_df["Player"].dropna().unique()
)

selected_player = st.sidebar.selectbox(
    "Player",
    players
)

# =========================
# PLAYER DATA
# =========================

p = filtered_df[
    filtered_df["Player"] == selected_player
].iloc[0]

# =========================
# TITLE
# =========================

st.title("🏒 SDHL Microstats Card")

# =========================
# PLAYER INFO
# =========================

info_col1, info_col2 = st.columns([1, 4])

with info_col1:

    st.markdown(
        f"""
        ## {selected_player}

        ### {p['Team']}

        ### Position: {p['Position']}
        """
    )

with info_col2:

    st.empty()

# =========================
# COLOR FUNCTION
# =========================

def get_tile_color(value):

    if value >= 90:

        return "#1E3A5F"

    elif value >= 75:

        return "#3B82C4"

    elif value >= 50:

        return "#A7D0F2"

    elif value >= 30:

        return "#F7B7B7"

    else:

        return "#E63946"

# =========================
# TILE FUNCTION
# =========================

def stat_tile(title, value):

    if pd.isna(value):

        value = 0

    value = int(value)

    color = get_tile_color(value)

    html_code = f"""
    <div style="
        background:{color};
        border-radius:6px;
        padding:10px;
        height:95px;
        text-align:center;
        display:flex;
        flex-direction:column;
        justify-content:center;
        align-items:center;
        font-family:Arial;
        color:black;
        margin-bottom:10px;
    ">

        <div style="
            font-size:14px;
            margin-bottom:6px;
            font-weight:600;
        ">
            {title}
        </div>

        <div style="
            font-size:34px;
            font-weight:800;
            line-height:1;
        ">
            {value}%
        </div>

    </div>
    """

    components.html(
        html_code,
        height=105
    )

# =========================
# CATEGORY TITLES
# =========================

st.markdown("## Shooting")

shoot_col1, shoot_col2, shoot_col3, shoot_col4 = st.columns(4)

with shoot_col1:

    stat_tile(
        "Shots",
        p["Shooting Score Percentile"]
    )

with shoot_col2:

    stat_tile(
        "Chances",
        p["Impact Score Percentile"]
    )

with shoot_col3:

    stat_tile(
        "Slot Shots",
        p["Offensive Support Score Percentile"]
        if selected_position == "D"
        else p["Playmaking Score Percentile"]
    )

with shoot_col4:

    stat_tile(
        "Transition",
        p["Transition Score Percentile"]
    )

# =========================
# PASSES
# =========================

st.markdown("## Passing")

pass_col1, pass_col2, pass_col3, pass_col4 = st.columns(4)

with pass_col1:

    stat_tile(
        "Playmaking",
        p["Playmaking Score Percentile"]
        if selected_position == "F"
        else p["Offensive Support Score Percentile"]
    )

with pass_col2:

    stat_tile(
        "Possession",
        p["Possession Score Percentile"]
    )

with pass_col3:

    stat_tile(
        "Defense",
        p["Defense Score Percentile"]
    )

with pass_col4:

    stat_tile(
        "Impact",
        p["Impact Score Percentile"]
    )

# =========================
# TRANSITION
# =========================

st.markdown("## Transition")

trans_col1, trans_col2, trans_col3, trans_col4 = st.columns(4)

with trans_col1:

    stat_tile(
        "Entries",
        p["Transition Score Percentile"]
    )

with trans_col2:

    stat_tile(
        "Carry",
        p["Transition Score Percentile"]
    )

with trans_col3:

    stat_tile(
        "Breakouts",
        p["Puck Moving Score Percentile"]
        if selected_position == "D"
        else p["Transition Score Percentile"]
    )

with trans_col4:

    stat_tile(
        "Overall",
        p["Impact Score Percentile"]
    )

# =========================
# DEFENSE
# =========================

st.markdown("## Defense")

def_col1, def_col2, def_col3, def_col4 = st.columns(4)

with def_col1:

    stat_tile(
        "Defense",
        p["Defense Score Percentile"]
    )

with def_col2:

    stat_tile(
        "Possession",
        p["Possession Score Percentile"]
    )

with def_col3:

    stat_tile(
        "Impact",
        p["Impact Score Percentile"]
    )

with def_col4:

    stat_tile(
        "Overall",
        (
            p["Impact Score Percentile"] +
            p["Defense Score Percentile"]
        ) / 2
    )
