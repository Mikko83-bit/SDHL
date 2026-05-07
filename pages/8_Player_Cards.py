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

    # HANDLE MISSING VALUES

    if pd.isna(value):

        value = 0

    value = int(value)

    color = get_color(value)

    html = f"""
    <div style="
        background:{color};
        border-radius:16px;
        padding:18px;
        text-align:center;
        margin-bottom:16px;
        color:white;
        height:120px;
        display:flex;
        flex-direction:column;
        justify-content:center;
        align-items:center;
        box-shadow:0 4px 10px rgba(0,0,0,0.25);
    ">

        <div style="
            font-size:16px;
            font-weight:600;
            margin-bottom:8px;
        ">
            {title}
        </div>

        <div style="
            font-size:42px;
            font-weight:800;
            line-height:1;
        ">
            {value}
        </div>

        <div style="
            font-size:13px;
            margin-top:6px;
            opacity:0.9;
        ">
            Percentile
        </div>

    </div>
    """

    st.markdown(
        html,
        unsafe_allow_html=True
    )
