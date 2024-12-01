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
        AVG, OBP, SLG, swing, whiff, StadiumID, "2B", "3B", HR, chase, OutsOnPlay, GameID,
        PitcherThrows, ExitSpeed, RelSpeed
    FROM pitches
    WHERE Batter = 'Caulfield, Garen';
"""
df = pd.read_sql_query(query, conn)

# Close the database connection
conn.close()

# Initialize containers for data
plate_appearances = {}
tendencies = HitterTendencies()
player_stats = {}

# Track plate appearance ID
current_pa_id = 0  # Start with 0, increment whenever PA == 1

# Helper functions
def update_stats(stats, pa, play_result, korbb, obp, slg, avg):
    """Update stats dynamically for lefties or righties."""
    # Increment the plate appearance counter when PA == 1
    
    if obp == 1:
        stats['on_base_percentage'] += obp
    if obp >= 0:
        stats['plate_appearances'] += 1

    if avg == 1:
        stats['hits'] += 1
    if avg >= 0:
        stats['at_bats'] += 1

    if slg >= 1:
        stats['slugging'] += slg

    if play_result != "Undefined" and play_result is not None:
        
        if play_result not in ["Sacrifice"]:
            
            if play_result in ["Single", "Double", "Triple", "HomeRun"]:
                
                if play_result == "Single":
                    stats['singles'] += 1
                elif play_result == "Double":
                    stats['doubles'] += 1
                elif play_result == "Triple":
                    stats['triples'] += 1
                elif play_result == "HomeRun":
                    stats['homeruns'] += 1
    

def calculate_rates(stats):
    """Calculate batting average, OBP, and SLG."""
    return 

# Process the data
for i, row in df.iterrows():
    pa = row['PA']  # Indicates start of a new plate appearance
    batter = row['Batter']

    obp = row['OBP']
    avg = row['AVG']
    slg = row['SLG']
    
    # Increment the plate appearance counter when PA == 1
    if pa == 1:
        current_pa_id += 1

    # Initialize hitter stats if not already present
    if batter not in player_stats:
        player_stats[batter] = {
            'plate_appearances': 0,
            'hits': 0, 'walks': 0, 'strikeouts': 0,
            'homeruns': 0, 'doubles': 0, 'triples': 0, 'singles': 0,
            'at_bats': 0, 'batting_average': 0, 'on_base_percentage': 0, 'slugging': 0,
            'stats_vs_left': {
                'plate_appearances': 0, 'hits': 0, 'walks': 0, 'strikeouts': 0,
                'homeruns': 0, 'doubles': 0, 'triples': 0, 'singles': 0,
                'at_bats': 0, 'batting_average': 0, 'on_base_percentage': 0, 'slugging': 0
            },
            'stats_vs_right': {
                'plate_appearances': 0, 'hits': 0, 'walks': 0, 'strikeouts': 0,
                'homeruns': 0, 'doubles': 0, 'triples': 0, 'singles': 0,
                'at_bats': 0, 'batting_average': 0, 'on_base_percentage': 0, 'slugging': 0
            }
        }

    # Update or create a new Hitter instance for this PA
    if current_pa_id not in plate_appearances:
        plate_appearances[current_pa_id] = Hitter(current_pa_id, batter)
    current_hitter = plate_appearances[current_pa_id]

    # Process the current pitch
    location = (row['PlateLocHeight'], row['PlateLocSide'])
    current_hitter.process_pitch(location, row['TaggedPitchType'], row['PitchofPA'], row['Balls'], row['Strikes'])
    tendencies.add_tendency(
        current_hitter.type_of_count(),
        current_hitter.count(),
        row['TaggedPitchType'], row['PlayResult'], row['TaggedHitType'], row['PitchCall'],
        row['Angle'], row['Direction'], row['Distance'], location
    )

    # Update player-level stats
    if row['KorBB'] == 'Strikeout':
        player_stats[batter]['strikeouts'] += 1
    elif row['KorBB'] == 'Walk':
        player_stats[batter]['walks'] += 1


    

    update_stats(player_stats[batter], row['PA'], row['PlayResult'], row['KorBB'], row['OBP'], row['SLG'], row['AVG'])
    if row['PitcherThrows'] == 'Left':
        update_stats(player_stats[batter]['stats_vs_left'], row['PA'], row['PlayResult'], row['KorBB'], row['OBP'], row['SLG'], row['AVG'])
    elif row['PitcherThrows'] == 'Right':
        update_stats(player_stats[batter]['stats_vs_right'], row['PA'], row['PlayResult'], row['KorBB'], row['OBP'], row['SLG'], row['AVG'])


# Calculate final stats (overall and splits)
for batter, stats in player_stats.items():
    # Overall Stats
    if stats['at_bats'] > 0:
        stats['batting_average'] = stats['hits'] / stats['at_bats']
    else:
        stats['batting_average'] = 0

    if stats['plate_appearances'] > 0:
        stats['on_base_percentage'] = stats['on_base_percentage'] / stats['plate_appearances']
    else:
        stats['on_base_percentage'] = 0

    if stats['at_bats'] > 0:
        stats['slugging'] = stats['slugging'] / stats['at_bats']
    else:
        stats['slugging'] = 0

    # Stats vs Left-Handed Pitchers
    left_stats = stats['stats_vs_left']
    if left_stats['at_bats'] > 0:
        left_stats['batting_average'] = left_stats['hits'] / left_stats['at_bats']
    else:
        left_stats['batting_average'] = 0

    if left_stats['plate_appearances'] > 0:
        left_stats['on_base_percentage'] = left_stats['on_base_percentage'] / left_stats['plate_appearances']
    else:
        left_stats['on_base_percentage'] = 0

    if left_stats['at_bats'] > 0:
        left_stats['slugging'] = left_stats['slugging'] / left_stats['at_bats']
    else:
        left_stats['slugging'] = 0

    # Stats vs Right-Handed Pitchers
    right_stats = stats['stats_vs_right']
    if right_stats['at_bats'] > 0:
        right_stats['batting_average'] = right_stats['hits'] / right_stats['at_bats']
    else:
        right_stats['batting_average'] = 0

    if right_stats['plate_appearances'] > 0:
        right_stats['on_base_percentage'] = right_stats['on_base_percentage'] / right_stats['plate_appearances']
    else:
        right_stats['on_base_percentage'] = 0

    if right_stats['at_bats'] > 0:
        right_stats['slugging'] = right_stats['slugging'] / right_stats['at_bats']
    else:
        right_stats['slugging'] = 0

    # Optional: Print each player's stats for debugging
    # print(f"Player: {batter}")
    # print(f"  AVG: {stats['batting_average']:.3f}")
    # print(f"  OBP: {stats['on_base_percentage']:.3f}")
    # print(f"  SLG: {stats['slugging']:.3f}")



# Calculate rates
for batter, stats in player_stats.items():
    calculate_rates(stats)
    calculate_rates(stats['stats_vs_left'])
    calculate_rates(stats['stats_vs_right'])

# Write Full Stats CSV
df.to_csv('full_stats.csv', index=False)

# Write Hitter Stats CSV
with open('hitter_stats.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([
        'Batter', 'Plate Appearances', 'Hits', 'Walks', 'Strikeouts',
        'Homeruns', 'Doubles', 'Triples', 'Singles', 'At-Bats',
        'Batting Average', 'On-Base Percentage', 'Slugging Percentage',
        'Plate Appearances vs Left', 'Hits vs Left', 'Walks vs Left', 'Strikeouts vs Left',
        'Homeruns vs Left', 'Doubles vs Left', 'Triples vs Left', 'Singles vs Left', 
        'Batting Average vs Left', 'On-Base Percentage vs Left', 'Slugging Percentage vs Left',
        'Plate Appearances vs Right', 'Hits vs Right', 'Walks vs Right', 'Strikeouts vs Right',
        'Homeruns vs Right', 'Doubles vs Right', 'Triples vs Right', 'Singles vs Right',
        'Batting Average vs Right', 'On-Base Percentage vs Right', 'Slugging Percentage vs Right'
    ])
    for batter, stats in player_stats.items():
        writer.writerow([
            batter,
            stats['plate_appearances'], stats['hits'], stats['walks'], stats['strikeouts'],
            stats['homeruns'], stats['doubles'], stats['triples'], stats['singles'], 
            stats['at_bats'], stats['batting_average'], stats['on_base_percentage'], stats['slugging'],
            stats['stats_vs_left']['plate_appearances'], stats['stats_vs_left']['hits'], 
            stats['stats_vs_left']['walks'], stats['stats_vs_left']['strikeouts'], 
            stats['stats_vs_left']['homeruns'], stats['stats_vs_left']['doubles'], 
            stats['stats_vs_left']['triples'], stats['stats_vs_left']['singles'], 
            stats['stats_vs_left']['batting_average'], stats['stats_vs_left']['on_base_percentage'], 
            stats['stats_vs_left']['slugging'],
            stats['stats_vs_right']['plate_appearances'], stats['stats_vs_right']['hits'], 
            stats['stats_vs_right']['walks'], stats['stats_vs_right']['strikeouts'], 
            stats['stats_vs_right']['homeruns'], stats['stats_vs_right']['doubles'], 
            stats['stats_vs_right']['triples'], stats['stats_vs_right']['singles'], 
            stats['stats_vs_right']['batting_average'], stats['stats_vs_right']['on_base_percentage'], 
            stats['stats_vs_right']['slugging']
        ])

# Write Hitter Tendencies CSV
processor = CountAnalysis(tendencies)
processor.write_data_to_csv('hitter_tendencies.csv')

print("CSV files created: full_stats.csv, hitter_stats.csv, hitter_tendencies.csv")
# print(player_stats)
# print(plate_appearances)
