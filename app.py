
import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="SDHL Analytics",
    page_icon="🏒",
    layout="wide"
)

st.title("🏒 SDHL Analytics")
st.caption("Hockey Performance & Analytics Platform")

# --------------------------------------------------
# NAVIGATION
# --------------------------------------------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select page",
    [
        "League Overview",
        "Team Analytics",
        "Player Analytics",
        "Game Analysis",
        "Data Center"
    ]
)

# --------------------------------------------------
# DATA UPLOAD
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload InStat cumulative Excel file",
    type=["xlsx"]
)

if uploaded_file is None:
    st.info("Upload your InStat cumulative Excel file to begin.")
    st.stop()

# --------------------------------------------------
# LOAD EXCEL DATA
# --------------------------------------------------

@st.cache_data
def load_sheet(file_bytes, sheet_name):
    return pd.read_excel(
        file_bytes,
        sheet_name=sheet_name
    )

file_bytes = uploaded_file.getvalue()

excel = pd.ExcelFile(file_bytes)
available_sheets = excel.sheet_names

if "Teams SDHL" not in available_sheets:
    st.error("The Excel file does not contain a 'Teams SDHL' sheet.")
    st.stop()

teams = load_sheet(file_bytes, "Teams SDHL")

# --------------------------------------------------
# LEAGUE OVERVIEW
# --------------------------------------------------

if page == "League Overview":

    st.header("League Overview")

    st.subheader("Team Performance")

    available_metrics = [
        "Goals",
        "xG (Expected goals)",
        "Net xG (xG - Opponent's xG)",
        "Shots",
        "Shots on goal",
        "Blocked shots",
        "Scoring chances",
        "CORSI%",
        "Faceoffs won, %"
    ]

    available_metrics = [
        metric for metric in available_metrics
        if metric in teams.columns
    ]

    metric = st.selectbox(
        "Select metric",
        available_metrics
    )

    # Prepare data
    chart_data = teams[["Team", metric]].copy()

    # Convert percentage values such as 62% into numbers
    chart_data[metric] = (
        chart_data[metric]
        .astype(str)
        .str.replace("%", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

    chart_data[metric] = pd.to_numeric(
        chart_data[metric],
        errors="coerce"
    )

    chart_data = chart_data.dropna(
        subset=[metric]
    )

    # Sort highest to lowest
    chart_data = chart_data.sort_values(
        by=metric,
        ascending=False
    ).reset_index(drop=True)

    # --------------------------------------------------
    # SORTED HORIZONTAL BAR CHART
    # --------------------------------------------------

    fig = px.bar(
        chart_data,
        x=metric,
        y="Team",
        orientation="h",
        text=metric,
        labels={
            metric: metric,
            "Team": ""
        }
    )

    fig.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside",
        cliponaxis=False
    )

    # Explicitly control team order:
    # Highest value at the top
    fig.update_yaxes(
        categoryorder="array",
        categoryarray=chart_data["Team"].tolist(),
        autorange="reversed"
    )

    fig.update_layout(
        height=500,
        showlegend=False,
        xaxis_title=metric,
        yaxis_title="",
        margin=dict(
            l=20,
            r=50,
            t=20,
            b=40
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------
    # TEAM COMPARISON TABLE
    # --------------------------------------------------

    st.subheader("League Team Comparison")

    display_data = chart_data.copy()

    display_data[metric] = display_data[metric].round(2)

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )

# --------------------------------------------------
# TEAM ANALYTICS
# --------------------------------------------------

elif page == "Team Analytics":

    st.header("Team Analytics")

    selected_team = st.selectbox(
        "Select team",
        sorted(teams["Team"].dropna().unique())
    )

    team_data = teams[
        teams["Team"] == selected_team
    ]

    st.subheader(selected_team)

    st.dataframe(
        team_data,
        use_container_width=True,
        hide_index=True
    )

# --------------------------------------------------
# PLAYER ANALYTICS
# --------------------------------------------------

elif page == "Player Analytics":

    st.header("Player Analytics")

    if "SDHL GAME SCORE" not in available_sheets:
        st.warning("Player statistics sheet not found.")

    else:

        players = load_sheet(
            file_bytes,
            "SDHL GAME SCORE"
        )

        selected_team = st.selectbox(
            "Select team",
            sorted(players["Team"].dropna().unique())
        )

        team_players = players[
            players["Team"] == selected_team
        ]

        selected_player = st.selectbox(
            "Select player",
            sorted(team_players["Player"].dropna().unique())
        )

        player_data = team_players[
            team_players["Player"] == selected_player
        ]

        st.subheader(selected_player)

        st.dataframe(
            player_data,
            use_container_width=True,
            hide_index=True
        )

# --------------------------------------------------
# GAME ANALYSIS
# --------------------------------------------------

elif page == "Game Analysis":

    st.header("Game Analysis")

    players = load_sheet(
        file_bytes,
        "SDHL GAME SCORE"
    )

    if "Date" in players.columns:

        dates = sorted(
            players["Date"].dropna().unique(),
            reverse=True
        )

        selected_date = st.selectbox(
            "Select game date",
            dates
        )

        game_data = players[
            players["Date"] == selected_date
        ]

        st.dataframe(
            game_data,
            use_container_width=True,
            hide_index=True
        )

# --------------------------------------------------
# DATA CENTER
# --------------------------------------------------

elif page == "Data Center":

    st.header("Data Center")

    st.success("InStat Excel file loaded successfully.")

    st.write("Available sheets:")

    st.write(available_sheets)

    selected_sheet = st.selectbox(
        "Select sheet",
        available_sheets
    )

    df = load_sheet(
        file_bytes,
        selected_sheet
    )

    st.write(f"Rows: {len(df)}")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

