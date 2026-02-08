import random
import pandas as pd
from datetime import datetime, timedelta

# List of crime areas in Pune (50-100 areas)
crime_areas = [
    "Wakad", "Baner", "Kothrud", "Hinjewadi", "Viman Nagar", "Koregaon Park", "Swargate", "Hadapsar", "Shivajinagar", 
    "Kondhwa", "Pashan", "Aundh", "Dhanori", "Lohegaon", "Yerawada", "Bhosari", "Nigdi", "Chinchwad", "Pimpri", "Kharadi", 
    "Vadgaon", "Warje", "Sinhagad Road", "Bavdhan", "Karvenagar", "Katraj", "Dhayari", "Undri", "NIBM Road", "Market Yard", 
    "Camp", "Deccan", "Sadashiv Peth", "Parvati", "Manjri", "Moshi", "Talegaon", "Alandi", "Ravet", "Charoli", "Wagholi", 
    "Narhe", "Fursungi", "Magarpatta", "Balewadi", "Hadapsar Industrial Area", "Tathawade", "Chakan", "Pimpri Industrial Area"
]

# Base coordinates for crime areas (simulated lat/lng for Pune)
base_coordinates = {area: (random.uniform(18.4, 18.7), random.uniform(73.7, 74.0)) for area in crime_areas}

# Crime types with probability distribution
crime_types = [
    "Murder", "Rape", "Kidnapping", "Robbery", "Molestation", "Tampering", "Acid Attacks", "Accident"
]
crime_probabilities = [0.05, 0.05, 0.08, 0.25, 0.15, 0.17, 0.01, 0.24]  # Logical probability distribution

# Function to generate a random date in 2024
def random_date():
    date = datetime(2024, random.randint(1, 12), random.randint(1, 28))
    return date.strftime('%Y-%m-%d')

# Function to generate a random time with preference for evening/night
# Function to generate a random time with preference for evening/night
def random_time():
    time_slots = [
        ("00:00-06:00", 0.3), ("06:00-12:00", 0.15), ("12:00-18:00", 0.20), ("18:00-24:00", 0.35)
    ]
    chosen_slot = random.choices(time_slots, weights=[slot[1] for slot in time_slots])[0][0]
    start_hour, end_hour = map(lambda x: int(x.split(':')[0]), chosen_slot.split('-'))  # Extract hours correctly
    random_hour = random.randint(start_hour, end_hour - 1)
    random_minute = random.randint(0, 59)
    return f"{random_hour:02d}:{random_minute:02d}"


# Generate dataset
rows = []
for _ in range(5000):
    area = random.choice(crime_areas)
    base_lat, base_lng = base_coordinates[area]
    lat = base_lat + random.uniform(-0.01, 0.01)
    lng = base_lng + random.uniform(-0.01, 0.01)
    crime_type = random.choices(crime_types, weights=crime_probabilities)[0]
    date = random_date()
    time = random_time()
    
    rows.append([area, lat, lng, crime_type, date, time])

# Create DataFrame
df = pd.DataFrame(rows, columns=["Crime Area", "Latitude", "Longitude", "Crime Type", "Date", "Time"])

# Save to CSV
df.to_csv("pune_crime_data.csv", index=False)

print("Dataset generated and saved as pune_crime_data.csv")
