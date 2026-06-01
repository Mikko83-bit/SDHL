# ==================================================
# DOWNLOAD FULL DATA
# ==================================================

from io import BytesIO

st.markdown("---")
st.subheader("📥 Download Full Dataset")

export_df = filtered_df.copy()

buffer = BytesIO()

with pd.ExcelWriter(
    buffer,
    engine="openpyxl"
) as writer:

    export_df.to_excel(
        writer,
        sheet_name="Relative Impact",
        index=False
    )

st.download_button(
    label="📥 Download Relative Impact Excel",
    data=buffer.getvalue(),
    file_name="Liiga_Relative_Impact.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
