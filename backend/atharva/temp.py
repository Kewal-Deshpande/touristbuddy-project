import googlemaps
import joblib
import numpy as np
from datetime import datetime
import os
from dotenv import load_dotenv
import pandas as pd
import smtplib
from email.mime.text import MIMEText
import polyline
# Load environment variables
load_dotenv()

# Load models and data
model = joblib.load('./crime_model.pkl')
kmeans = joblib.load('./cluster_model.pkl')
crime_df = pd.read_csv('pune_crime_data.csv')
gmaps = googlemaps.Client(key="AIzaSyABXrzOdYntmVFt7vHZPMHEtAnvZLr7N-s")

# Prepare danger index
crime_counts = crime_df['Crime Area'].value_counts().to_dict()
max_crimes = max(crime_counts.values())
danger_index = {area: (count / max_crimes) * 100 for area, count in crime_counts.items()}


def predict_danger(lat, lng, time=None):
    time = time or datetime.now()
    features = pd.DataFrame([{
        'Hour': time.hour,
        'DayOfWeek': time.weekday(),
        'Month': time.month,
        'TotalCrimes': 0,
        'ViolentCrimes': 0,
        'Latitude': lat,
        'Longitude': lng
    }])
    
    cluster = kmeans.predict([[lat, lng]])[0]
    cluster_data = crime_df[crime_df['AreaCluster'] == cluster]
    
    features['TotalCrimes'] = cluster_data.shape[0]
    features['ViolentCrimes'] = cluster_data['Crime Type'].isin(['Murder', 'Rape', 'Robbery']).sum()
    
    return model.predict(features)[0]


def get_route_danger(route_coords):
    danger = 0
    for coord in route_coords:
        min_dist = float('inf')
        nearest_area = None
        for _, row in crime_df.iterrows():
            dist = np.linalg.norm(np.array(coord) - np.array([row['Latitude'], row['Longitude']]))
            if dist < min_dist:
                min_dist = dist
                nearest_area = row['Crime Area']
        if nearest_area in danger_index:
            danger += danger_index[nearest_area]
    return danger


def get_routes(start, end):
    directions = gmaps.directions(start, end, alternatives=True)
    routes = []

    for i, route in enumerate(directions):
        path = polyline.decode(route['overview_polyline']['points'])
        danger = get_route_danger(path)

        routes.append({
            'id': i,
            'danger': danger,
            'distance': route['legs'][0]['distance']['text'],
            'duration': route['legs'][0]['duration']['text'],
            'coordinates': path
        })
    return sorted(routes, key=lambda x: x['danger'])


