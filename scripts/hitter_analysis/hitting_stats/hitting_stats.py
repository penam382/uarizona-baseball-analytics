import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('/Users/marcopena/Documents/GitHub/uarizona-baseball-analytics/baseball_analytics.db')

# Query only relevant data for "Caulfield, Garen"
query = "SELECT * FROM pitches WHERE Batter = 'Caulfield, Garen';"
df = pd.read_sql_query(query, conn)

# Close the database connection
conn.close()

# Player Name, Batting Average, OBP, SLG, HRs, RBIs, specific hitting against lefty or righty
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
            'games': set()  # Track unique games to avoid counting the same game multiple times
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

    # Track the games to avoid duplicate counts
    player_stats[player_id]['games'].add(games)

# Calculate Batting Average, OBP, and Slugging after the loop
for player_id, stats in player_stats.items():
    # Batting Average (AVG)
    if stats['at_bats'] > 0:
        stats['batting_average'] = stats['hits'] / stats['at_bats']

    # On-base Percentage (OBP)
    if stats['plate_appearances'] > 0:
        stats['on_base_percentage'] = (stats['hits'] + stats['walks']) / stats['plate_appearances']

    # Slugging Percentage (SLG)
    if stats['at_bats'] > 0:
        stats['slugging'] = (stats['singles'] + 2 * stats['doubles'] + 3 * stats['triples'] + 4 * stats['homeruns']) / stats['at_bats']

# Now you can print or analyze the `player_stats` dictionary for each player's stats
print(player_stats)
