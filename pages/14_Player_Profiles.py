# SDHL 2025-2026 Win Shares Streamlit App

## Folder Structure

```text
project/
│
├── Home.py
├── requirements.txt
├── Skaters - SDHL 2025-2026 WIN SHARE.xlsx
│
├── pages/
│   ├── 1_Player_Profiles.py
│   ├── 2_Win_Shares_Rankings.py
│   ├── 3_Team_Analysis.py
│   └── 4_League_Overview.py
```

---

# requirements.txt

```txt
streamlit
pandas
numpy
plotly
scipy
openpyxl
```

---

# IMPORTANT

Excel file name:

```text
Skaters - SDHL 2025-2026 WIN SHARE.xlsx
```

Sheet names should be:

```text
Players
Teams
```

---

# Home.py

```python
import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import zscore

st.set_page_config(
    page_title="SDHL Win Shares",
    page_icon="🏒",
    layout="wide"
)

FILE = "Skaters - SDHL 2025-2026 WIN SHARE.xlsx"

@st.cache_data

def load_data():
    players = pd.read_excel(FILE, sheet_name="Players")
    teams = pd.read_excel(FILE, sheet_name="Teams")

    # Clean column names
    players.columns = (
        players.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("/", "_per_")
        .str.replace("%", "perc")
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
    )

    teams.columns = (
        teams.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("/", "_per_")
    )

    # Merge
    df = players.merge(teams, on="Team")

    # Rename easier columns
    df = df.rename(columns={
        "Goals_per_60": "Goals60",
        "Assists_per_60": "Assists60",
        "xG_per_60": "xG60",
        "Takeaways__per_60": "Takeaways60",
        "Puck_losses_per_60": "PuckLosses60",
        "Net_penalties_per_60": "NetPenalties60",
        "Passes_to_the_slot": "SlotPasses",
        "Puck_battles_won": "PuckBattlesWon",
        "Net_xG": "NetxG"
    })

    # Fill missing values
    numeric_cols = df.select_dtypes(include=np.number).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)

    # Z-scores
    metrics = [
        "Goals60",
        "Assists60",
        "xG60",
        "Scoring_chances",
        "SlotPasses",
        "NetxG",
        "Takeaways60",
        "PuckLosses60",
        "NetPenalties60",
        "PuckBattlesWon"
    ]

    for metric in metrics:
        if metric in df.columns:
            df[f"{metric}_z"] = zscore(df[metric])

    # Offensive Win Shares
    df["OWS"] = (
        0.30 * df["Goals60_z"] +
        0.35 * df["Assists60_z"] +
        0.20 * df["xG60_z"] +
        0.15 * df["SlotPasses_z"]
    )

    # Defensive Win Shares
    df["DWS"] = (
        0.40 * df["NetxG_z"] +
        0.20 * df["Takeaways60_z"] -
        0.20 * df["PuckLosses60_z"] +
        0.10 * df["NetPenalties60_z"] +
        0.10 * df["PuckBattlesWon_z"]
    )

    # Overall Win Shares
    df["WS"] = df["OWS"] + df["DWS"]

    # Percentiles
    df["OWS_percentile"] = df["OWS"].rank(pct=True) * 100
    df["DWS_percentile"] = df["DWS"].rank(pct=True) * 100
    df["WS_percentile"] = df["WS"].rank(pct=True) * 100

    return df


df = load_data()

st.title("🏒 SDHL 2025-2026 Win Shares Dashboard")

st.markdown("""
This dashboard calculates:
- Offensive Win Shares (OWS)
- Defensive Win Shares (DWS)
- Overall Win Shares (WS)
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Players", len(df))

with col2:
    st.metric("Teams", df['Team'].nunique())

with col3:
    st.metric("Average WS", round(df['WS'].mean(), 2))

st.subheader("Top 10 Overall Win Shares")

leaderboard = df[[
    "Player",
    "Team",
    "Position",
    "OWS",
    "DWS",
    "WS"
]].sort_values("WS", ascending=False).head(10)

st.dataframe(leaderboard, use_container_width=True)
```

---

# pages/1_Player_Profiles.py

```python
import streamlit as st
import pandas as pd
import plotly.express as px
from scipy.stats import zscore
import numpy as np

FILE = "Skaters - SDHL 2025-2026 WIN SHARE.xlsx"

@st.cache_data

def load_data():
    players = pd.read_excel(FILE, sheet_name="Players")
    teams = pd.read_excel(FILE, sheet_name="Teams")

    players.columns = (
        players.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("/", "_per_")
        .str.replace("%", "perc")
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
    )

    teams.columns = (
        teams.columns
        .str.strip()
        .str.replace(" ", "_")
    )

    df = players.merge(teams, on="Team")

    df = df.rename(columns={
        "Goals_per_60": "Goals60",
        "Assists_per_60": "Assists60",
        "xG_per_60": "xG60",
        "Takeaways__per_60": "Takeaways60",
        "Puck_losses_per_60": "PuckLosses60",
        "Net_penalties_per_60": "NetPenalties60",
        "Passes_to_the_slot": "SlotPasses",
        "Puck_battles_won": "PuckBattlesWon",
        "Net_xG": "NetxG"
    })

    metrics = [
        "Goals60",
        "Assists60",
        "xG60",
        "SlotPasses",
        "NetxG",
        "Takeaways60",
        "PuckLosses60",
        "NetPenalties60",
        "PuckBattlesWon"
    ]

    for metric in metrics:
        df[f"{metric}_z"] = zscore(df[metric])

    df["OWS"] = (
        0.30 * df["Goals60_z"] +
        0.35 * df["Assists60_z"] +
        0.20 * df["xG60_z"] +
        0.15 * df["SlotPasses_z"]
    )

    df["DWS"] = (
        0.40 * df["NetxG_z"] +
        0.20 * df["Takeaways60_z"] -
        0.20 * df["PuckLosses60_z"] +
        0.10 * df["NetPenalties60_z"] +
        0.10 * df["PuckBattlesWon_z"]
    )

    df["WS"] = df["OWS"] + df["DWS"]

    return df


df = load_data()

st.title("Player Profiles")

player = st.selectbox(
    "Select player",
    sorted(df["Player"].unique())
)

player_df = df[df["Player"] == player].iloc[0]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("OWS", round(player_df["OWS"], 2))

with col2:
    st.metric("DWS", round(player_df["DWS"], 2))

with col3:
    st.metric("WS", round(player_df["WS"], 2))

radar_df = pd.DataFrame({
    "Metric": [
        "Goals60",
        "Assists60",
        "xG60",
        "NetxG",
        "Takeaways60",
        "PuckBattlesWon"
    ],
    "Value": [
        player_df["Goals60"],
        player_df["Assists60"],
        player_df["xG60"],
        player_df["NetxG"],
        player_df["Takeaways60"],
        player_df["PuckBattlesWon"]
    ]
})

fig = px.line_polar(
    radar_df,
    r="Value",
    theta="Metric",
    line_close=True
)

st.plotly_chart(fig, use_container_width=True)
```

