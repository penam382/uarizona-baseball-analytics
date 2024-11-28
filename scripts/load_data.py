# Script to load CSV into SQL database

import sqlite3
import pandas as pd

# Read the CSV
df = pd.read_csv('raw/fall_data.csv')

# Connect to SQLite
conn = sqlite3.connect('baseball_analytics.db')

# Save to SQL table
df.to_sql('pitches', conn, if_exists='replace', index=False)

conn.close()


