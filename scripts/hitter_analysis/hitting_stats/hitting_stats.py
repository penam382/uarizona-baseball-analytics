import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('/Users/marcopena/Documents/GitHub/uarizona-baseball-analytics/baseball_analytics.db')

# Query only relevant data for "Caulfield, Garen"
query = "SELECT * FROM pitches WHERE Batter = 'Caulfield, Garen';"
df = pd.read_sql_query(query, conn)

# Close the database connection
conn.close()

# Player stats, with separate entries for left-handed and right-handed pitchers
player_stats = {}

# Loop through each row of data
for i, row in df.iterrows():
    player_id = row['BatterId']
    
    # Initialize player data if not already in the dictionary
    if player_id not in player_stats:
        player_stats[player_id] = {
            'plate_appearances': 0,
            'hits': 0,  # Initialize hits for this player
            'walks': 0,
            'strikeouts': 0,
            'homeruns': 0,
            'doubles': 0,
            'triples': 0,
            'singles': 0,  # Track singles separately
            'at_bats': 0,  # Track at-bats
            'batting_average': 0,
            'on_base_percentage': 0,
            'slugging': 0,
            'games': set(),  # Track unique games to avoid counting the same game multiple times
            'stats_vs_left': {
                'plate_appearances': 0,
                'hits': 0,
                'walks': 0,
                'strikeouts': 0,
                'homeruns': 0,
                'doubles': 0,
                'triples': 0,
                'singles': 0,
                'at_bats': 0,
                'batting_average': 0,
                'on_base_percentage': 0,
                'slugging': 0
            },
            'stats_vs_right': {
                'plate_appearances': 0,
                'hits': 0,
                'walks': 0,
                'strikeouts': 0,
                'homeruns': 0,
                'doubles': 0,
                'triples': 0,
                'singles': 0,
                'at_bats': 0,
                'batting_average': 0,
                'on_base_percentage': 0,
                'slugging': 0
            }
        }

    plate_appearances = row['PA']
    play_result = row['PlayResult']
    korbb = row['KorBB']
    pitcher_throws = row['PitcherThrows']

    # Stats from the current row
    homeruns = row['HR']
    triples = row['3B']
    doubles = row['2B']
    games = row['GameID']

    # Handle strikeouts and walks
    if korbb == 'Strikeout':
        player_stats[player_id]['strikeouts'] += 1
    elif korbb == 'Walk':
        player_stats[player_id]['walks'] += 1

    # Track plate appearances and at-bats (excluding walks and strikeouts)
    if play_result != "Undefined":
        player_stats[player_id]['plate_appearances'] += plate_appearances
        if korbb not in ['Walk']:
            player_stats[player_id]['at_bats'] += 1
    
    # Track hits (singles, doubles, triples, homeruns)
    if play_result in ["Single", "Double", "Triple", "Homerun"]:
        player_stats[player_id]['hits'] += 1
        if play_result == "Single":
            player_stats[player_id]['singles'] += 1
        elif play_result == "Double":
            player_stats[player_id]['doubles'] += 1
        elif play_result == "Triple":
            player_stats[player_id]['triples'] += 1
        elif play_result == "Homerun":
            player_stats[player_id]['homeruns'] += 1

    # Track stats against lefty or righty pitchers
    if pitcher_throws == 'Left':  # Left-handed pitcher
        if play_result != "Undefined":
            player_stats[player_id]['stats_vs_left']['plate_appearances'] += plate_appearances
            if korbb not in ['Walk']:
                player_stats[player_id]['stats_vs_left']['at_bats'] += 1
            if play_result in ["Single", "Double", "Triple", "Homerun"]:
                player_stats[player_id]['stats_vs_left']['hits'] += 1
                if play_result == "Single":
                    player_stats[player_id]['stats_vs_left']['singles'] += 1
                elif play_result == "Double":
                    player_stats[player_id]['stats_vs_left']['doubles'] += 1
                elif play_result == "Triple":
                    player_stats[player_id]['stats_vs_left']['triples'] += 1
                elif play_result == "Homerun":
                    player_stats[player_id]['stats_vs_left']['homeruns'] += 1
    elif pitcher_throws == 'Right':  # Right-handed pitcher
        if play_result != "Undefined":
            player_stats[player_id]['stats_vs_right']['plate_appearances'] += plate_appearances
            if korbb not in ['Walk']:
                player_stats[player_id]['stats_vs_right']['at_bats'] += 1
            if play_result in ["Single", "Double", "Triple", "Homerun"]:
                player_stats[player_id]['stats_vs_right']['hits'] += 1
                if play_result == "Single":
                    player_stats[player_id]['stats_vs_right']['singles'] += 1
                elif play_result == "Double":
                    player_stats[player_id]['stats_vs_right']['doubles'] += 1
                elif play_result == "Triple":
                    player_stats[player_id]['stats_vs_right']['triples'] += 1
                elif play_result == "Homerun":
                    player_stats[player_id]['stats_vs_right']['homeruns'] += 1

    # Track the games to avoid duplicate counts
    player_stats[player_id]['games'].add(games)

# Calculate Batting Average, OBP, and Slugging after the loop for both lefty and righty stats
for player_id, stats in player_stats.items():
    # Batting Average (AVG)
    if stats['stats_vs_left']['at_bats'] > 0:
        stats['stats_vs_left']['batting_average'] = stats['stats_vs_left']['hits'] / stats['stats_vs_left']['at_bats']
    if stats['stats_vs_right']['at_bats'] > 0:
        stats['stats_vs_right']['batting_average'] = stats['stats_vs_right']['hits'] / stats['stats_vs_right']['at_bats']

    # On-base Percentage (OBP)
    if stats['stats_vs_left']['plate_appearances'] > 0:
        stats['stats_vs_left']['on_base_percentage'] = (stats['stats_vs_left']['hits'] + stats['stats_vs_left']['walks']) / stats['stats_vs_left']['plate_appearances']
    if stats['stats_vs_right']['plate_appearances'] > 0:
        stats['stats_vs_right']['on_base_percentage'] = (stats['stats_vs_right']['hits'] + stats['stats_vs_right']['walks']) / stats['stats_vs_right']['plate_appearances']

    # Slugging Percentage (SLG)
    if stats['stats_vs_left']['at_bats'] > 0:
        stats['stats_vs_left']['slugging'] = (stats['stats_vs_left']['singles'] + 2 * stats['stats_vs_left']['doubles'] + 3 * stats['stats_vs_left']['triples'] + 4 * stats['stats_vs_left']['homeruns']) / stats['stats_vs_left']['at_bats']
    if stats['stats_vs_right']['at_bats'] > 0:
        stats['stats_vs_right']['slugging'] = (stats['stats_vs_right']['singles'] + 2 * stats['stats_vs_right']['doubles'] + 3 * stats['stats_vs_right']['triples'] + 4 * stats['stats_vs_right']['homeruns']) / stats['stats_vs_right']['at_bats']

# Now you can print or analyze the `player_stats` dictionary for each player's stats against lefties and righties
print(player_stats)
