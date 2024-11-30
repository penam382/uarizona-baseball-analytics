# generate_csv.py
import pandas as pd

def write_to_csv(data, filename):
    """ Write data to a CSV file """
    # Create a DataFrame from the data
    df = pd.DataFrame(data)
    # Write to CSV
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")
