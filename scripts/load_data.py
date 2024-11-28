import sqlite3
import pandas as pd

# Path to the downloaded CSV file
csv_path = '/Users/marcopena/Documents/GitHub/uarizona-baseball-analytics/data/raw/fall_data.csv'

try:
    # Load the CSV
    print("Loading CSV from local path...")
    df = pd.read_csv(csv_path)
    print("CSV loaded successfully.")

    # Connect to SQLite database
    print("Connecting to SQLite database...")
    conn = sqlite3.connect('baseball_analytics.db')

    # Save the data to an SQL table
    print("Saving data to SQLite table...")
    df.to_sql('pitches', conn, if_exists='replace', index=False)
    print("Data saved successfully.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    if conn:
        conn.close()
    print("Database connection closed.")
