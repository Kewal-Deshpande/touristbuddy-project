# safe_route_ml.py
import pandas as pd
import numpy as np
import folium
from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
import googlemaps
from dotenv import load_dotenv
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.cluster import KMeans
import joblib
from datetime import datetime

load_dotenv()

# Load and preprocess data
crime_df = pd.read_csv('pune_crime_data.csv')

# Feature Engineering
crime_df['DateTime'] = pd.to_datetime(crime_df['Date'] + ' ' + crime_df['Time'])
crime_df['Hour'] = crime_df['DateTime'].dt.hour
crime_df['DayOfWeek'] = crime_df['DateTime'].dt.dayofweek
crime_df['Month'] = crime_df['DateTime'].dt.month

# Cluster locations into 50 areas
coords = crime_df[['Latitude', 'Longitude']].values
kmeans = KMeans(n_clusters=50, random_state=42)
crime_df['AreaCluster'] = kmeans.fit_predict(coords)

# Prepare training data
cluster_stats = crime_df.groupby('AreaCluster').agg(
    TotalCrimes=('Crime Type', 'count'),
    CrimeTypeDistribution=('Crime Type', lambda x: x.value_counts().to_dict())
).reset_index()

# Feature Engineering for ML
def create_features(df):
    features = []
    for _, row in df.iterrows():
        cluster = row['AreaCluster']
        stats = cluster_stats[cluster_stats['AreaCluster'] == cluster].iloc[0]
        
        features.append({
            'Hour': row['Hour'],
            'DayOfWeek': row['DayOfWeek'],
            'Month': row['Month'],
            'TotalCrimes': stats['TotalCrimes'],
            'ViolentCrimes': sum(1 for k,v in stats['CrimeTypeDistribution'].items() 
                             if k in ['Murder', 'Rape', 'Robbery']),
            'Latitude': row['Latitude'],
            'Longitude': row['Longitude']
        })
    return pd.DataFrame(features)

X = create_features(crime_df)
y = crime_df.groupby('AreaCluster')['Crime Type'].transform('count').values

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Build pipeline
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['Hour', 'DayOfWeek', 'Month'])
    ])

model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
])

# Train model
model.fit(X_train, y_train)
joblib.dump(model, 'crime_model.pkl')
joblib.dump(kmeans, 'cluster_model.pkl')

# Flask App
app = Flask(__name__)
# ... [Keep previous Flask configuration] ...

# Load models
model = joblib.load('crime_model.pkl')
kmeans = joblib.load('cluster_model.pkl')

def predict_danger(lat, lng, current_time=None):
    """Predict danger score for a location"""
    if current_time is None:
        current_time = datetime.now()
    
    features = pd.DataFrame([{
        'Hour': current_time.hour,
        'DayOfWeek': current_time.weekday(),
        'Month': current_time.month,
        'TotalCrimes': 0,  # Will be replaced from cluster stats
        'ViolentCrimes': 0,
        'Latitude': lat,
        'Longitude': lng
    }])
    
    # Find cluster and add cluster features
    cluster = kmeans.predict([[lat, lng]])[0]
    cluster_data = cluster_stats[cluster_stats['AreaCluster'] == cluster].iloc[0]
    
    features['TotalCrimes'] = cluster_data['TotalCrimes']
    features['ViolentCrimes'] = sum(1 for k,v in cluster_data['CrimeTypeDistribution'].items() 
                               if k in ['Murder', 'Rape', 'Robbery'])
    
    return model.predict(features)[0]

def get_route_danger(route_coords):
    """Calculate danger score for a route using ML predictions"""
    current_time = datetime.now()
    total_danger = 0
    
    for coord in route_coords:
        danger = predict_danger(coord[0], coord[1], current_time)
        total_danger += danger
    
    return total_danger / len(route_coords)  # Average danger per point

# ... [Keep previous Flask routes] ...

if __name__ == '__main__':
    app.run(debug=True)