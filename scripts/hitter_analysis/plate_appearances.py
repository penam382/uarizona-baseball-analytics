import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# ---------- Step 1: Query the Database ---------- #
def query_database():
    """
    Queries the SQLite database to retrieve data for analysis.
    
    Returns:
        DataFrame: A pandas DataFrame containing the queried data.
    """
    conn = sqlite3.connect('/Users/marcopena/Documents/GitHub/uarizona-baseball-analytics/baseball_analytics.db')
    query = """
        SELECT 
            PA, PitchofPA, Batter, Strikes, Balls, KorBB, TaggedPitchType, PlayResult, 
            Angle, Direction, Distance, PlateLocHeight, PlateLocSide, PitchCall, TaggedHitType,
            AVG, OBP, SLG, swing, whiff, StadiumID, "2B", "3B", HR, chase, OutsOnPlay, GameID,
            PitcherThrows, ExitSpeed, RelSpeed, PositionAt110X, PositionAt110Y, PositionAt110Z,
            ContactPositionX, ContactPositionY, ContactPositionZ
        FROM pitches
        WHERE Batter = 'Caulfield, Garen';
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# ---------- Step 2: Process Count Type ---------- #
def type_of_count(balls, strikes):
    if balls == 0 and strikes == 0:
        return "0-0 Count"
    if balls == 3 and strikes == 2:
        return "Full Count"
    if (balls == 3 and strikes <= 1) or (balls == 2 and strikes in [0, 1]):
        return "Hitter's Count"
    if strikes >= 2 and balls < 3:
        return "Pitcher's Count"
    return "Neutral Count"

def add_count_type_column(df):
    df['CountType'] = df.apply(lambda row: type_of_count(row['Balls'], row['Strikes']), axis=1)
    return df

# ---------- Step 3: Process DataFrames ---------- #
def process_tendencies(df):
    df['AdjustedDirection'] = -df['Direction']
    tendencies = df[['PA', 'PitchofPA', 'Batter', 'TaggedPitchType', 'PlayResult',
                     'Angle', 'Direction', 'AdjustedDirection', 'Distance', 
                     'PlateLocHeight', 'PlateLocSide', 'CountType', 'PitchCall', 
                     'ExitSpeed', 'KorBB', 'PositionAt110X', 'PositionAt110Y', 
                     'PositionAt110Z', 'PitcherThrows', 'TaggedHitType', 
                     'ContactPositionX', 'ContactPositionY', 'ContactPositionZ', 
                     'swing', 'whiff', 'RelSpeed']].copy()
    return tendencies

def process_plate_appearances(df):
    return df.groupby('PA').agg(
        batter=('Batter', 'first'),
        total_pitches=('PitchofPA', 'max'),
        strikes=('Strikes', 'max'),
        balls=('Balls', 'max'),
        result=('PlayResult', 'last'),
        hit_type=('TaggedHitType', 'last')
    ).reset_index()

# ---------- Step 4: Player Stats and Visuals ---------- #
def calculate_player_stats(df):
    df['is_single'] = (df['PlayResult'] == 'Single').astype(int)
    df['is_double'] = (df['PlayResult'] == 'Double').astype(int)
    df['is_triple'] = (df['PlayResult'] == 'Triple').astype(int)
    df['is_home_run'] = (df['PlayResult'] == 'HomeRun').astype(int)

    stats = df.groupby('Batter').agg(
        games=('GameID', 'nunique'),
        plate_appearances=('OBP', lambda x: (x >= 0).sum()),
        hits=('AVG', lambda x: (x == 1).sum()),
        at_bats=('AVG', lambda x: (x >= 0).sum()),
        walks=('KorBB', lambda x: (x == 'Walk').sum()),
        strikeouts=('KorBB', lambda x: (x == 'Strikeout').sum()),
        singles=('is_single', 'sum'),
        doubles=('is_double', 'sum'),
        triples=('is_triple', 'sum'),
        homeruns=('is_home_run', 'sum'),
        batting_average=('AVG', lambda x: (x == 1).sum() / (x >= 0).sum() if (x >= 0).sum() > 0 else 0),
        on_base_percentage=('OBP', 'mean'),
        slugging=('SLG', 'mean')
    ).reset_index()

    stats[['batting_average', 'on_base_percentage', 'slugging']] = stats[['batting_average', 'on_base_percentage', 'slugging']].round(3)
    return stats

def display_hitter_stats_chart(df):
    columns = [
        "Batter", "games", "plate_appearances", "hits", "at_bats",
        "walks", "strikeouts", "singles", "doubles", "triples",
        "homeruns", "batting_average", "on_base_percentage", "slugging"
    ]
    table_data = df[columns].values
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(
        cellText=table_data,
        colLabels=columns,
        cellLoc='center',
        loc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width(col=list(range(len(columns))))
    plt.title("Hitter Stats", fontsize=16, pad=15)
    plt.show()

def display_hitter_stats_filtered_by_pitcher_throws(df, pitcher_throws):
    filtered_df = df[df['PitcherThrows'] == pitcher_throws]
    filtered_stats = calculate_player_stats(filtered_df)
    columns = [
        "Batter", "plate_appearances", "hits", "at_bats",
        "walks", "strikeouts", "singles", "doubles", "triples",
        "homeruns", "batting_average", "on_base_percentage", "slugging"
    ]
    table_data = filtered_stats[columns].values
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(
        cellText=table_data,
        colLabels=columns,
        cellLoc='center',
        loc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width(col=list(range(len(columns))))
    plt.title(f"Hitter Stats (Pitcher Throws: {pitcher_throws})", fontsize=16, pad=15)
    plt.show()

# ---------- Step 5: Whiff Metrics ---------- #
def calculate_whiff_metrics(df):
    metrics = df.groupby('TaggedPitchType').agg(
        total_pitches=('swing', 'count'),
        swings=('swing', 'sum'),
        whiffs=('whiff', 'sum'),
        chases=('chase', 'sum')
    ).reset_index()
    metrics.rename(columns={'swings': 'swings_count'}, inplace=True)
    metrics['whiff_percentage'] = (metrics['whiffs'] / metrics['swings_count']) * 100
    metrics['chase_percentage'] = (metrics['chases'] / metrics['swings_count']) * 100
    return metrics

def display_whiff_metrics_chart(metrics):
    metrics[['whiff_percentage', 'chase_percentage']] = metrics[['whiff_percentage', 'chase_percentage']].round(2)
    columns = ['TaggedPitchType', 'swings_count', 'whiff_percentage', 'chase_percentage']
    table_data = metrics[columns].values
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(
        cellText=table_data,
        colLabels=['Pitch Type', 'Swings', 'Whiff %', 'Chase %'],
        cellLoc='center',
        loc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width(col=list(range(len(columns))))
    plt.title("Whiff Metrics by Pitch Type", fontsize=14, pad=10)
    plt.show()

# ---------- Main Execution ---------- #
if __name__ == "__main__":
    print("Querying data...")
    raw_data = query_database()
    
    print("Adding count type...")
    data_with_count_type = add_count_type_column(raw_data)
    
    print("Processing tendencies...")
    tendencies_df = process_tendencies(data_with_count_type)
    pa_summary = process_plate_appearances(data_with_count_type)
    player_stats = calculate_player_stats(data_with_count_type)

    print("Exporting CSV files...")
    tendencies_df.to_csv("tendencies.csv", index=False)
    pa_summary.to_csv("plate_appearances.csv", index=False)
    player_stats.to_csv("hitter_stats.csv", index=False)
    
    print("Displaying charts...")
    display_hitter_stats_chart(player_stats)
    display_hitter_stats_filtered_by_pitcher_throws(data_with_count_type, 'Right')
    display_hitter_stats_filtered_by_pitcher_throws(data_with_count_type, 'Left')
    whiff_metrics = calculate_whiff_metrics(raw_data)
    display_whiff_metrics_chart(whiff_metrics)
