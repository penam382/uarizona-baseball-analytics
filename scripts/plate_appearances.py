import sqlite3
import pandas as pd

from Hitter import Hitter

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

for i, row in df.iterrows():
    pitch_of_pa = row['PitchofPA']
    batter = row['Batter']
    
    # Retrieve strike and ball counts for the current pitch
    strike = row['Strikes']
    ball = row['Balls']

    # process pitch
    # location = (PlateLocHeight, PlateLocSide) 
    plate_loc_height = row['PlateLocHeight']
    plate_loc_side = row['PlateLocSide']
    location = (plate_loc_height, plate_loc_side)

    pitch_type = row['']


    # Detect the start of a new plate appearance
    if pitch_of_pa == 1:
        # Save the current hitter instance if it exists
        if current_hitter is not None:
            plate_appearances[current_pa_id] = current_hitter

        # Increment the plate appearance ID and create a new Hitter instance
        current_pa_id += 1
        current_hitter = Hitter(current_pa_id, batter)

    # Ensure current_hitter is initialized
    if current_hitter is None:
        print(f"Error: No Hitter instance found for Plate Appearance {current_pa_id}")
        continue

# Save the final plate appearance
if current_hitter is not None:
    plate_appearances[current_pa_id] = current_hitter

Hitter.type_of_count(ball, strike)
Hitter.count(ball, strike)
Hitter.process_pitch(location, pitch_type, pitch_of_pa)
Hitter.log_tendency(count_type, pitch_type, outcome, location)


# Output the plate appearances
for pa_id, hitter in plate_appearances.items():
    print(f"Plate Appearance {pa_id}: {hitter}")
