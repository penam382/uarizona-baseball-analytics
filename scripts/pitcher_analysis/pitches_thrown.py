import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('/Users/marcopena/Documents/GitHub/uarizona-baseball-analytics/baseball_analytics.db')

# Query only relevant data for "Caulfield, Garen"
query = "SELECT * FROM pitches WHERE Batter = 'Caulfield, Garen';"
df = pd.read_sql_query(query, conn)

# Close the database connection
conn.close()

# Process the data to create Hitter instances
plate_appearances = {}

current_pa_id = 0  # Initialize a counter for plate appearance IDs
current_hitter = None

strikeouts = 0
walks = 0

for i, row in df.iterrows():
    pitch_of_pa = row['PitchofPA']
    batter = row['Batter']