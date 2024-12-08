import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('/Users/marcopena/Documents/GitHub/uarizona-baseball-analytics/baseball_analytics.db')

# Execute the query
query = """
    SELECT 
        PA, PitchofPA, Pitcher, Strikes, Balls, KorBB, TaggedPitchType, PlayResult, RunsScored,
        VertRelAngle, HorzRelAngle, SpinRate, SpinAxis, Tilt, RelHeight, RelSide, Extension, VertBreak, InducedVertBreak, 
        HorzBreak, PlateLocHeight, PlateLocSide, ExitSpeed, RelSpeed, PreviousPitch, called_strike, ooz,
        Angle, Direction, Distance, PitchCall, TaggedHitType, k, bb, bbspin, pitches, zone, izswing, izmiss,
        AVG, OBP, SLG, swing, whiff, StadiumID, "2B", "3B", HR, chase, OutsOnPlay, GameID,
        PitcherThrows
    FROM pitches
    WHERE Pitcher = 'Berg, Jack';
"""
df = pd.read_sql_query(query, conn)

# Close the database connection
conn.close()

# Data Cleaning and Preparation
# Classify hits by type
df['is_single'] = df['PlayResult'] == 'Single'
df['is_double'] = df['PlayResult'] == 'Double'
df['is_triple'] = df['PlayResult'] == 'Triple'
df['is_home_run'] = df['PlayResult'] == 'HomeRun'

# Metrics Calculation
metrics = df.groupby('TaggedPitchType').agg(
    total_pitches=('TaggedPitchType', 'count'),
    total_hits=('PlayResult', lambda x: (x.isin(['Single', 'Double', 'Triple', 'HomeRun'])).sum()),
    singles=('is_single', 'sum'),
    doubles=('is_double', 'sum'),
    triples=('is_triple', 'sum'),
    home_runs=('is_home_run', 'sum'),
    avg_exit_speed=('ExitSpeed', 'mean'),
    avg_release_speed=('RelSpeed', 'mean'),
)

# Sort by total hits to identify underperforming pitches
underperforming_pitches = metrics.sort_values(by='total_hits', ascending=False)

# Output Results
print("Pitch Effectiveness Metrics:")
print(metrics)

print("\nUnderperforming Pitches by Hits Given Up:")
print(underperforming_pitches)

# Count unique GameIDs to determine total games pitched
total_games_pitched = df['GameID'].nunique()
print(f"\nTotal Games Pitched: {total_games_pitched}")

# Batting Average Calculation
# Filter valid at-bats where AVG >= 0
valid_at_bats = df[df['AVG'] >= 0]

# Calculate total at-bats and hits
total_at_bats = len(valid_at_bats)  # Count of rows where AVG >= 0
total_hits = len(valid_at_bats[valid_at_bats['AVG'] == 1])  # Count where AVG == 1

# Calculate batting average
batting_average = total_hits / total_at_bats if total_at_bats > 0 else 0

# Output Batting Average
print(f"\nTotal At-Bats: {total_at_bats}")
print(f"Total Hits: {total_hits}")
print(f"Batting Average: {batting_average:.3f}")

# Confirm performance based on batting average
if batting_average < 0.200:
    print("This is an excellent performance! Very few hits given up.")
elif batting_average < 0.300:
    print("This is a solid performance.")
else:
    print("Performance is average or below average. Consider adjustments.")
