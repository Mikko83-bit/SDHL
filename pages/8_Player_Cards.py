import pandas as pd

# =========================
# LOAD DATA
# =========================

df = pd.read_excel(
    "Skaters - Lulea HF, 07-May-2026.xlsx"
)

# =========================
# CLEAN COLUMN NAMES
# =========================

df.columns = df.columns.str.strip()

# =========================
# FILL MISSING VALUES
# =========================

df = df.fillna(0)

# =========================
# TIME ON ICE
# =========================

toi = "Time on ice"

# =========================
# CONVERT NUMERIC COLUMNS
# =========================

numeric_columns = [

    "Goals",
    "Assists",
    "Shots",
    "xG (Expected goals)",
    "Puck battles",
    "Puck battles won",
    "Pre-shots passes",
    "Passes to the slot",
    "Entries",
    "Breakouts",
    "Takeaways",
    "Puck losses",
    "Shots on goal",
    "Inner slot shots - total",
    "Scoring chances - total",
    "First assist",
    "Accurate passes",
    "Entries via stickhandling",
    "Entries via pass",
    "Breakouts via stickhandling",
    "Breakouts via pass",
    "Puck touches",
    "Puck control time",
    "Takeaways in DZ",
    "Opponent's xG when on ice",
    "Net xG (xG player on - opp. team's xG)",
    "Team xG when on ice",
    "CORSI for, %",
    "Fenwick for, %",
    "Accurate passes, %",
    "Puck battles won, %"
]

for col in numeric_columns:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    ).fillna(0)

# =========================
# CREATE PER60 STATS
# =========================

per60_stats = [

    "Goals",
    "Assists",
    "Shots",
    "xG (Expected goals)",
    "Puck battles",
    "Puck battles won",
    "Pre-shots passes",
    "Passes to the slot",
    "Entries",
    "Breakouts",
    "Takeaways",
    "Puck losses",
    "Shots on goal",
    "Inner slot shots - total",
    "Scoring chances - total",
    "First assist",
    "Accurate passes",
    "Entries via stickhandling",
    "Entries via pass",
    "Breakouts via stickhandling",
    "Breakouts via pass",
    "Puck touches",
    "Puck control time"

]

for stat in per60_stats:

    df[f"{stat}/60"] = (

        df[stat] / df[toi]

    ) * 60

# =========================
# METRIC GROUPS
# =========================

shooting_metrics = [

    "Shots/60",
    "Scoring chances - total/60",
    "Inner slot shots - total/60",
    "Goals/60"

]

playmaking_metrics = [

    "Pre-shots passes/60",
    "Passes to the slot/60",
    "First assist/60",
    "Accurate passes, %"

]

transition_metrics = [

    "Entries/60",
    "Entries via stickhandling/60",
    "Entries via pass/60",
    "Breakouts/60"

]

puck_movement_metrics = [

    "Breakouts via pass/60",
    "Breakouts via stickhandling/60",
    "Puck touches/60",
    "Puck control time/60"

]

defense_metrics = [

    "Takeaways/60",
    "Takeaways in DZ",
    "Puck battles won, %",
    "Opponent's xG when on ice"

]

impact_metrics = [

    "Net xG (xG player on - opp. team's xG)",
    "Team xG when on ice",
    "CORSI for, %",
    "Fenwick for, %"

]

# =========================
# CREATE PERCENTILES
# =========================

all_metrics = (

    shooting_metrics +

    playmaking_metrics +

    transition_metrics +

    puck_movement_metrics +

    defense_metrics +

    impact_metrics

)

for metric in all_metrics:

    df[f"{metric} Percentile"] = (

        df[metric].rank(
            pct=True
        ) * 100

    )

# =========================
# REVERSE BAD METRIC
# =========================

df["Opponent's xG when on ice Percentile"] = (

    100 -

    df["Opponent's xG when on ice"].rank(
        pct=True
    ) * 100

)

# =========================
# CREATE SKILL SCORES
# =========================

def average_percentiles(metrics):

    percentile_cols = [

        f"{m} Percentile"
        for m in metrics

    ]

    return df[percentile_cols].mean(axis=1)

# =========================
# SKILL SCORES
# =========================

df["Shooting Score"] = average_percentiles(
    shooting_metrics
)

df["Playmaking Score"] = average_percentiles(
    playmaking_metrics
)

df["Transition Score"] = average_percentiles(
    transition_metrics
)

df["Puck Movement Score"] = average_percentiles(
    puck_movement_metrics
)

df["Defense Score"] = average_percentiles(
    defense_metrics
)

df["Impact Score"] = average_percentiles(
    impact_metrics
)

# =========================
# OVERALL SCORE
# =========================

df["Overall Score"] = (

    df["Shooting Score"] * 0.20 +

    df["Playmaking Score"] * 0.20 +

    df["Transition Score"] * 0.20 +

    df["Puck Movement Score"] * 0.15 +

    df["Defense Score"] * 0.10 +

    df["Impact Score"] * 0.15

)

# =========================
# ROUND VALUES
# =========================

numeric_cols = df.select_dtypes(
    include="number"
).columns

df[numeric_cols] = df[numeric_cols].round(2)

# =========================
# EXPORT
# =========================

df.to_excel(
    "SDHL_Microstats_Final.xlsx",
    index=False
)

print("DONE")
print(df.head())

