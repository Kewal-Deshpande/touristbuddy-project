import pandas as pd
from datetime import datetime, timedelta

# Load the dataset
df = pd.read_csv('crime_data_pune.csv')

# Convert 'Time' column to proper time format
df['Time'] = pd.to_datetime(df['Time'], format='%H:%M').dt.time

def get_crime_locations():
    # Get current time
    now = datetime.now().time()

    # Calculate time range (±2 hours)
    lower_bound = (datetime.combine(datetime.today(), now) - timedelta(hours=2)).time()
    upper_bound = (datetime.combine(datetime.today(), now) + timedelta(hours=2)).time()

    # Handle cases where the time range crosses midnight
    if lower_bound <= upper_bound:
        filtered_df = df[(df['Time'] >= lower_bound) & (df['Time'] <= upper_bound)]
    else:
        # If range crosses midnight, select times in two parts
        filtered_df = df[(df['Time'] >= lower_bound) | (df['Time'] <= upper_bound)]

    print(f"Current Time: {now.strftime('%H:%M')}")
    print(f"Filtering crimes between: {lower_bound.strftime('%H:%M')} - {upper_bound.strftime('%H:%M')}")
    print(filtered_df)

    return filtered_df
