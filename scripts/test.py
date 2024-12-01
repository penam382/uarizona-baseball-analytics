import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('/Users/marcopena/Documents/GitHub/uarizona-baseball-analytics/baseball_analytics.db')

# Query relevant data for "Caulfield, Garen"
query = """
    SELECT 
        PA, PitchofPA, Batter, Strikes, Balls, KorBB, TaggedPitchType, PlayResult, 
        Angle, Direction, Distance, PlateLocHeight, PlateLocSide, PitchCall, TaggedHitType,
        AVG, OBP, SLG, swing, whiff, StadiumID, "2B", "3B", HR, chase, OutsOnPlay, GameID,
        PitcherThrows, ExitSpeed, RelSpeed
    FROM pitches
    WHERE Batter = 'Caulfield, Garen';
"""
df = pd.read_sql_query(query, conn)

# Close the database connection
conn.close()

# Initialize variables for calculations
hits = 0
total_bases = 0
at_bats = 0
plate_appearances = 0
walks = 0
on_base = 0
slg = 0


# Process each row to calculate stats
for _, row in df.iterrows():
    if row['OBP'] >= 0:
        plate_appearances += 1
    
    if row['AVG'] == 1:
        hits += 1
    if row['AVG'] >= 0:
        at_bats += 1
    if row['OBP'] == 1:
        on_base += 1
    
    if row['SLG'] >= 1:
        slg += row['SLG']


# Print the results
print(f"Player: Caulfield, Garen")
print(f"Plate Appearances (PA): {plate_appearances}")
print(f"At Bats (AB): {at_bats}")
print("hits", hits)
print("AVG", hits / at_bats)
print("OBP", (on_base / plate_appearances))
print("OBP_TEST", plate_appearances)
print("SLG", slg / at_bats)

