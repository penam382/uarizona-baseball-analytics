import sqlite3
import pandas as pd

# Step 1: Query the database
def query_database():
    conn = sqlite3.connect('/Users/marcopena/Documents/GitHub/uarizona-baseball-analytics/baseball_analytics.db')
    query = """
        SELECT 
            PA, PitchofPA, Batter, Strikes, Balls, KorBB, TaggedPitchType, PlayResult, 
            Angle, Direction, Distance, PlateLocHeight, PlateLocSide, PitchCall, TaggedHitType,
            AVG, OBP, SLG, swing, whiff, StadiumID, "2B", "3B", HR, chase, OutsOnPlay, GameID,
            PitcherThrows, ExitSpeed, RelSpeed, PositionAt110X, PositionAt110Y, PositionAt110Z
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

# Step 4: Process tendencies
def process_tendencies(df):
    """
    Extract tendencies and group by CountType.
    """
    tendencies = df[['PA', 'PitchofPA', 'Batter', 'TaggedPitchType', 'PlayResult', 
                     'Angle', 'Direction', 'Distance', 'PlateLocHeight', 'PlateLocSide', 'CountType', 'PitchCall', 'ExitSpeed', 'KorBB',
                     'PositionAt110X', 'PositionAt110Y', 'PositionAt110Z']].copy()
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

# Step 6: Calculate hit positions
def calculate_hit_positions(df):
    """
    Determines the hit position based on angle and distance.
    """
    def determine_position(angle, distance):
        if distance < 90:
            if -45 <= angle <= -15:
                return "Third Base"
            elif -15 < angle < 0:
                return "Up The Middle"
            elif 0 <= angle < 15:
                return "Second Base"
            elif 15 <= angle <= 45:
                return "First Base"
            elif -90 <= angle < -45:
                return "Shortstop"
            elif 45 < angle <= 90:
                return "Second Base"
        elif distance >= 90:
            if -45 <= angle <= -15:
                return "Left Field"
            elif -15 < angle < 15:
                return "Center Field"
            elif 15 <= angle <= 45:
                return "Right Field"
            elif -90 <= angle < -45:
                return "Left-Center Field"
            elif 45 < angle <= 90:
                return "Right-Center Field"
        return "Foul Territory"
    
    df['HitPosition'] = df.apply(lambda row: determine_position(row['Angle'], row['Distance']), axis=1)
    return df

if __name__ == "__main__":
    # Query data
    raw_data = query_database()

    # Add count type
    data_with_count_type = add_count_type_column(raw_data)

    # Process tendencies
    tendencies_df = process_tendencies(data_with_count_type)

    # Summarize plate appearances
    pa_summary = process_plate_appearances(data_with_count_type)

    # Calculate hit positions
    updated_data = calculate_hit_positions(data_with_count_type)

    # Export results
    tendencies_df.to_csv("tendencies.csv", index=False)
    # pa_summary.to_csv("plate_appearances.csv", index=False)
    # updated_data.to_csv("full_data.csv", index=False)

    print("CSV files created: tendencies.csv, plate_appearances.csv, full_data.csv")
