import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Step 1: Query the database
def query_database():
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

# Step 2: Determine count type based on strikes and balls
def type_of_count(balls, strikes):
    """
    Determines the type of count based on the given strikes and balls.
    """
    if balls == 0 and strikes == 0:
        return "0-0 Count"
    if balls == 3 and strikes == 2:
        return "Full Count"
    if (balls == 3 and strikes <= 1) or (balls == 2 and strikes == 1) or (balls == 2 and strikes == 0):
        return "Hitter's Count"
    if (strikes >= 2 and balls != 3):
        return "Pitcher's Count"
    return "Neutral Count"

# Step 3: Add a column for CountType
def add_count_type_column(df):
    """
    Adds a 'CountType' column to the DataFrame based on the balls and strikes.
    """
    df['CountType'] = df.apply(lambda row: type_of_count(row['Balls'], row['Strikes']), axis=1)
    return df

def process_tendencies(df):
    """
    Extract tendencies and group by CountType, including adjusted direction for Rapsodo convention.
    Filters out hits with extremely short distances (<50 feet).
    """

    # Adjust direction for Rapsodo convention
    df['AdjustedDirection'] = -df['Direction']



    # Include adjusted direction in the tendencies DataFrame
    tendencies = df[['PA', 'PitchofPA', 'Batter', 'TaggedPitchType', 'PlayResult',
                     'Angle', 'Direction', 'AdjustedDirection', 'Distance', 
                     'PlateLocHeight', 'PlateLocSide', 'CountType', 'PitchCall', 
                     'ExitSpeed', 'KorBB', 'PositionAt110X', 'PositionAt110Y', 
                     'PositionAt110Z', 'PitcherThrows', 'TaggedHitType', 
                     'ContactPositionX', 'ContactPositionY', 'ContactPositionZ', 'swing', 'whiff', 'RelSpeed']].copy()
    return tendencies



# Step 5: Summarize plate appearances
def process_plate_appearances(df):
    """
    Summarizes plate appearances by aggregating data.
    """
    return df.groupby('PA').agg(
        batter=('Batter', 'first'),
        total_pitches=('PitchofPA', 'max'),
        strikes=('Strikes', 'max'),
        balls=('Balls', 'max'),
        result=('PlayResult', 'last'),
        hit_type=('TaggedHitType', 'last')
    ).reset_index()


# Step 3: Calculate player stats
def calculate_player_stats(df):
    # Add columns for specific hit types
    df['is_single'] = (df['PlayResult'] == 'Single').astype(int)
    df['is_double'] = (df['PlayResult'] == 'Double').astype(int)
    df['is_triple'] = (df['PlayResult'] == 'Triple').astype(int)
    df['is_home_run'] = (df['PlayResult'] == 'HomeRun').astype(int)

    # Overall stats grouped by batter
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
        # Batting average: hits / at-bats (only if at-bats > 0)
        batting_average=('AVG', lambda x: (x == 1).sum() / (x >= 0).sum() if (x >= 0).sum() > 0 else 0),  
        # For each batter:
        #   - Count hits: (x == 1).sum()
        #   - Count at-bats: (x >= 0).sum()
        #   - Compute batting average: hits / at-bats if at-bats > 0, otherwise return 0.
        on_base_percentage=('OBP', 'mean'),
        slugging=('SLG', 'mean')
    ).reset_index()

    # Round numerical columns to the nearest thousandths
    numerical_columns = ['batting_average', 'on_base_percentage', 'slugging']
    stats[numerical_columns] = stats[numerical_columns].round(3)

    return stats


