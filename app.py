
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="SDHL Analytics",
    page_icon="🏒",
    layout="wide"
)

st.title("🏒 SDHL Analytics")
st.caption("Hockey Performance & Analytics Platform")

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select page",
    ["League Overview", "Team Analytics", "Player Analytics",
     "Game Analysis", "Data Center"]
)

uploaded_file = st.file_uploader(
    "Upload InStat cumulative Excel file",
    type=["xlsx"]
)

if uploaded_file is None:
    st.info("Upload your InStat cumulative Excel file to begin.")
    st.stop()

@st.cache_data
def load_sheet(file, sheet):
    return pd.read_excel(file, sheet_name=sheet)

teams = load_sheet(uploaded_file, "Teams SDHL")
players = load_sheet(uploaded_file, "SDHL GAME SCORE")

if page == "League Overview":
    st.header("League Overview")

    st.subheader("Team Performance")

    metric = st.selectbox(
        "Select metric",
        [
            "Goals",
            "xG (Expected goals)",
            "Net xG (xG - Opponent's xG)",
            "Shots",
            "Shots on goal",
            "Scoring chances",
            "CORSI%"
        ]
    )

    chart_data = teams[["Team", metric]].copy()

    if metric == "CORSI%":
        chart_data[metric] = (
            chart_data[metric].astype(str).str.replace("%", "", regex=False)
        )
        chart_data[metric] = pd.to_numeric(
            chart_data[metric], errors="coerce"
        )

    chart_data[metric] = pd.to_numeric(
        chart_data[metric], errors="coerce"
    )

    chart_data = chart_data.sort_values(metric, ascending=False)

    st.bar_chart(
        chart_data.set_index("Team"),
        horizontal=True
    )

    st.subheader("League Team Comparison")

    st.dataframe(
        chart_data,
        use_container_width=True,
        hide_index=True
    )

elif page == "Team Analytics":
    st.header("Team Analytics")

    team = st.selectbox("Select team", teams["Team"].unique())

    data = teams[teams["Team"] == team]

    st.dataframe(data, use_container_width=True, hide_index=True)

elif page == "Player Analytics":
    st.header("Player Analytics")
    st.info("Player analysis will be developed next.")

elif page == "Game Analysis":
    st.header("Game Analysis")
    st.info("Game analysis will be developed next.")

elif page == "Data Center":
    st.header("Data Center")

    st.success("InStat Excel file loaded successfully.")

    st.write("Available sheets:")
    st.write(pd.ExcelFile(uploaded_file).sheet_names)

    selected_sheet = st.selectbox(
        "Select sheet",
        pd.ExcelFile(uploaded_file).sheet_names
    )

    df = load_sheet(uploaded_file, selected_sheet)

    st.write(f"Rows: {len(df)}")
    st.dataframe(df, use_container_width=True)
