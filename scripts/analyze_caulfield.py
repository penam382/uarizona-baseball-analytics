

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

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

# Path to SQL file
sql_file = '/Users/marcopena/Documents/GitHub/uarizona-baseball-analytics/sql/queries.sql'

# Load the specific query
query = load_query(sql_file, 'caulfield_pitch_count')

# Connect to the database
conn = sqlite3.connect('/Users/marcopena/Documents/GitHub/uarizona-baseball-analytics/baseball_analytics.db')

# Execute the query
df = pd.read_sql_query(query, conn)

# Calculate percentages
df['Percentage'] = (df['Total'] / df['Total'].sum()) * 100

# Replace None or NaN in TaggedPitchType with 'Unknown'
df['TaggedPitchType'] = df['TaggedPitchType'].fillna('Unknown')

# Close the connection
conn.close()

# Print the DataFrame
print(df)

# Create a bar chart
# plt.figure(figsize=(10, 6))
# plt.bar(df['TaggedPitchType'], df['Percentage'], color='skyblue')
# plt.title('Pitch Type Distribution to Garen Caulfield')
# plt.xlabel('Pitch Type')
# plt.ylabel('Percentage (%)')
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.savefig('/Users/marcopena/Documents/GitHub/uarizona-baseball-analytics/visuals/caulfield_pitches.png')  # Save the chart
# plt.show()