---

# pages/2_Win_Shares_Rankings.py

```python
import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import zscore

FILE = "Skaters - SDHL 2025-2026 WIN SHARE.xlsx"

@st.cache_data

def load_data():
    players = pd.read_excel(FILE, sheet_name="Players")
    teams = pd.read_excel(FILE, sheet_name="Teams")

    players.columns = (
        players.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("/", "_per_")
        .str.replace("%", "perc")
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
    )

    teams.columns = (
        teams.columns
        .str.strip()
        .str.replace(" ", "_")
    )

    df = players.merge(teams, on="Team")

    df = df.rename(columns={
        "Goals_per_60": "Goals60",
        "Assists_per_60": "Assists60",
        "xG_per_60": "xG60",
        "Takeaways__per_60": "Takeaways60",
        "Puck_losses_per_60": "PuckLosses60",
        "Net_penalties_per_60": "NetPenalties60",
        "Passes_to_the_slot": "SlotPasses",
        "Puck_battles_won": "PuckBattlesWon",
        "Net_xG": "NetxG"
    })

    metrics = [
        "Goals60",
        "Assists60",
        "xG60",
        "SlotPasses",
        "NetxG",
        "Takeaways60",
        "PuckLosses60",
        "NetPenalties60",
        "PuckBattlesWon"
    ]

    for metric in metrics:
        df[f"{metric}_z"] = zscore(df[metric])

    df["OWS"] = (
        0.30 * df["Goals60_z"] +
        0.35 * df["Assists60_z"] +
        0.20 * df["xG60_z"] +
        0.15 * df["SlotPasses_z"]
    )

    df["DWS"] = (
        0.40 * df["NetxG_z"] +
        0.20 * df["Takeaways60_z"] -
        0.20 * df["PuckLosses60_z"] +
        0.10 * df["NetPenalties60_z"] +
        0.10 * df["PuckBattlesWon_z"]
    )

    df["WS"] = df["OWS"] + df["DWS"]

    return df


df = load_data()

st.title("Win Shares Rankings")

metric = st.selectbox(
    "Select metric",
    ["OWS", "DWS", "WS"]
)

position = st.multiselect(
    "Position",
    df["Position"].unique(),
    default=df["Position"].unique()
)

filtered_df = df[df["Position"].isin(position)]

ranking = filtered_df[[
    "Player",
    "Team",
    "Position",
    "Goals60",
    "Assists60",
    "xG60",
    "OWS",
    "DWS",
    "WS"
]].sort_values(metric, ascending=False)

st.dataframe(ranking, use_container_width=True)
```

---

# pages/3_Team_Analysis.py

```python
import streamlit as st
import pandas as pd
import plotly.express as px

FILE = "Skaters - SDHL 2025-2026 WIN SHARE.xlsx"

players = pd.read_excel(FILE, sheet_name="Players")
teams = pd.read_excel(FILE, sheet_name="Teams")

st.title("Team Analysis")

team = st.selectbox(
    "Select Team",
    teams["Team"].unique()
)

team_players = players[players["Team"] == team]

st.subheader("Roster")
st.dataframe(team_players)

fig = px.bar(
    teams,
    x="Team",
    y="G",
    title="Goals For by Team"
)

st.plotly_chart(fig, use_container_width=True)
```

---

# pages/4_League_Overview.py

```python
import streamlit as st
import pandas as pd
import plotly.express as px

FILE = "Skaters - SDHL 2025-2026 WIN SHARE.xlsx"

players = pd.read_excel(FILE, sheet_name="Players")

players.columns = (
    players.columns
    .str.strip()
    .str.replace(" ", "_")
    .str.replace("/", "_per_")
)

st.title("League Overview")

fig = px.histogram(
    players,
    x="Points",
    nbins=20,
    title="Points Distribution"
)

st.plotly_chart(fig, use_container_width=True)

fig2 = px.scatter(
    players,
    x="Goals_per_60",
    y="xG_per_60",
    hover_name="Player",
    color="Team"
)

st.plotly_chart(fig2, use_container_width=True)
```

---

# RUN THE APP

Open terminal:

```bash
streamlit run Home.py
```

---

# NEXT IMPROVEMENTS

Later you can add:

* Team-adjusted Win Shares
* League-adjusted Win Shares
* Percentiles
* Player comparison
* Radar charts
* Prospect model
* Transition impact
* xWAR model
* GAR model

