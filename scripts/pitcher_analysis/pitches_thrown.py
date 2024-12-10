import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import tkinter as tk
from tkinter import ttk

# Step 1: Load and Clean Data
def load_data(db_path):
    conn = sqlite3.connect(db_path)
    query = """
        SELECT 
            PA, PitchofPA, Pitcher, Strikes, Balls, KorBB, TaggedPitchType, PlayResult, RunsScored,
            VertRelAngle, HorzRelAngle, SpinRate, SpinAxis, Tilt, RelHeight, RelSide, Extension, VertBreak, 
            InducedVertBreak, HorzBreak, PlateLocHeight, PlateLocSide, ExitSpeed, RelSpeed, PreviousPitch, 
            called_strike, ooz, Angle, Direction, Distance, PitchCall, TaggedHitType, k, bb, bbspin, pitches, 
            zone, izswing, izmiss, AVG, OBP, SLG, swing, whiff, StadiumID, "2B", "3B", HR, chase, OutsOnPlay, 
            GameID, BatterSide, PitcherThrows, PositionAt110X, PositionAt110Y, PositionAt110Z
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

# Utility Functions
def save_data_to_csv(df, filename="pitch_data_for_tableau.csv"):
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

def add_count_type_column(df):
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

    df['CountType'] = df.apply(lambda row: type_of_count(row['Balls'], row['Strikes']), axis=1)
    return df

# Visualization Functions
def plot_scatter(df, x, y, title, xlabel, ylabel, xlim=None, ylim=None):
    unique_pitches = df['TaggedPitchType'].unique()
    colors = sns.color_palette("tab10", len(unique_pitches))
    pitch_color_map = {pitch: colors[i] for i, pitch in enumerate(unique_pitches)}

    plt.figure(figsize=(10, 6))
    for pitch in unique_pitches:
        subset = df[df['TaggedPitchType'] == pitch]
        plt.scatter(subset[x], subset[y], label=pitch, color=pitch_color_map[pitch], alpha=0.7)

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if xlim: plt.xlim(xlim)
    if ylim: plt.ylim(ylim)
    plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
    plt.axvline(0, color='black', linewidth=0.8, linestyle='--')
    plt.legend(title="Pitch Type", fontsize='small')
    plt.grid()
    plt.tight_layout()
    plt.show()

def plot_release_points(df):
    plot_scatter(
        df, 'RelSide', 'RelHeight',
        title='Pitcher Release Points by Pitch Type',
        xlabel='Release Side (ft)',
        ylabel='Release Height (ft)',
        xlim=(-6, 6),
        ylim=(-1, 7)
    )

def plot_vertical_vs_horizontal_break(df):
    plot_scatter(
        df, 'HorzBreak', 'VertBreak',
        title='Vertical Break vs Horizontal Break by Pitch Type',
        xlabel='Horizontal Break (inches)',
        ylabel='Vertical Break (inches)',
        xlim=(-30, 30),
        ylim=(-60, 30)
    )

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

# Metrics Calculations
def calculate_metrics(df):
    metrics = df.groupby('TaggedPitchType').agg(
        total_pitches=('TaggedPitchType', 'count'),
        total_hits=('PlayResult', lambda x: x.isin(['Single', 'Double', 'Triple', 'HomeRun']).sum()),
        avg_exit_speed=('ExitSpeed', 'mean'),
        avg_release_speed=('RelSpeed', 'mean'),
        avg_spin_rate=('SpinRate', 'mean'),
        avg_spin_axis=('SpinAxis', 'mean')
    ).reset_index()
    return metrics

def display_table(df, columns, title, rows=20):
    """
    Displays a subset of a DataFrame as a table-like chart.
    """
    table_data = df[columns].head(rows).values
    column_headers = columns
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(
        cellText=table_data,
        colLabels=column_headers,
        cellLoc='center',
        loc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width(list(range(len(columns))))
    plt.title(title, fontsize=14, pad=10)
    plt.show()

# Main Function
if __name__ == "__main__":
    DB_PATH = '/Users/marcopena/Documents/GitHub/uarizona-baseball-analytics/baseball_analytics.db'
    df = load_data(DB_PATH)

    # Add derived columns and save the DataFrame
    df = add_count_type_column(df)
    save_data_to_csv(df)

    # Plot visualizations
    plot_release_points(df)
    plot_vertical_vs_horizontal_break(df)
    plot_spin_rate_vs_spin_axis(df)  # Spin Rate vs. Spin Axis plot

    # Calculate and display metrics
    metrics = calculate_metrics(df)
    display_table(metrics, metrics.columns, "Pitch Metrics by Pitch Type", rows=30)
