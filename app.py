
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
    [
        "League Overview",
        "Team Analytics",
        "Player Analytics",
        "Game Analysis",
        "Data Center"
    ]
)

if page == "League Overview":
    st.header("League Overview")
    st.info("League statistics and team comparisons will appear here.")

elif page == "Team Analytics":
    st.header("Team Analytics")
    st.info("Team performance analysis will appear here.")

elif page == "Player Analytics":
    st.header("Player Analytics")
    st.info("Player statistics and comparisons will appear here.")

elif page == "Game Analysis":
    st.header("Game Analysis")
    st.info("Game-by-game analysis will appear here.")

elif page == "Data Center":
    st.header("Data Center")

    uploaded_file = st.file_uploader(
        "Upload InStat cumulative Excel file",
        type=["xlsx"]
    )

    if uploaded_file is not None:
        excel = pd.ExcelFile(uploaded_file)

        st.success("Excel file loaded successfully!")
        st.write("Available sheets:", excel.sheet_names)

        selected_sheet = st.selectbox(
            "Select sheet",
            excel.sheet_names
        )

        df = pd.read_excel(
            uploaded_file,
            sheet_name=selected_sheet
        )

        st.write(f"Rows: {len(df)}")
        st.dataframe(df, use_container_width=True)

