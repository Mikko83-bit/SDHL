
import streamlit as st
import pandas as pd
import plotly.express as px
import io

# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="SDHL Analytics",
    page_icon="🏒",
    layout="wide"
)

st.title("🏒 SDHL Analytics")
st.caption("Hockey Performance & Analytics Platform")

# ==================================================
# NAVIGATION
# ==================================================

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

# ==================================================
# EXCEL UPLOAD
# ==================================================

uploaded_file = st.file_uploader(
    "Upload InStat cumulative Excel file",
    type=["xlsx"]
)

if uploaded_file is None:
    st.info("Upload your InStat cumulative Excel file to begin.")
    st.stop()

# Read uploaded file as bytes
file_bytes = uploaded_file.getvalue()

# ==================================================
# LOAD EXCEL WORKBOOK
# ==================================================

try:
    excel = pd.ExcelFile(io.BytesIO(file_bytes))
    available_sheets = excel.sheet_names

except Exception as error:
    st.error("Could not read the Excel file.")
    st.exception(error)
    st.stop()


@st.cache_data
def load_sheet(file_bytes, sheet_name):
    return pd.read_excel(
        io.BytesIO(file_bytes),
        sheet_name=sheet_name
    )


def get_sheet(sheet_name):
    if sheet_name not in available_sheets:
        return None

    return load_sheet(file_bytes, sheet_name)


# ==================================================
# LOAD MAIN DATA
# ==================================================

teams = get_sheet("Teams SDHL")

if teams is None:
    st.error("The Excel file does not contain the 'Teams SDHL' sheet.")
    st.stop()

if "Team" not in teams.columns:
    st.error("The Teams SDHL sheet does not contain a Team column.")
    st.stop()


# ==================================================
# LEAGUE OVERVIEW
# ==================================================

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
        "Faceoffs won, %",
        "Faceoffs won in DZ, %",
        "Faceoffs won in NZ, %",
        "Faceoffs won in OZ, %"
    ]

    available_metrics = [
        metric
        for metric in available_metrics
        if metric in teams.columns
    ]

    if not available_metrics:
        st.warning("No supported team metrics were found.")
        st.stop()

    metric = st.selectbox(
        "Select metric",
        available_metrics
    )

    # Prepare chart data
    chart_data = teams[["Team", metric]].copy()

    # Convert percentage and numeric values
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

    # Horizontal bar chart
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
            r=60,
            t=20,
            b=40
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # Comparison table
    st.subheader("League Team Comparison")

    display_data = chart_data.copy()

    display_data[metric] = display_data[metric].round(2)

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )


# ==================================================
# TEAM ANALYTICS
# ==================================================

elif page == "Team Analytics":

    st.header("Team Analytics")

    team_names = sorted(
        teams["Team"].dropna().unique()
    )

    selected_team = st.selectbox(
        "Select team",
        team_names
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


# ==================================================
# PLAYER ANALYTICS
# ==================================================

elif page == "Player Analytics":

    st.header("Player Analytics")

    players = get_sheet("SDHL GAME SCORE")

    if players is None:
        st.warning("Player statistics sheet not found.")
        st.stop()

    required_columns = ["Team", "Player"]

    if not all(
        column in players.columns
        for column in required_columns
    ):
        st.error("Required player columns are missing.")
        st.stop()

    team_names = sorted(
        players["Team"].dropna().unique()
    )

    selected_team = st.selectbox(
        "Select team",
        team_names
    )

    team_players = players[
        players["Team"] == selected_team
    ]

    player_names = sorted(
        team_players["Player"].dropna().unique()
    )

    selected_player = st.selectbox(
        "Select player",
        player_names
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


# ==================================================
# GAME ANALYSIS
# ==================================================

elif page == "Game Analysis":

    st.header("Game Analysis")

    players = get_sheet("SDHL GAME SCORE")

    if players is None:
        st.warning("Player statistics sheet not found.")
        st.stop()

    if "Date" not in players.columns:
        st.warning("Date column not found.")
        st.stop()

    players["Date"] = pd.to_datetime(
        players["Date"],
        errors="coerce"
    )

    dates = sorted(
        players["Date"].dropna().unique(),
        reverse=True
    )

    if not dates:
        st.warning("No game dates found.")
        st.stop()

    selected_date = st.selectbox(
        "Select game date",
        dates,
        format_func=lambda date: pd.Timestamp(date).strftime("%Y-%m-%d")
    )

    game_data = players[
        players["Date"] == selected_date
    ]

    st.subheader(
        pd.Timestamp(selected_date).strftime("%Y-%m-%d")
    )

    st.dataframe(
        game_data,
        use_container_width=True,
        hide_index=True
    )


# ==================================================
# DATA CENTER
# ==================================================

elif page == "Data Center":

    st.header("Data Center")

    st.success("InStat Excel file loaded successfully.")

    st.subheader("Available sheets")

    st.write(available_sheets)

    selected_sheet = st.selectbox(
        "Select sheet",
        available_sheets
    )

    df = get_sheet(selected_sheet)

    if df is not None:

        st.write(f"Rows: {len(df)}")
        st.write(f"Columns: {len(df.columns)}")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
