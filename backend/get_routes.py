import googlemaps
import joblib
import numpy as np
from datetime import datetime, timedelta
import polyline
import os
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

# Load all trained artifacts
model = joblib.load('models/best_model.pkl')  # From train.py's best model selection
kmeans = joblib.load('models/kmeans.pkl')
scaler = joblib.load('models/scaler.pkl')
hotspot_coords = joblib.load('models/hotspot_coords.pkl')

# Load precomputed features
hourly_counts = joblib.load('models/hourly_counts.pkl')
daily_counts = joblib.load('models/daily_counts.pkl')
monthly_violent = joblib.load('models/monthly_violent.pkl')

gmaps = googlemaps.Client(key="AIzaSyABXrzOdYntmVFt7vHZPMHEtAnvZLr7N-s")

def get_features(lat, lng, current_time):
    """Generate features for a single coordinate at specific time"""
    # Temporal features
    hour = current_time.hour
    day_of_week = current_time.weekday()  # Monday=0, Sunday=6
    month = current_time.month
    
    # Cluster prediction
    cluster = kmeans.predict([[lat, lng]])[0]
    
    # Get precomputed values
    crimes_per_hour = hourly_counts.get(hour, 0)
    crimes_per_weekday = daily_counts.get(day_of_week, 0)
    violent_this_month = monthly_violent.get(month, 0)
    
    # Distance from hotspot
    hotspot_dist = np.sqrt(
        (lat - hotspot_coords['lat'])**2 +
        (lng - hotspot_coords['lon'])**2
    )
    
    return [
        lat, lng, 
        hour, day_of_week, month,
        cluster,
        crimes_per_hour, crimes_per_weekday,
        hotspot_dist,
        violent_this_month
    ]

def predict_danger(features):
    """Predict danger probability for a single set of features"""
    scaled_features = scaler.transform([features])
    return model.predict_proba(scaled_features)[0][1]  # Probability of violent crime

def calculate_route_danger(route_path, start_time):
    """Calculate danger score for a route path"""
    total_points = len(route_path)
    if total_points == 0:
        return 0
    
    # Estimate time per coordinate (assuming constant speed)
    total_seconds = 3600  # Default 1 hour if duration not available
    if 'duration' in route_path[0]:  # If using actual duration from Google
        total_seconds = sum(step['duration']['value'] for step in route_path)
    
    time_increment = total_seconds / total_points
    current_time = start_time
    total_danger = 0
    
    for i, coord in enumerate(route_path):
        # Generate features for this point in time
        features = get_features(coord[0], coord[1], current_time)
        danger = predict_danger(features)
        total_danger += danger
        
        # Update time based on progression through route
        current_time += timedelta(seconds=time_increment)
    
    return total_danger / total_points  # Average danger probability

def get_routes(source_coords, dest_coords):
    """Main function to get routes with safety scores"""
    directions = gmaps.directions(
        origin={"lat": source_coords[0], "lng": source_coords[1]},
        destination={"lat": dest_coords[0], "lng": dest_coords[1]},
        alternatives=True
    )
    routes = []

    for i, route in enumerate(directions):
        # Decode polyline points
        path = polyline.decode(route['overview_polyline']['points'])
        
        # Get route metadata
        legs = route['legs'][0]
        distance = legs['distance']['text']
        duration = legs['duration']['text']
        
        # Estimate start time (could be passed as parameter)
        start_time = datetime.now()
        
        # Calculate danger score
        danger_score = calculate_route_danger(path, start_time)
        
        # Format steps for frontend
        steps = [{
            "instruction": step["html_instructions"],
            "distance": step["distance"]["text"],
            "location": step["end_location"]
        } for step in legs['steps']]

        routes.append({
            'id': i,
            'danger': round(float(danger_score) * 100, 2),  # Convert to percentage
            'distance': distance,
            'duration': duration,
            'coordinates': path,
            'steps': steps
        })

    # Sort routes by safety (ascending danger score)
    return sorted(routes, key=lambda x: x['danger'])
