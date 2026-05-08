import pandas as pd

# ==================================================
# LOAD DATA
# ==================================================

df = pd.read_excel(
    "Skaters - SDHL 2025-2026 uusi.xlsx"
)

# ==================================================
# CLEAN COLUMNS
# ==================================================

df.columns = df.columns.str.strip()

# ==================================================
# REPLACE "-" VALUES
# ==================================================

df = df.replace("-", 0)

# ==================================================
# CLEAN POSITION
# ==================================================

df["Position"] = (
    df["Position"]
    .astype(str)
    .str.strip()
)

# ==================================================
# FIX % COLUMNS
# ==================================================

percent_columns = [

    "Accurate passes, %",
    "Puck battles won, %",
    "CORSI for, %",
    "Fenwick for, %"

]

for col in percent_columns:

    if col in df.columns:

        df[col] = (

            df[col]
            .astype(str)
            .str.replace("%", "", regex=False)
            .str.replace(",", ".", regex=False)

        )

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        ).fillna(0)

# ==================================================
# CONVERT NUMERIC COLUMNS
# ==================================================

numeric_columns = [

    "Games played",
    "Time on ice",

    "Goals",
    "Assists",
    "Points",
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

    "OZ possession",

    "Takeaways in DZ",

    "Opponent's xG when on ice",

    "Net xG (xG player on - opp. team's xG)",

    "Team xG when on ice"

]

for col in numeric_columns:

    if col in df.columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        ).fillna(0)

# ==================================================
# CREATE PER60 STATS
# ==================================================

per60_stats = [

    "Goals",
    "Assists",
    "Shots",

    "xG (Expected goals)",

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

    "OZ possession"

]

for stat in per60_stats:

    if stat in df.columns:

        df[f"{stat}/60"] = (

            df[stat] /
            df["Time on ice"]

        ) * 60

# ==================================================
# CREATE POSITION-BASED PERCENTILES
# ==================================================

percentile_metrics = [

    # SHOOTING

    "Goals/60",
    "Shots/60",
    "xG (Expected goals)/60",

    "Scoring chances - total/60",
    "Inner slot shots - total/60",

    # PLAYMAKING

    "Pre-shots passes/60",
    "Passes to the slot/60",
    "First assist/60",

    "Accurate passes, %",

    # TRANSITION

    "Entries/60",
    "Entries via stickhandling/60",
    "Entries via pass/60",

    "Breakouts/60",

    # PUCK MOVEMENT

    "Breakouts via pass/60",
    "Breakouts via stickhandling/60",

    "Puck touches/60",
    "Puck control time/60",

    "OZ possession/60",

    # DEFENSE

    "Takeaways/60",
    "Takeaways in DZ",

    "Puck battles won, %",

    "Opponent's xG when on ice",

    # IMPACT

    "Net xG (xG player on - opp. team's xG)",

    "Team xG when on ice",

    "CORSI for, %",
    "Fenwick for, %"

]

for metric in percentile_metrics:

    if metric in df.columns:

        df[f"{metric} Percentile"] = (

            df.groupby("Position")[metric]
            .rank(pct=True) * 100

        )

# ==================================================
# REVERSE NEGATIVE METRIC
# ==================================================

if "Opponent's xG when on ice" in df.columns:

    df["Opponent's xG when on ice Percentile"] = (

        100 -

        df.groupby("Position")[
            "Opponent's xG when on ice"
        ].rank(pct=True) * 100

    )

# ==================================================
# AVERAGE FUNCTION
# ==================================================

def average_percentiles(metrics):

    cols = [

        f"{m} Percentile"
        for m in metrics

        if f"{m} Percentile" in df.columns

    ]

    if len(cols) == 0:

        return 0

    return df[cols].fillna(0).mean(axis=1)

# ==================================================
# SHOOTING SCORE
# ==================================================

shooting_metrics = [

    "Goals/60",
    "Shots/60",

    "xG (Expected goals)/60",

    "Scoring chances - total/60",
    "Inner slot shots - total/60"

]

df["Shooting Score"] = average_percentiles(
    shooting_metrics
)

# ==================================================
# PLAYMAKING SCORE
# ==================================================

playmaking_metrics = [

    "Pre-shots passes/60",
    "Passes to the slot/60",

    "First assist/60",

    "Accurate passes, %"

]

df["Playmaking Score"] = average_percentiles(
    playmaking_metrics
)

# ==================================================
# TRANSITION SCORE
# ==================================================

transition_metrics = [

    "Entries/60",
    "Entries via stickhandling/60",

    "Entries via pass/60",

    "Breakouts/60"

]

df["Transition Score"] = average_percentiles(
    transition_metrics
)

# ==================================================
# PUCK MOVEMENT SCORE
# ==================================================

puck_movement_metrics = [

    "Breakouts via pass/60",
    "Breakouts via stickhandling/60",

    "Puck touches/60",
    "Puck control time/60",

    "OZ possession/60"

]

df["Puck Movement Score"] = average_percentiles(
    puck_movement_metrics
)

# ==================================================
# DEFENSE SCORE
# ==================================================

defense_metrics = [

    "Takeaways/60",
    "Takeaways in DZ",

    "Puck battles won, %",

    "Opponent's xG when on ice"

]

df["Defense Score"] = average_percentiles(
    defense_metrics
)

# ==================================================
# IMPACT SCORE
# ==================================================

impact_metrics = [

    "Net xG (xG player on - opp. team's xG)",

    "Team xG when on ice",

    "CORSI for, %",
    "Fenwick for, %"

]

df["Impact Score"] = average_percentiles(
    impact_metrics
)

# ==================================================
# POSITION-SPECIFIC OVERALL SCORE
# ==================================================

df["Overall Score"] = 0

# ==================================================
# FORWARDS
# ==================================================

forward_mask = df["Position"] == "F"

df.loc[forward_mask, "Overall Score"] = (

    df.loc[forward_mask, "Shooting Score"] * 0.25 +

    df.loc[forward_mask, "Playmaking Score"] * 0.25 +

    df.loc[forward_mask, "Transition Score"] * 0.25 +

    df.loc[forward_mask, "Puck Movement Score"] * 0.10 +

    df.loc[forward_mask, "Defense Score"] * 0.05 +

    df.loc[forward_mask, "Impact Score"] * 0.10

)

# ==================================================
# DEFENSEMEN
# ==================================================

defense_mask = df["Position"] == "D"

df.loc[defense_mask, "Overall Score"] = (

    df.loc[defense_mask, "Shooting Score"] * 0.10 +

    df.loc[defense_mask, "Playmaking Score"] * 0.15 +

    df.loc[defense_mask, "Transition Score"] * 0.25 +

    df.loc[defense_mask, "Puck Movement Score"] * 0.25 +

    df.loc[defense_mask, "Defense Score"] * 0.15 +

    df.loc[defense_mask, "Impact Score"] * 0.10

)

# ==================================================
# OVERALL PERCENTILE
# ==================================================

df["Overall Score Percentile"] = (

    df.groupby("Position")[
        "Overall Score"
    ].rank(pct=True) * 100

)

# ==================================================
# ROUND VALUES
# ==================================================

numeric_cols = df.select_dtypes(
    include="number"
).columns

df[numeric_cols] = df[numeric_cols].round(2)

# ==================================================
# DEFRAGMENT DATAFRAME
# ==================================================

df = df.copy()

# ==================================================
# EXPORT FINAL DATASET
# ==================================================

df.to_excel(
    "SDHL_Processed_2025_2026.xlsx",
    index=False
)

# ==================================================
# DONE
# ==================================================

print("DONE")
print(df.head())
