import io
import re
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# SDHL ANALYTICS | Streamlit application
# ============================================================

st.set_page_config(
    page_title="SDHL Analytics",
    page_icon="🏒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Visual system ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

:root {
    --bg: #0b1020;
    --panel: #121a2b;
    --panel2: #172237;
    --line: rgba(148,163,184,.16);
    --muted: #91a0b8;
    --text: #edf3ff;
    --accent: #65aefc;
    --accent2: #38d6c5;
}
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: radial-gradient(ellipse at 12% 0%, #182844 0%, #0b1020 48%, #090e19 100%); color: var(--text); }
[data-testid="stHeader"] { background: rgba(11,16,32,.88); }
[data-testid="stSidebar"] { background: #0e1728; border-right: 1px solid var(--line); }
[data-testid="stSidebar"] * { color: var(--text); }
.block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1600px; }
h1,h2,h3 { font-family: 'Manrope', sans-serif !important; letter-spacing: -.03em; color: var(--text); }
h1 { font-size: 2.1rem !important; font-weight: 800 !important; }
h2 { font-size: 1.35rem !important; font-weight: 700 !important; }
h3 { font-size: 1.05rem !important; font-weight: 700 !important; }
p, label, span { color: inherit; }
[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(26,39,62,.96), rgba(17,27,44,.96));
    border: 1px solid var(--line); border-radius: 14px;
    padding: 16px 18px; min-height: 112px;
}
[data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: .82rem !important; }
[data-testid="stMetricValue"] { color: var(--text) !important; font-family: 'Manrope'; font-weight: 800; }
[data-testid="stMetricDelta'] { color: var(--accent2) !important; }
div[data-testid="stDataFrame"], div[data-testid="stTable"] {
    border: 1px solid var(--line); border-radius: 12px; overflow: hidden;
}
.stSelectbox > div > div, .stMultiSelect > div > div {
    background: #172237; border-color: var(--line); border-radius: 9px;
}
.stFileUploader section { background: #121d30; border: 1px dashed #456080; border-radius: 12px; }
.stButton button {
    background: linear-gradient(90deg, #3188e8, #47b7e8);
    color: white; border: 0; border-radius: 9px; font-weight: 700;
}
hr { border-color: var(--line); }
.eyebrow { color: #7fa9d8; text-transform: uppercase; letter-spacing: .14em; font-size: .68rem; font-weight: 700; }
.hero {
    background: linear-gradient(115deg, rgba(30,62,99,.82), rgba(17,31,51,.94) 62%, rgba(18,45,57,.82));
    border: 1px solid rgba(120,170,220,.24); border-radius: 18px;
    padding: 24px 28px; margin-bottom: 22px;
}
.hero-title { font-family: 'Manrope'; font-size: 1.9rem; font-weight: 800; color: #f3f7ff; }
.hero-sub { color: #a8bad2; margin-top: 5px; font-size: .92rem; }
.section-head { display:flex; align-items:center; justify-content:space-between; margin: 20px 0 10px; }
.small-muted { color: var(--muted); font-size: .8rem; }
.pill {
    display:inline-block; padding:4px 9px; border-radius:999px;
    background:rgba(56,214,197,.12); color:#6ce5d5; font-size:.72rem; font-weight:700;
    border:1px solid rgba(56,214,197,.22);
}
</style>
""", unsafe_allow_html=True)

# ---------- Helpers ----------
def read_excel_sheet(file_bytes, sheet_name):
    return pd.read_excel(io.BytesIO(file_bytes), sheet_name=sheet_name)

def numeric_series(series):
    return pd.to_numeric(
        series.astype(str).str.replace("%", "", regex=False).str.replace(",", ".", regex=False),
        errors="coerce"
    )

def safe_sum(df, column):
    if column not in df.columns:
        return None
    return pd.to_numeric(df[column], errors="coerce").sum(min_count=1)

def fmt_num(value, digits=1):
    if value is None or pd.isna(value):
        return "—"
    return f"{value:,.{digits}f}"

def format_date(value):
    try:
        return pd.Timestamp(value).strftime("%d %b %Y")
    except Exception:
        return str(value)

def normalize_toi(value):
    """Convert InStat mm:ss or numeric TOI values to minutes where possible."""
    if pd.isna(value):
        return None
    s = str(value).strip()
    if ":" in s:
        parts = s.split(":")
        try:
            if len(parts) == 2:
                return int(parts[0]) + int(parts[1]) / 60
            if len(parts) == 3:
                return int(parts[0]) * 60 + int(parts[1]) + int(parts[2]) / 60
        except ValueError:
            return None
    try:
        return float(s.replace(",", "."))
    except ValueError:
        return None

def section_title(title, note=None):
    st.markdown(f'<div class="section-head"><h2 style="margin:0">{title}</h2>'
                + (f'<span class="small-muted">{note}</span>' if note else '')
                + '</div>', unsafe_allow_html=True)

def metric_card(label, value, help_text=None):
    st.metric(label, value, help=help_text)

def chart_theme(fig, height=390):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(l=12, r=18, t=24, b=28),
        font=dict(family="DM Sans", color="#dce7f7", size=12),
        xaxis=dict(gridcolor="rgba(148,163,184,.12)", zerolinecolor="rgba(148,163,184,.15)"),
        yaxis=dict(gridcolor="rgba(148,163,184,.08)", zerolinecolor="rgba(148,163,184,.15)"),
    )
    return fig

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown('<div class="eyebrow">Performance intelligence</div>', unsafe_allow_html=True)
    st.markdown("## 🏒 SDHL Analytics")
    st.caption("League • Teams • Players • Games")
    st.divider()
    page = st.radio(
        "WORKSPACE",
        ["League Overview", "Team Analytics", "Player Analytics",
         "Game Analysis", "Playing Style", "Data Center"],
        label_visibility="visible"
    )
    st.divider()
    st.markdown('<span class="small-muted">DATA SOURCE</span>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload InStat cumulative Excel", type=["xlsx"])
    st.caption("Upload the latest cumulative export. Data is available for this app session.")

# ---------- Data load ----------
if uploaded_file is None:
    st.markdown("""
    <div class="hero">
      <div class="eyebrow">SDHL performance platform</div>
      <div class="hero-title">Turn game data into better decisions.</div>
      <div class="hero-sub">Upload the latest InStat cumulative workbook to explore league, team, player and game performance.</div>
    </div>
    """, unsafe_allow_html=True)
    st.info("Upload the InStat Excel file in the left sidebar to begin.")
    st.stop()

file_bytes = uploaded_file.getvalue()
try:
    workbook = pd.ExcelFile(io.BytesIO(file_bytes))
    sheets = workbook.sheet_names
except Exception as exc:
    st.error("The uploaded file could not be read as an Excel workbook.")
    st.exception(exc)
    st.stop()

@st.cache_data(show_spinner=False)
def cached_sheet(data, sheet):
    return pd.read_excel(io.BytesIO(data), sheet_name=sheet)

def get_sheet(name):
    if name not in sheets:
        return None
    return cached_sheet(file_bytes, name)

teams = get_sheet("Teams SDHL")
players = get_sheet("SDHL GAME SCORE")
faceoffs = get_sheet("Faceoffs")
puck = get_sheet("Puck management")
lines = get_sheet("Forward lines")

if teams is None or "Team" not in teams.columns:
    st.error("Required sheet 'Teams SDHL' or its Team column is missing.")
    st.stop()

teams = teams.copy()
for col in teams.columns:
    if col != "Team":
        teams[col] = numeric_series(teams[col])

# ---------- Header ----------
st.markdown(f"""
<div class="hero">
  <div class="eyebrow">SDHL • Season performance</div>
  <div class="hero-title">{page}</div>
  <div class="hero-sub">InStat data workspace &nbsp; <span class="pill">{len(teams)} teams detected</span>
  &nbsp; <span class="pill">{len(players) if players is not None else 0:,} player-game rows</span></div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# LEAGUE OVERVIEW
# ============================================================
if page == "League Overview":
    st.markdown("### League snapshot")
    kpi_cols = st.columns(4)
    kpis = [
        ("Teams", len(teams), "Teams in current workbook"),
        ("Goals", safe_sum(teams, "Goals"), "Team totals in Teams SDHL"),
        ("Expected goals", safe_sum(teams, "xG (Expected goals)"), "Team xG totals"),
        ("Shots", safe_sum(teams, "Shots"), "Team shot totals"),
    ]
    for col, (label, value, help_text) in zip(kpi_cols, kpis):
        with col:
            metric_card(label, fmt_num(value, 0), help_text)

    section_title("Team performance ranking", "Select a metric to rank all teams")
    metric_options = [
        "Goals", "xG (Expected goals)", "Net xG (xG - Opponent's xG)",
        "Shots", "Shots on goal", "Scoring chances", "CORSI%",
        "Faceoffs won, %", "Hits", "Blocked shots"
    ]
    metric_options = [m for m in metric_options if m in teams.columns]
    if metric_options:
        selected_metric = st.selectbox("Ranking metric", metric_options, key="league_metric")
        rank = teams[["Team", selected_metric]].copy()
        rank[selected_metric] = numeric_series(rank[selected_metric])
        rank = rank.dropna(subset=[selected_metric]).sort_values(selected_metric, ascending=False)
        left, right = st.columns([1.65, 1])
        with left:
            fig = px.bar(rank, x=selected_metric, y="Team", orientation="h",
                         text=selected_metric, color=selected_metric,
                         color_continuous_scale=["#243c5a", "#3188e8", "#46d6c5"])
            fig.update_traces(texttemplate="%{text:.1f}", textposition="outside", cliponaxis=False)
            fig.update_yaxes(categoryorder="array", categoryarray=rank["Team"].tolist(), autorange="reversed")
            fig.update_coloraxes(showscale=False)
            chart_theme(fig, 440)
            fig.update_layout(xaxis_title=selected_metric, yaxis_title="", margin=dict(l=8,r=45,t=18,b=25))
            st.plotly_chart(fig, use_container_width=True)
        with right:
            st.markdown("#### Ranking")
            table = rank.reset_index(drop=True).copy()
            table.insert(0, "Rank", range(1, len(table) + 1))
            table[selected_metric] = table[selected_metric].round(2)
            st.dataframe(table, use_container_width=True, hide_index=True, height=440)

    section_title("League profile", "Team totals from the Teams SDHL sheet")
    profile_metrics = [m for m in ["Goals", "Shots", "Shots on goal", "Scoring chances", "xG (Expected goals)", "Net xG (xG - Opponent's xG)"] if m in teams.columns]
    if profile_metrics:
        profile = teams[["Team"] + profile_metrics].copy()
        st.dataframe(profile, use_container_width=True, hide_index=True)

# ============================================================
# TEAM ANALYTICS
# ============================================================
elif page == "Team Analytics":
    team_names = sorted(teams["Team"].dropna().astype(str).unique())
    selected_team = st.selectbox("Select team", team_names)
    row = teams[teams["Team"].astype(str) == selected_team].iloc[0]
    st.markdown(f"### {selected_team}")
    cols = st.columns(4)
    for col, metric in zip(cols, ["Goals", "xG (Expected goals)", "Shots", "CORSI%"]):
        with col:
            val = row.get(metric, None)
            metric_card(metric, fmt_num(val, 1))
    section_title("Team performance profile")
    team_metrics = [m for m in ["Goals", "xG (Expected goals)", "Net xG (xG - Opponent's xG)", "Shots", "Shots on goal", "Scoring chances", "Hits", "Blocked shots", "CORSI%"] if m in teams.columns]
    if team_metrics:
        comp = teams[["Team"] + team_metrics].copy()
        for m in team_metrics:
            comp[m] = numeric_series(comp[m])
        comp = comp.melt(id_vars="Team", var_name="Metric", value_name="Value")
        fig = px.bar(comp[comp["Team"] == selected_team], x="Metric", y="Value", color="Metric",
                     color_discrete_sequence=["#65aefc", "#38d6c5", "#a78bfa"])
        chart_theme(fig, 340)
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Value")
        st.plotly_chart(fig, use_container_width=True)
    section_title("League comparison")
    if team_metrics:
        compare = teams[["Team"] + team_metrics].copy()
        st.dataframe(compare.sort_values("Team"), use_container_width=True, hide_index=True)

    if players is not None and {"Team", "Player"}.issubset(players.columns):
        section_title("Player contributions", "Player-game rows; counting stats summed within the selected team")
        team_rows = players[players["Team"].astype(str) == selected_team].copy()
        if not team_rows.empty:
            count_cols = [c for c in ["Goals", "Assists", "Points", "Shots", "Hits", "Blocked shots"] if c in team_rows.columns]
            if count_cols:
                for c in count_cols:
                    team_rows[c] = numeric_series(team_rows[c])
                summary = team_rows.groupby("Player", as_index=False)[count_cols].sum()
                sort_col = "Points" if "Points" in count_cols else count_cols[0]
                summary = summary.sort_values(sort_col, ascending=False)
                st.dataframe(summary, use_container_width=True, hide_index=True)

# ============================================================
# PLAYER ANALYTICS
# ============================================================
elif page == "Player Analytics":
    if players is None or not {"Team", "Player"}.issubset(players.columns):
        st.warning("Player-game sheet or required columns are missing.")
        st.stop()
    p = players.copy()
    team_names = sorted(p["Team"].dropna().astype(str).unique())
    selected_team = st.selectbox("Team", team_names)
    p = p[p["Team"].astype(str) == selected_team]
    player_names = sorted(p["Player"].dropna().astype(str).unique())
    selected_player = st.selectbox("Player", player_names)
    pp = p[p["Player"].astype(str) == selected_player].copy()
    st.markdown(f"### {selected_player}")
    if "Date" in pp.columns:
        pp["Date"] = pd.to_datetime(pp["Date"], errors="coerce")
    games = pp["Date"].nunique() if "Date" in pp.columns else len(pp)
    toi_minutes = pp["Time on ice"].apply(normalize_toi).sum() if "Time on ice" in pp.columns else None
    goals = numeric_series(pp["Goals"]).sum() if "Goals" in pp.columns else None
    assists = numeric_series(pp["Assists"]).sum() if "Assists" in pp.columns else None
    points = numeric_series(pp["Points"]).sum() if "Points" in pp.columns else None
    shots = numeric_series(pp["Shots"]).sum() if "Shots" in pp.columns else None
    c = st.columns(5)
    for col, (label, value) in zip(c, [
        ("Games", games), ("Goals", goals), ("Assists", assists),
        ("Points", points), ("Shots", shots)
    ]):
        with col:
            metric_card(label, fmt_num(value, 0))
    if toi_minutes is not None:
        st.caption(f"Approximate total time on ice: {toi_minutes:.1f} minutes. TOI parsing depends on the InStat export format.")
    section_title("Game-by-game performance")
    show_cols = [x for x in ["Date", "Opponent", "Position", "Time on ice", "Goals", "Assists", "Points", "xG (Expected goals)", "Shots", "Shots on goal", "+/-"] if x in pp.columns]
    if "Date" in pp.columns:
        pp = pp.sort_values("Date")
    st.dataframe(pp[show_cols], use_container_width=True, hide_index=True)
    if "Date" in pp.columns and "Points" in pp.columns:
        trend = pp.groupby("Date", as_index=False)["Points"].sum()
        fig = px.line(trend, x="Date", y="Points", markers=True)
        fig.update_traces(line_color="#65aefc", marker_color="#38d6c5", line_width=3)
        chart_theme(fig, 300)
        fig.update_layout(xaxis_title="", yaxis_title="Points")
        section_title("Points trend")
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# GAME ANALYSIS
# ============================================================
elif page == "Game Analysis":
    if players is None or "Date" not in players.columns:
        st.warning("Player-game sheet or Date column is missing.")
        st.stop()
    g = players.copy()
    g["Date"] = pd.to_datetime(g["Date"], errors="coerce")
    dates = sorted(g["Date"].dropna().unique(), reverse=True)
    if not dates:
        st.warning("No valid game dates found.")
        st.stop()
    selected_date = st.selectbox("Game date", dates, format_func=format_date)
    gd = g[g["Date"] == selected_date].copy()
    teams_in_game = sorted(gd["Team"].dropna().astype(str).unique()) if "Team" in gd.columns else []
    if "Opponent" in gd.columns and teams_in_game:
        opponent = gd["Opponent"].dropna().astype(str).mode()
        matchup = f"{' vs '.join(teams_in_game)}"
        if not opponent.empty:
            matchup += f" • Opponent field: {opponent.iloc[0]}"
        st.markdown(f"### {matchup}")
    if teams_in_game:
        st.markdown("#### Player rows by team")
        for team_name in teams_in_game:
            st.markdown(f"**{team_name}**")
            td = gd[gd["Team"].astype(str) == team_name]
            cols = [x for x in ["Player", "Position", "Time on ice", "Goals", "Assists", "Points", "xG (Expected goals)", "Shots", "Shots on goal", "Hits", "Blocked shots"] if x in td.columns]
            st.dataframe(td[cols], use_container_width=True, hide_index=True)
    st.caption("This view shows the player-game records from the selected date. It does not calculate team totals from overlapping on-ice metrics.")

# ============================================================
# PLAYING STYLE
# ============================================================
elif page == "Playing Style":
    st.markdown("### Team playing-style indicators")
    st.caption("Descriptive profile from the available cumulative team data. These are raw totals/percentages, not possession-adjusted ratings.")
    style_metrics = [m for m in ["CORSI%", "Shots", "Shots on goal", "Scoring chances", "Faceoffs won, %", "Hits", "Blocked shots"] if m in teams.columns]
    if not style_metrics:
        st.warning("No playing-style metrics found in Teams SDHL.")
        st.stop()
    chosen = st.multiselect("Choose indicators", style_metrics, default=style_metrics[:4])
    if chosen:
        d = teams[["Team"] + chosen].copy()
        for m in chosen:
            d[m] = numeric_series(d[m])
        st.dataframe(d, use_container_width=True, hide_index=True)
        selected = st.selectbox("Highlight team", sorted(d["Team"].dropna().unique()))
        melt = d.melt(id_vars="Team", var_name="Indicator", value_name="Value")
        fig = px.bar(melt[melt["Team"] == selected], x="Indicator", y="Value",
                     color="Indicator", color_discrete_sequence=["#65aefc", "#38d6c5", "#a78bfa", "#f6bd60"])
        chart_theme(fig, 340)
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Value")
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# DATA CENTER
# ============================================================
elif page == "Data Center":
    st.markdown("### Workbook status")
    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Sheets detected", len(sheets))
    with c2:
        metric_card("Teams", len(teams))
    with c3:
        metric_card("Player-game rows", len(players) if players is not None else 0)
    st.markdown("#### Available worksheets")
    st.write(sheets)
    selected_sheet = st.selectbox("Inspect worksheet", sheets)
    df = get_sheet(selected_sheet)
    if df is not None:
        st.caption(f"{len(df):,} rows • {len(df.columns):,} columns")
        st.dataframe(df, use_container_width=True, hide_index=True, height=600)
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "Download selected sheet as CSV",
            data=csv,
            file_name=f"{re.sub(r'[^A-Za-z0-9_-]+', '_', selected_sheet)}.csv",
            mime="text/csv"
        )

st.markdown("---")
st.caption("SDHL Analytics • InStat data • Prototype build. Validate source definitions before using derived comparisons.")
