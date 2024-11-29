import sqlite3
import pandas as pd

# Function to load specific queries from queries.sql
def load_query(file_path, query_name):
    with open(file_path, 'r') as file:
        queries = file.read()
    start_marker = f"-- {query_name}"
    start_index = queries.find(start_marker)
    if start_index == -1:
        raise ValueError(f"Query '{query_name}' not found in {file_path}.")
    end_index = queries.find("-- ", start_index + len(start_marker))
    query = queries[start_index + len(start_marker):end_index].strip()
    return query

# Paths
sql_file = '/Users/marcopena/Documents/GitHub/uarizona-baseball-analytics/sql/queries.sql'
db_path = '/Users/marcopena/Documents/GitHub/uarizona-baseball-analytics/baseball_analytics.db'

# Load the query for pitches per at-bat
query = load_query(sql_file, 'caulfield_pitches_per_at_bat')

# Connect to the database
conn = sqlite3.connect(db_path)

# Execute the query
df = pd.read_sql_query(query, conn)

# Close the database connection
conn.close()

pitch_of_pa_list = df['PitchofPA'].tolist() 

plate_appearance = {}
counter = 0

# loops through the pitches per PA. keep count of amount of PA
for index in range(1, len(pitch_of_pa_list)): 
    if pitch_of_pa_list[index] == 1:
        counter += 1
        plate_appearance[counter] = pitch_of_pa_list[index - 1]

# Print the DataFrame to the command line
print("Number of PA for Garen Caulfield:")
print(plate_appearance)

