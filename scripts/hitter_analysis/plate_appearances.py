import sqlite3
import pandas as pd

from Hitter import Hitter
from Tendencies import Tendencies
from count_analysis.hitters_count.Hitters_Count import Hitters_Count

# Connect to the database
conn = sqlite3.connect('/Users/marcopena/Documents/GitHub/uarizona-baseball-analytics/baseball_analytics.db')

# Query only relevant data for "Caulfield, Garen"
query = "SELECT * FROM pitches WHERE Batter = 'Caulfield, Garen';"
df = pd.read_sql_query(query, conn)

# Close the database connection
conn.close()

# Process the data to create Hitter instances
plate_appearances = {}

# Create a Tendencies instance to track tendencies
tendencies = Tendencies()

hitters_count = Hitters_Count(tendencies)

current_pa_id = 0  # Initialize a counter for plate appearance IDs
current_hitter = None

strikeouts = 0
walks = 0

print("yo")

for i, row in df.iterrows():
    pitch_of_pa = row['PitchofPA']
    batter = row['Batter']
    
    # Retrieve strike and ball counts for the current pitch
    strike = row['Strikes']
    ball = row['Balls']

    korbb = row['KorBB']
    

    if korbb == 'Strikeout':
        strikeouts += 1
    elif korbb == 'Walk':
        walks += 1

    # process pitch
    # location = (PlateLocHeight, PlateLocSide) 
    plate_loc_height = row['PlateLocHeight']
    plate_loc_side = row['PlateLocSide']
    location = (plate_loc_height, plate_loc_side)

    pitch_type = row['TaggedPitchType']

    play_result = row['PlayResult']
    hit_type = row['TaggedHitType']

    angle = row['Angle']
    direction = row['Direction']
    distance = row['Distance']


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

    current_hitter.balls = ball
    current_hitter.strikes = strike

    current_hitter.process_pitch(location, pitch_type, pitch_of_pa, ball, strike)

    count_type = current_hitter.type_of_count()
    count = current_hitter.count()

    # Add tendency to the Tendencies instance
    tendencies.add_tendency(count_type, count, pitch_type, current_hitter.outcome, location)
    # Add the pitch to hitters_count as well
    hitters_count.add_pitch_to_count(count_type, (pitch_type, current_hitter.outcome, location))

    play_result_and_hit_type = (play_result, hit_type)
    angle_direction_distance = (angle, direction, distance)

    current_hitter.outcome_of_PA(play_result_and_hit_type, angle_direction_distance, korbb)
    

    # print("calculate_hit_position", current_hitter.calculate_hit_position(angle, distance))

    

# Save the final plate appearance
if current_hitter is not None:
    plate_appearances[current_pa_id] = current_hitter


# Output the plate appearances

# for pa_id, hitter in plate_appearances.items():
#     print(f"Plate Appearance {pa_id}: {hitter}")

# print(f"Total Strikeouts: {strikeouts}, Total Walks: {walks}")

# Output the tendencies across all plate appearances
# print("Tendencies across all Plate Appearances:", tendencies.get_tendencies())
# print(tendencies.tendencies)

print("print")
if hasattr(tendencies, 'tendencies'):  # Make sure the 'tendencies' attribute exists
    for key, value in tendencies.tendencies.items():
        print(key)
        # if key == "Hitter's Count 2-0":
        #     for j in value:
        #         print("hitters count - ", j)
        # elif key == "Pitcher's Count":
        #     for j in value:
        #         print("pitchers count - ", j)
        # elif key == "Neutral Count":
        #     for j in value:
        #         print("neutral count - ", j)
        # elif key == "Full Count":
        #     for j in value:
        #         print("full count - ", j)
        # else:
        #     for j in value:
        #         print("0-0 count - ", j)

            



