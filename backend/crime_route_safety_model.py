import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from datetime import datetime, timedelta
from scipy.spatial import cKDTree
import pickle

class CrimeRouteSafetyModel:
    def __init__(self):
        # Crime type weights - can be adjusted based on severity
        self.crime_weights = {
            'Theft': 0.5,
            'Robbery': 0.8,
            'Assault': 0.9,
            'Murder': 1.0,
            'Harassment': 0.6,
            'Vehicle theft': 0.7,
            'Burglary': 0.7,
            'Drug related': 0.6,
            'Fraud': 0.4,
            # Add more crime types with weights as needed
            'Other': 0.5  # Default for unclassified crimes
        }
        
        # Time-based weight factors (higher during night)
        self.time_weights = {
            'morning': 0.6,     # 6am-12pm
            'afternoon': 0.4,   # 12pm-6pm
            'evening': 0.7,     # 6pm-10pm
            'night': 1.0        # 10pm-6am
        }
        
        self.model = None
        self.crime_kdtree = None
        self.crime_data = None
        self.distance_threshold = 0.005  # Approximately 500m in lat/long units
        
    def _preprocess_date_time(self, df):
        """Convert Date and Time columns to datetime objects and extract features"""
        # Combine date and time columns
        if isinstance(df['Date'].iloc[0], str) and isinstance(df['Time'].iloc[0], str):
            df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], errors='coerce')
        else:
            df['DateTime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'].astype(str), errors='coerce')
            
        # Extract time-based features
        df['Hour'] = df['DateTime'].dt.hour
        df['DayOfWeek'] = df['DateTime'].dt.dayofweek
        df['Month'] = df['DateTime'].dt.month
        
        # Create time period feature
        conditions = [
            (df['Hour'] >= 6) & (df['Hour'] < 12),
            (df['Hour'] >= 12) & (df['Hour'] < 18),
            (df['Hour'] >= 18) & (df['Hour'] < 22),
            (df['Hour'] >= 22) | (df['Hour'] < 6)
        ]
        choices = ['morning', 'afternoon', 'evening', 'night']
        df['TimePeriod'] = np.select(conditions, choices, default='other')
        
        return df
    
    def train(self, crime_data):
        """Train the danger prediction model using crime data"""
        # Copy the dataframe to avoid modifying the original
        df = crime_data.copy()
        
        # Preprocess date and time
        df = self._preprocess_date_time(df)
        
        # Fill NaN values in Crime Type with 'Other'
        df['Crime Type'] = df['Crime Type'].fillna('Other')
        
        # Assign weights to crime types
        df['CrimeWeight'] = df['Crime Type'].apply(
            lambda x: self.crime_weights.get(x, self.crime_weights['Other'])
        )
        
        # Assign weights to time periods
        df['TimeWeight'] = df['TimePeriod'].apply(
            lambda x: self.time_weights.get(x, self.time_weights['morning'])
        )
        
        # Calculate danger score for each crime (could be refined further)
        df['DangerScore'] = df['CrimeWeight'] * df['TimeWeight']
        
        # Features for the model
        features = ['Latitude', 'Longitude', 'Hour', 'DayOfWeek', 'Month']
        categorical_features = ['TimePeriod']
        
        # Create preprocessing pipeline
        preprocessor = ColumnTransformer(
            transformers=[
                ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
            ],
            remainder='passthrough'
        )
        
        # Create and train the model
        self.model = Pipeline([
            ('preprocessor', preprocessor),
            ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
        ])
        
        X = df[features + categorical_features]
        y = df['DangerScore']
        
        self.model.fit(X, y)
        
        # Create KDTree for efficient spatial queries
        self.crime_kdtree = cKDTree(df[['Latitude', 'Longitude']].values)
        self.crime_data = df
        
        return self
    
    def save_model(self, filepath='crime_safety_model.pkl'):
        """Save the trained model to a file"""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'crime_data': self.crime_data,
                'crime_weights': self.crime_weights,
                'time_weights': self.time_weights
            }, f)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath='crime_safety_model.pkl'):
        """Load a trained model from a file"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.crime_data = data['crime_data']
            self.crime_weights = data['crime_weights']
            self.time_weights = data['time_weights']
            
            # Recreate KDTree
            self.crime_kdtree = cKDTree(self.crime_data[['Latitude', 'Longitude']].values)
        print(f"Model loaded from {filepath}")
        return self
    
    def get_nearby_crimes(self, lat, lon, current_time=None, hours_window=2):
        """
        Get crimes near a specific point that occurred within a time window
        relative to the current time
        """
        if current_time is None:
            current_time = datetime.now()
        elif isinstance(current_time, str):
            # Try different time formats
            time_formats = [
                '%Y-%m-%d %H:%M:%S',  # Format with seconds
                '%Y-%m-%d %H:%M',     # Format without seconds
                '%m/%d/%Y %H:%M:%S',  # Alternative format
                '%m/%d/%Y %H:%M'      # Alternative format without seconds
            ]
            
            for time_format in time_formats:
                try:
                    current_time = datetime.strptime(current_time, time_format)
                    break
                except ValueError:
                    continue
            else:
                # If none of the formats match, raise a more helpful error
                raise ValueError(f"Unable to parse time string '{current_time}'. Please use format 'YYYY-MM-DD HH:MM' or 'YYYY-MM-DD HH:MM:SS'")
            
        # Find crimes within spatial threshold
        point = np.array([[lat, lon]])
        indices = self.crime_kdtree.query_ball_point(point, self.distance_threshold)[0]
        
        if not indices:
            return pd.DataFrame(columns=self.crime_data.columns)
            
        nearby_crimes = self.crime_data.iloc[indices].copy()
        
        # Filter by time window (same hour of day +/- hours_window)
        current_hour = current_time.hour
        
        # Create hour range considering day wraparound
        hour_min = (current_hour - hours_window) % 24
        hour_max = (current_hour + hours_window) % 24
        
        if hour_min < hour_max:
            time_filtered = nearby_crimes[(nearby_crimes['Hour'] >= hour_min) & 
                                        (nearby_crimes['Hour'] <= hour_max)]
        else:
            # Handle wraparound (e.g., 23:00 +/- 2 hours spans from 21:00 to 01:00)
            time_filtered = nearby_crimes[(nearby_crimes['Hour'] >= hour_min) | 
                                        (nearby_crimes['Hour'] <= hour_max)]
        
        return time_filtered
    
    # Update the predict_point_danger method in the CrimeRouteSafetyModel class

    def predict_point_danger(self, lat, lon, current_time=None):
        """Predict danger score for a specific point"""
        if current_time is None:
            current_time = datetime.now()
        elif isinstance(current_time, str):
            # Try different time formats
            time_formats = [
                '%Y-%m-%d %H:%M:%S',  # Format with seconds
                '%Y-%m-%d %H:%M',     # Format without seconds
                '%m/%d/%Y %H:%M:%S',  # Alternative format
                '%m/%d/%Y %H:%M'      # Alternative format without seconds
            ]
            
            for time_format in time_formats:
                try:
                    current_time = datetime.strptime(current_time, time_format)
                    break
                except ValueError:
                    continue
            else:
                # If none of the formats match, raise a more helpful error
                raise ValueError(f"Unable to parse time string '{current_time}'. Please use format 'YYYY-MM-DD HH:MM' or 'YYYY-MM-DD HH:MM:SS'")
            
        # Extract time features
        hour = current_time.hour
        day_of_week = current_time.weekday()
        month = current_time.month
        
        # Determine time period
        if 6 <= hour < 12:
            time_period = 'morning'
        elif 12 <= hour < 18:
            time_period = 'afternoon'
        elif 18 <= hour < 22:
            time_period = 'evening'
        else:
            time_period = 'night'
            
        # Create feature vector
        X = pd.DataFrame({
            'Latitude': [lat],
            'Longitude': [lon],
            'Hour': [hour],
            'DayOfWeek': [day_of_week],
            'Month': [month],
            'TimePeriod': [time_period]
        })
        
        # Make prediction
        danger_score = self.model.predict(X)[0]
        
        # Enhance with nearby crime influence
        nearby_crimes = self.get_nearby_crimes(lat, lon, current_time)
        nearby_influence = 0
        
        if not nearby_crimes.empty:
            # Weight by proximity and crime type
            for _, crime in nearby_crimes.iterrows():
                # Calculate distance
                dist = np.sqrt((crime['Latitude'] - lat)**2 + (crime['Longitude'] - lon)**2)
                proximity_factor = max(0, 1 - (dist / self.distance_threshold))
                
                # Get crime type weight
                crime_weight = self.crime_weights.get(
                    crime['Crime Type'], self.crime_weights['Other']
                )
                
                # Get time period weight
                time_weight = self.time_weights.get(crime['TimePeriod'], 0.5)
                
                # Add weighted influence
                nearby_influence += proximity_factor * crime_weight * time_weight
                
            # Normalize by number of crimes
            nearby_influence = nearby_influence / len(nearby_crimes) * 3  # Scaling factor
        
        # Combine model prediction with nearby crime influence
        final_danger = 0.7 * danger_score + 0.3 * nearby_influence
        
        return min(final_danger, 1.0)  # Cap at 1.0
    
    def evaluate_route(self, route_coordinates, current_time=None):
        """Calculate danger score for an entire route based on points along it"""
        if not route_coordinates:
            return 0.0
            
        # Get danger score for each point in the route
        danger_scores = []
        
        for lat, lon in route_coordinates:
            point_danger = self.predict_point_danger(lat, lon, current_time)
            danger_scores.append(point_danger)
            
        # Calculate average danger, giving more weight to highest danger points
        if danger_scores:
            danger_scores.sort(reverse=True)
            weighted_scores = []
            
            # Give more weight to the most dangerous segments
            for i, score in enumerate(danger_scores):
                weight = 1.0 / (i + 1)  # Hyperbolic weighting
                weighted_scores.append(score * weight)
                
            total_weight = sum([1.0 / (i + 1) for i in range(len(danger_scores))])
            avg_danger = sum(weighted_scores) / total_weight
            
            return min(avg_danger, 1.0)  # Cap at 1.0
        
        return 0.0

# Function to get route danger - to be used with the get_routes function
def get_route_danger(path, model=None, current_time=None):
    """
    Calculate danger index for a route using the trained model
    
    Args:
        path: List of (lat, lon) coordinates defining the route
        model: Trained CrimeRouteSafetyModel instance
        current_time: Current time for time-based analysis
        
    Returns:
        Danger score from 0-1 (higher is more dangerous)
    """
    if model is None:
        # Try to load a pre-trained model
        try:
            model = CrimeRouteSafetyModel().load_model()
        except FileNotFoundError:
            print("No trained model found. Please train the model first.")
            return 0.5  # Default medium danger
    
    return model.evaluate_route(path, current_time)

# Usage example
def train_and_save_model(crime_data_file):
    # Load crime data
    crime_data = pd.read_csv(crime_data_file)
    
    # Train the model
    model = CrimeRouteSafetyModel().train(crime_data)
    
    # Save the model for future use
    model.save_model()
    
    return model

# Example of how to use the model with the get_routes function
def example_usage():
    # Load the saved model
    model = CrimeRouteSafetyModel().load_model()
    
    # Define start and end points
    start = "18.5204, 73.8567"  # Example coordinates in Pune
    end = "18.5502, 73.8567"    # Example destination
    
    # Set current time (or use None for current time)
    current_time = datetime.now()
    
    # Get and sort routes based on danger
    routes = get_routes(start, end)
    
    # The routes are already sorted by danger in get_routes
    print(f"Found {len(routes)} routes. Showing from safest to most dangerous:")
    
    for i, route in enumerate(routes):
        print(f"\nRoute {i+1}:")
        print(f"Danger Score: {route['danger']:.2f} (lower is safer)")
        print(f"Distance: {route['distance']}")
        print(f"Duration: {route['duration']}")
        print("Steps:")
        for step in route['steps'][:3]:  # Show first 3 steps
            print(f"- {step['instruction']}: {step['distance']}")
        if len(route['steps']) > 3:
            print(f"- ...and {len(route['steps']) - 3} more steps")

# For the get_routes function to work properly:
# 1. Make sure to have the 'googlemaps' and 'polyline' packages installed
# 2. Set your Google Maps API key
# 3. Initialize the gmaps client before calling get_routes
#
# Example:
# import googlemaps
# import polyline
# gmaps = googlemaps.Client(key='YOUR_API_KEY_HERE')

if __name__ == "__main__":
    # Example of training and using the model
    try:
        # Try to load existing model
        model = CrimeRouteSafetyModel().load_model()
        print("Loaded existing model")
    except:
        # Train new model if no saved model exists
        print("Training new model...")
        model = train_and_save_model('/content/crime_data_pune.csv')
        print("Model training complete")
    
    # Now the get_route_danger function can be used with the trained model
    print("Model ready for route danger evaluation")