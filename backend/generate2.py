import random
from datetime import datetime, timedelta
import csv

# Defining parameters
crime_types = ["Murder", "Rape", "Kidnapping", "Robbery", "Molestation", "Tampering", "Acid Attacks", "Accident"]
time_periods = [("00:00-06:00", 0.3), ("06:00-12:00", 0.15), ("12:00-18:00", 0.20), ("18:00-24:00", 0.35)]
crime_weights = [0.05, 0.05, 0.08, 0.25, 0.15, 0.17, 0.01, 0.24]

# Latitude and Longitude bounds for Pune city (more accurate for the city center)
latitude_bounds = (18.569009, 18.444587)  # approximate bounds of Pune city latitude
longitude_bounds = (73.759484, 73.942139)  # approximate bounds of Pune city longitude

# Function to generate random latitude and longitude in Pune city
def random_location():
    lat = random.uniform(latitude_bounds[0], latitude_bounds[1])
    lon = random.uniform(longitude_bounds[0], longitude_bounds[1])
    return lat, lon

# Function to generate a random time period with a specific time inside that period
def random_time_period():
    period, weight = random.choices(time_periods, weights=[x[1] for x in time_periods])[0]
    start_time, end_time = period.split("-")

    # Convert the start and end time to minutes from midnight
    start_hour, start_minute = map(int, start_time.split(":"))
    end_hour, end_minute = map(int, end_time.split(":"))
    
    start_minutes = start_hour * 60 + start_minute
    end_minutes = end_hour * 60 + end_minute

    # Generate a random minute within the time range
    random_minutes = random.randint(start_minutes, end_minutes)
    
    # Convert minutes back to hour:minute format
    random_hour = random_minutes // 60
    random_minute = random_minutes % 60
    
    return f"{random_hour:02}:{random_minute:02}"

# Function to generate a random crime type
def random_crime_type():
    crime = random.choices(crime_types, weights=crime_weights)[0]
    return crime

# Generate a random date within the given range
def random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

# Generate dataset
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 12, 31)

data = []
for _ in range(500):  # Let's generate 500 records for example
    lat, lon = random_location()
    date = random_date(start_date, end_date).strftime('%Y-%m-%d')
    time_period = random_time_period()
    crime_type = random_crime_type()
    data.append([lat, lon, date, time_period, crime_type])

# Save the data as a CSV file
with open("crime_data_pune.csv", mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Latitude", "Longitude", "Date", "Time", "Crime Type"])
    writer.writerows(data)

# Print the first few records to show the output
for record in data[:5]:  # Showing only the first 5 records for brevity
    print(record)
