import streamlit as st
import pandas as pd

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    layout="wide"
)

# =========================
# PAGE TITLE
# =========================

st.title("🏒 SDHL Player Cards")

# =========================
# LOAD DATA
# =========================

df = pd.read_excel(
    "SDHL_Player_Cards_Data.xlsx"
)

# =========================
# SIDEBAR FILTERS
# =========================

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

# PLAYER

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
# TEAM LOGOS
# =========================

team_logos = {

    "Lulea/MSSK": "images/Lulea.png"
}

# =========================
# COLOR FUNCTION
# =========================

def get_color(percentile):

    if percentile >= 90:

        return "#00C853"

    elif percentile >= 75:

        return "#64DD17"

    elif percentile >= 50:

        return "#FFD600"

    elif percentile >= 30:

        return "#FF9100"

    else:

        return "#FF1744"

# =========================
# SKILL BOX FUNCTION
# =========================

def skill_box(title, value):

    color = get_color(value)

    st.markdown(
        f"""
        <div style="
            background-color:{color};
            padding:25px;
            border-radius:18px;
            text-align:center;
            margin-bottom:20px;
            color:white;
            box-shadow:0px 4px 12px rgba(0,0,0,0.35);
        ">
            <h3 style="margin-bottom:10px;">
                {title}
            </h3>

            <h1 style="
                font-size:52px;
                margin:0;
            ">
                {int(value)}
            </h1>

            <p style="
                font-size:18px;
                margin-top:10px;
            ">
                Percentile
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================
# ARCHETYPE
# =========================

archetype = "Balanced Player"

# FORWARDS

if selected_position == "F":

    if p["Shooting Score Percentile"] >= 90:

        archetype = "Elite Finisher"

    elif p["Playmaking Score Percentile"] >= 90:

        archetype = "Offensive Playmaker"

    elif p["Transition Score Percentile"] >= 90:

        archetype = "Transition Driver"

    elif p["Possession Score Percentile"] >= 90:

        archetype = "Possession Forward"

    elif p["Defense Score Percentile"] >= 90:

        archetype = "Two-Way Forward"

# DEFENSEMEN

if selected_position == "D":

    if p["Puck Moving Score Percentile"] >= 90:

        archetype = "Puck-Moving Defenseman"

    elif p["Transition Score Percentile"] >= 90:

        archetype = "Transition Defenseman"

    elif p["Defense Score Percentile"] >= 90:

        archetype = "Shutdown Defenseman"

    elif p["Offensive Support Score Percentile"] >= 90:

        archetype = "Offensive Defenseman"

# =========================
# TOP SECTION
# =========================

left_col, right_col = st.columns([1, 3])

# =========================
# LEFT SIDE
# =========================

with left_col:

    # TEAM LOGO

    if p["Team"] in team_logos:

        st.image(
            team_logos[p["Team"]],
            width=140
        )

    # PLAYER INFO

    st.markdown(
        f"# {selected_player}"
    )

    st.markdown(
        f"### {p['Team']}"
    )

    st.markdown(
        f"### Position: {p['Position']}"
    )

    st.markdown("---")

    st.subheader("🧬 Archetype")

    st.success(archetype)

# =========================
# RIGHT SIDE
# =========================

with right_col:

    st.subheader("📊 Skill Profile")

    # FORWARDS

    if selected_position == "F":

        col1, col2, col3 = st.columns(3)

        with col1:

            skill_box(
                "Shooting",
                p["Shooting Score Percentile"]
            )

            skill_box(
                "Possession",
                p["Possession Score Percentile"]
            )

        with col2:

            skill_box(
                "Playmaking",
                p["Playmaking Score Percentile"]
            )

            skill_box(
                "Defense",
                p["Defense Score Percentile"]
            )

        with col3:

            skill_box(
                "Transition",
                p["Transition Score Percentile"]
            )

            skill_box(
                "Impact",
                p["Impact Score Percentile"]
            )

    # DEFENSEMEN

    if selected_position == "D":

        col1, col2, col3 = st.columns(3)

        with col1:

            skill_box(
                "Puck Moving",
                p["Puck Moving Score Percentile"]
            )

            skill_box(
                "Possession",
                p["Possession Score Percentile"]
            )

        with col2:

            skill_box(
                "Transition",
                p["Transition Score Percentile"]
            )

            skill_box(
                "Defense",
                p["Defense Score Percentile"]
            )

        with col3:

            skill_box(
                "Offensive Support",
                p["Offensive Support Score Percentile"]
            )

            skill_box(
                "Impact",
                p["Impact Score Percentile"]
            )

# =========================
# PLAYER SUMMARY
# =========================

st.markdown("---")

st.subheader("🔍 Automated Summary")

summary = []

# FORWARDS

if selected_position == "F":

    if p["Shooting Score Percentile"] >= 90:

        summary.append(
            "Elite shooting profile with dangerous scoring ability."
        )

    if p["Playmaking Score Percentile"] >= 75:

        summary.append(
            "Creates offensive opportunities consistently through passing and vision."
        )

    if p["Transition Score Percentile"] >= 75:

        summary.append(
            "Strong transition player capable of carrying play through the neutral zone."
        )

    if p["Defense Score Percentile"] >= 75:

        summary.append(
            "Positive defensive impact relative to league peers."
        )

# DEFENSEMEN

if selected_position == "D":

    if p["Puck Moving Score Percentile"] >= 90:

        summary.append(
            "Elite puck-moving defenseman with strong breakout ability."
        )

    if p["Transition Score Percentile"] >= 75:

        summary.append(
            "Drives transition play effectively from the defensive zone."
        )

    if p["Defense Score Percentile"] >= 75:

        summary.append(
            "Strong defensive impact player."
        )

    if p["Offensive Support Score Percentile"] >= 75:

        summary.append(
            "Provides consistent offensive support from the blue line."
        )

# DISPLAY SUMMARY

for line in summary:

    st.markdown(
        f"- {line}"
    )
