import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import tkinter as tk
from tkinter import ttk

# Step 1: Load and Clean Data
def load_data():
    conn = sqlite3.connect('/Users/marcopena/Documents/GitHub/uarizona-baseball-analytics/baseball_analytics.db')
    query = """
        SELECT 
            PA, PitchofPA, Pitcher, Strikes, Balls, KorBB, TaggedPitchType, PlayResult, RunsScored,
            VertRelAngle, HorzRelAngle, SpinRate, SpinAxis, Tilt, RelHeight, RelSide, Extension, VertBreak, InducedVertBreak, 
            HorzBreak, PlateLocHeight, PlateLocSide, ExitSpeed, RelSpeed, PreviousPitch, called_strike, ooz,
            Angle, Direction, Distance, PitchCall, TaggedHitType, k, bb, bbspin, pitches, zone, izswing, izmiss,
            AVG, OBP, SLG, swing, whiff, StadiumID, "2B", "3B", HR, chase, OutsOnPlay, GameID, BatterSide,
            PitcherThrows, PositionAt110X, PositionAt110Y, PositionAt110Z
        FROM pitches
        WHERE Pitcher = 'Berg, Jack';
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Add derived columns
    df['is_single'] = df['PlayResult'] == 'Single'
    df['is_double'] = df['PlayResult'] == 'Double'
    df['is_triple'] = df['PlayResult'] == 'Triple'
    df['is_home_run'] = df['PlayResult'] == 'HomeRun'
    return df

# Step 2: Calculate Metrics
def calculate_metrics(df):
    metrics = df.groupby('TaggedPitchType').agg(
        total_pitches=('TaggedPitchType', 'count'),
        total_hits=('PlayResult', lambda x: (x.isin(['Single', 'Double', 'Triple', 'HomeRun'])).sum()),
        avg_exit_speed=('ExitSpeed', 'mean'),
        avg_release_speed=('RelSpeed', 'mean'),
        avg_spin_rate=('SpinRate', 'mean'),
        avg_spin_axis=('SpinAxis', 'mean'),
    )
    return metrics

# Step 3: Plot Release Points
def plot_release_points(df):
    unique_pitches = df['TaggedPitchType'].unique()
    colors = sns.color_palette("tab10", len(unique_pitches))
    pitch_color_map = {pitch: colors[i] for i, pitch in enumerate(unique_pitches)}

    plt.figure(figsize=(8, 6))
    for pitch in unique_pitches:
        subset = df[df['TaggedPitchType'] == pitch]
        plt.scatter(
            subset['RelSide'],
            subset['RelHeight'],
            label=pitch,
            color=pitch_color_map[pitch],
            alpha=0.7
        )

    plt.xlabel('Release Side (ft)')
    plt.ylabel('Release Height (ft)')
    plt.title('Pitcher Release Points by Pitch Type')
    plt.xlim(-6, 6)
    plt.ylim(-1, 7)
    plt.legend(title="Pitch Type", loc="best", bbox_to_anchor=(1.05, 1), fontsize='small')
    plt.grid()
    plt.tight_layout()
    plt.show()

# Step 4: Plot Vertical vs Horizontal Break
def plot_vertical_vs_horizontal_break(df):
    unique_pitches = df['TaggedPitchType'].unique()
    colors = sns.color_palette("tab10", len(unique_pitches))
    pitch_color_map = {pitch: colors[i] for i, pitch in enumerate(unique_pitches)}

    plt.figure(figsize=(10, 6))
    for pitch in unique_pitches:
        subset = df[df['TaggedPitchType'] == pitch]
        plt.scatter(
            subset['HorzBreak'], subset['VertBreak'],
            label=pitch, color=pitch_color_map[pitch], alpha=0.7
        )

    plt.xlim(-30, 30)
    plt.ylim(-60, 30)
    plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
    plt.axvline(0, color='black', linewidth=0.8, linestyle='--')
    plt.xlabel('Horizontal Break (inches)')
    plt.ylabel('Vertical Break (inches)')
    plt.title('Vertical Break vs. Horizontal Break by Pitch Type')
    plt.legend(title="Pitch Type", loc="best", fontsize='small')
    plt.grid()
    plt.tight_layout()
    plt.show()

# Step 5: Plot Spin Rate vs Spin Axis
def plot_spin_rate_vs_spin_axis(df):
    spin_axis_radians = np.radians(df['SpinAxis'])
    pitch_types = df['TaggedPitchType'].unique()
    pitch_type_mapping = {pitch: i for i, pitch in enumerate(pitch_types)}
    pitch_colors = [pitch_type_mapping[pitch] for pitch in df['TaggedPitchType']]

    fig = plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, polar=True)

    scatter = ax.scatter(
        spin_axis_radians, df['SpinRate'], 
        c=pitch_colors, 
        cmap='rainbow', alpha=0.7, edgecolors='black'
    )

    legend_labels = [
        plt.Line2D([0], [0], marker='o', color='w', 
                   markerfacecolor=plt.cm.rainbow(i/len(pitch_types)), markersize=10, label=pitch)
        for pitch, i in pitch_type_mapping.items()
    ]
    ax.legend(handles=legend_labels, title='Pitch Types', bbox_to_anchor=(1.2, 1.1), loc='upper right')

    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_title('Spin Axis x Spin Rate', va='bottom', fontsize=14, weight='bold')
    plt.tight_layout()
    plt.show()

# Step 6: Add Count Type Column
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

# Step 7: Calculate Hits by Pitch and Count Type
def calculate_hits_by_pitch_and_count(df):
    hits_by_pitch_and_count = df[df['PlayResult'].isin(['Single', 'Double', 'Triple', 'HomeRun'])] \
        .groupby(['TaggedPitchType', 'CountType']).size().reset_index(name='HitFrequency')
    return hits_by_pitch_and_count


def display_count_type_table_scrollable(df):
    """
    Displays a scrollable table for CountType, Balls/Strikes, TaggedHitType, and KorBB.
    Replaces 'Undefined' in KorBB with a blank value for better readability.
    """
    required_columns = ['TaggedPitchType', 'CountType', 'Balls', 'Strikes', 'PlayResult', 'TaggedHitType', 'KorBB']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        print(f"Error: Missing required columns: {missing_columns}")
        return

    # Replace 'Undefined' in KorBB with a blank string
    df['KorBB'] = df['KorBB'].replace('Undefined', '')
    df['TaggedHitType'] = df['TaggedHitType'].replace('Undefined', '')
    df['PlayResult'] = df['PlayResult'].replace('Undefined', '')

    # Extract the necessary columns
    table_data = df[required_columns]

    # Create the tkinter GUI
    root = tk.Tk()
    root.title("CountType Table")

    # Create a frame for the table
    frame = ttk.Frame(root)
    frame.pack(fill='both', expand=True)

    # Create a Treeview widget
    tree = ttk.Treeview(frame, columns=required_columns, show='headings', height=20)
    tree.pack(side='left', fill='both', expand=True)

    # Add column headings
    for col in required_columns:
        tree.heading(col, text=col)
        tree.column(col, anchor='center', width=100)

    # Add data to the Treeview
    for index, row in table_data.iterrows():
        tree.insert('', 'end', values=row.tolist())

    # Add a scrollbar
    scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
    scrollbar.pack(side='right', fill='y')

    # Configure Treeview to work with scrollbar
    tree.configure(yscrollcommand=scrollbar.set)

    root.mainloop()



def save_data_to_csv(df, filename="pitch_data_for_tableau.csv"):
    """
    Saves the cleaned and augmented DataFrame to a CSV file.
    """
    # Add any additional calculated fields if necessary
    df['pitch_category'] = df['TaggedPitchType'].astype('category').cat.codes  # Encode pitch type for visualization
    
    # Save to a CSV file
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")



def display_pitcher_stats_table(stats, rows=20):
    """
    Displays a table-like chart for pitcher statistics.
    """
    # Extract the necessary columns
    table_data = stats[['Pitcher', 'games', 'hits', 'runs_allowed', 'walks', 'strikeouts', 'WHIP', 'AVG']].head(rows)
    
    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis('tight')
    ax.axis('off')
    
    # Create a table
    table = ax.table(
        cellText=table_data.values,
        colLabels=table_data.columns,
        cellLoc='center',
        loc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width(col=list(range(len(table_data.columns))))
    
    # Set title above the table
    plt.suptitle("Pitcher Statistics Table", fontsize=16, weight='bold', y=0.98)  # Adjust y for spacing
    
    plt.show()




def calculate_pitcher_stats(df):
    """
    Calculates statistics for each pitcher, excluding innings pitched.
    """
    # Ensure data consistency
    df['Walks'] = df['KorBB'].apply(lambda x: 1 if x == 'Walk' else 0)  # Count Walks
    df['Hits'] = df['PlayResult'].apply(lambda x: 1 if x in ['Single', 'Double', 'Triple', 'HomeRun'] else 0)  # Count Hits

    stats = df.groupby('Pitcher').agg(
        games=('GameID', 'nunique'),
        hits=('Hits', 'sum'),
        runs_allowed=('RunsScored', 'sum'),
        walks=('Walks', 'sum'),
        strikeouts=('KorBB', lambda x: (x == 'Strikeout').sum()),
        WHIP=('Pitcher', lambda x: (df.loc[x.index, 'Walks'].sum() + df.loc[x.index, 'Hits'].sum()) /
                                  max(df.loc[x.index, 'OutsOnPlay'].sum() / 3, 1) if df.loc[x.index, 'OutsOnPlay'].sum() > 0 else 0),
        AVG=('AVG', 'mean')  # Batting average against
    )
    stats = stats.reset_index()

    # Round WHIP and AVG to 3 decimal places
    stats['WHIP'] = stats['WHIP'].round(3)
    stats['AVG'] = stats['AVG'].round(3)

    return stats





def calculate_pitcher_metrics(df):
    metrics = df.groupby('TaggedPitchType').agg(
        total_pitches=('TaggedPitchType', 'count'),           # Total number of pitches
        whiffs=('whiff', 'sum'),                              # Total whiffs
        chases=('chase', 'sum'),                              # Total chases
        total_hits=('PlayResult', lambda x: (x.isin(['Single', 'Double', 'Triple', 'HomeRun'])).sum())  # Total hits
    ).reset_index()

    # Add calculated percentages
    metrics['whiff_rate'] = (metrics['whiffs'] / metrics['total_pitches']) * 100
    metrics['chase_rate'] = (metrics['chases'] / metrics['total_pitches']) * 100
    metrics['hit_rate'] = (metrics['total_hits'] / metrics['total_pitches']) * 100

    return metrics

# Display pitcher metrics as a table-like chart
def display_pitcher_metrics_chart(metrics):
    # Format percentages to two decimal places
    metrics['whiff_rate'] = metrics['whiff_rate'].round(2)
    metrics['chase_rate'] = metrics['chase_rate'].round(2)
    metrics['hit_rate'] = metrics['hit_rate'].round(2)

    # Select columns to display
    columns = ['TaggedPitchType', 'total_pitches', 'whiff_rate', 'chase_rate', 'hit_rate']

    # Prepare data for the table
    table_data = metrics[columns].values
    column_headers = ['Pitch Type', 'Total Pitches', 'Whiff %', 'Chase %', 'Hit %']

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

    plt.title("Pitcher Metrics by Pitch Type", fontsize=14, pad=10)
    plt.show()



def calculate_pitch_metrics(df):
    metrics = df.groupby('TaggedPitchType').agg(
        total_pitches=('TaggedPitchType', 'count'),           # Total number of pitches
        sits=('RelSpeed', lambda x: f"{x.quantile(0.1):.0f}-{x.quantile(0.9):.0f}"),  # Narrower speed range (10th-90th percentile)
        top_speed=('RelSpeed', 'max'),                       # Top speed
        avg_spin_rate=('SpinRate', 'mean'),                  # Average spin rate
        carry_sink=('InducedVertBreak', 'mean'),             # Carry or sink
        ext=('Extension', 'mean'),                           # Average extension
        rel_height=('RelHeight', 'mean'),                    # Average release height
        rel_side=('RelSide', 'mean')                         # Average release side
    ).reset_index()

    # Rename columns for clarity and style
    metrics.rename(columns={
        'TaggedPitchType': 'Pitch Type',
        'total_pitches': 'X',
        'sits': 'Sits',
        'top_speed': 'Top',
        'avg_spin_rate': 'Spin',
        'carry_sink': 'Carry/Sink',
        'ext': 'Ext',
        'rel_height': 'RelH',
        'rel_side': 'RelSide'
    }, inplace=True)

    # Round numerical values for clarity
    numerical_cols = ['Spin', 'Carry/Sink', 'Ext', 'RelH', 'RelSide']
    metrics[numerical_cols] = metrics[numerical_cols].round(1)
    metrics['Top'] = metrics['Top'].round(1)


    return metrics

# Display Formatted Table
def display_formatted_metrics_table(metrics):
    # Select columns to display
    columns = ['Pitch Type', 'X', 'Sits', 'Top', 'Spin', 'Carry/Sink', 'RelH', 'RelSide', 'Ext']
    table_data = metrics[columns].values
    column_headers = columns

    # Create the figure
    fig, ax = plt.subplots(figsize=(12, 4))
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





# Main Function
if __name__ == "__main__":
    df = load_data()
    count_type_column = add_count_type_column(df)
    
    save_data_to_csv(df)

    metrics = calculate_metrics(df)

    plot_release_points(df)
    plot_vertical_vs_horizontal_break(df)
    plot_spin_rate_vs_spin_axis(df)

    # Display the table-like chart
    display_count_type_table_scrollable(count_type_column)

    # Calculate pitcher stats
    pitcher_stats = calculate_pitcher_stats(df)

    # Display or save results
    # print(pitcher_stats.head())
    display_pitcher_stats_table(pitcher_stats, rows=30)

    pitcher_metrics = calculate_pitcher_metrics(df)
    display_pitcher_metrics_chart(pitcher_metrics)


    pitcher_stats = calculate_pitch_metrics(df)

    # Display formatted metrics table
    display_formatted_metrics_table(pitcher_stats)