def display_hitter_stats_chart(df):
    """
    Displays a simple table chart of hitter stats using Matplotlib.
    """
    # Select relevant columns to display
    columns = [
        "Batter", "games", "plate_appearances", "hits", "at_bats",
        "walks", "strikeouts", "singles", "doubles", "triples",
        "homeruns", "batting_average", "on_base_percentage", "slugging"
    ]
    
    # Prepare data for the table
    table_data = df[columns].values
    column_headers = columns

    # Create the figure
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.axis('tight')
    ax.axis('off')

    # Create the table
    table = ax.table(
        cellText=table_data,
        colLabels=column_headers,
        cellLoc='center',
        loc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width(col=list(range(len(columns))))

    plt.title("Hitter Stats", fontsize=16, pad=15)
    plt.show()



def display_hitter_stats_filtered_by_pitcher_throws(df, pitcher_throws):
    """
    Displays a table chart of hitter stats filtered by the PitcherThrows data using Matplotlib.

    Parameters:
        df (DataFrame): The DataFrame containing hitter stats.
        pitcher_throws (str): The filter value for the 'PitcherThrows' column (e.g., 'R' or 'L').
    """
    # Filter the DataFrame based on the PitcherThrows column
    filtered_df = df[df['PitcherThrows'] == pitcher_throws]

    # Calculate player stats for the filtered data
    filtered_stats = calculate_player_stats(filtered_df)

    # Select relevant columns to display
    columns = [
        "Batter", "plate_appearances", "hits", "at_bats",
        "walks", "strikeouts", "singles", "doubles", "triples",
        "homeruns", "batting_average", "on_base_percentage", "slugging"
    ]

    # Prepare data for the table
    table_data = filtered_stats[columns].values
    column_headers = columns

    # Create the figure
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.axis('tight')
    ax.axis('off')

    # Create the table
    table = ax.table(
        cellText=table_data,
        colLabels=column_headers,
        cellLoc='center',
        loc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width(col=list(range(len(columns))))

    plt.title(f"Hitter Stats (Pitcher Throws: {pitcher_throws})", fontsize=16, pad=15)
    plt.show()


def map_hits_by_count_and_pitch(df):
    """
    Maps each hit type (single, double, triple, home run) to the corresponding pitch type and count type.

    Parameters:
        df (DataFrame): The DataFrame containing hitter data.

    Returns:
        DataFrame: A summary of hits grouped by count type and pitch type.
    """
    # Add columns for specific hit types
    df['is_single'] = (df['PlayResult'] == 'Single').astype(int)
    df['is_double'] = (df['PlayResult'] == 'Double').astype(int)
    df['is_triple'] = (df['PlayResult'] == 'Triple').astype(int)
    df['is_home_run'] = (df['PlayResult'] == 'HomeRun').astype(int)

    # Group by CountType and TaggedPitchType and aggregate hit metrics
    hits_by_count_and_pitch = df.groupby(['CountType', 'TaggedPitchType']).agg(
        singles=('is_single', 'sum'),
        doubles=('is_double', 'sum'),
        triples=('is_triple', 'sum'),
        homeruns=('is_home_run', 'sum')
    ).reset_index()

    # Print the mapping
    print("\nHits Mapped to Count Types and Pitch Types:")
    print(hits_by_count_and_pitch)

    return hits_by_count_and_pitch


def calculate_whiff_metrics(df):
    # Group by TaggedPitchType and calculate main metrics
    metrics = df.groupby('TaggedPitchType').agg(
        total_pitches=('swing', 'count'),       # Total pitches for each pitch type
        swings=('swing', 'sum'),               # Total swings
        whiffs=('whiff', 'sum'),               # Total whiffs
        chases=('chase', 'sum')                # Total chases
    ).reset_index()

    # Rename 'swings' to 'swings_count' to match expected chart input
    metrics.rename(columns={'swings': 'swings_count'}, inplace=True)

    # Add calculated percentages
    metrics['whiff_percentage'] = (metrics['whiffs'] / metrics['swings_count']) * 100
    metrics['chase_percentage'] = (metrics['chases'] / metrics['swings_count']) * 100

    return metrics







# Display metrics as a chart
def display_whiff_metrics_chart(metrics):
    # Format percentages to two decimal places
    metrics['whiff_percentage'] = metrics['whiff_percentage'].round(2)
    metrics['chase_percentage'] = metrics['chase_percentage'].round(2)

    # Select columns to display
    columns = ['TaggedPitchType', 'swings_count', 'whiff_percentage', 'chase_percentage']

    # Prepare data for the table
    table_data = metrics[columns].values
    column_headers = ['Pitch Type', 'Swings', 'Whiff %', 'Chase %']

    # Create the figure
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis('tight')
    ax.axis('off')

    # Create the table
    table = ax.table(
        cellText=table_data,
        colLabels=column_headers,
        cellLoc='center',
        loc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width(col=list(range(len(columns))))

    plt.title("Pitch Metrics by Type", fontsize=14, pad=10)
    plt.show()





if __name__ == "__main__":
    # Query data
    raw_data = query_database()

    # Add count type
    data_with_count_type = add_count_type_column(raw_data)

    # Process tendencies
    tendencies_df = process_tendencies(data_with_count_type)

    # Summarize plate appearances
    pa_summary = process_plate_appearances(data_with_count_type)

    # Calculate player stats
    player_stats = calculate_player_stats(data_with_count_type)

    # Export results
    tendencies_df.to_csv("tendencies.csv", index=False)
    pa_summary.to_csv("plate_appearances.csv", index=False)
    player_stats.to_csv("hitter_stats.csv", index=False)

    print("CSV files created: tendencies.csv, plate_appearances.csv, hitter_stats.csv")

    # Display stats as a Matplotlib table
    display_hitter_stats_chart(player_stats)

    # Display stats filtered by 'PitcherThrows'
    display_hitter_stats_filtered_by_pitcher_throws(data_with_count_type, 'Right')  # Filter for right-handed pitchers
    display_hitter_stats_filtered_by_pitcher_throws(data_with_count_type, 'Left')  # Filter for left-handed pitchers


    # Map hits by count type and pitch type
    hits_by_count_and_pitch = map_hits_by_count_and_pitch(data_with_count_type)
    

    # Calculate metrics
    pitch_metrics = calculate_whiff_metrics(raw_data)

    # Plot whiff percentage
    display_whiff_metrics_chart(pitch_metrics)