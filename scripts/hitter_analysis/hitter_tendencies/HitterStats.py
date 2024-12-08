import sqlite3
import pandas as pd
import csv

from Hitter import Hitter
from HitterTendencies import HitterTendencies
from CountAnalysis import CountAnalysis

# Connect to the database
conn = sqlite3.connect('/Users/marcopena/Documents/GitHub/uarizona-baseball-analytics/baseball_analytics.db')

# Query relevant data for "Caulfield, Garen"
query = """
    SELECT 
        PA, PitchofPA, Batter, Strikes, Balls, KorBB, TaggedPitchType, PlayResult, 
        Angle, Direction, Distance, PlateLocHeight, PlateLocSide, PitchCall, TaggedHitType,
        AVG, OBP, SLG, swing, whiff, StadiumID, "2B", "3B", HR, GameID, PitcherThrows
    FROM pitches
    WHERE Batter = 'Caulfield, Garen';
"""

df = pd.read_sql_query(query, conn)

# Close the database connection
conn.close()


# Write Full Stats CSV
df.to_csv('test_stats.csv', index=False)



