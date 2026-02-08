from flask import Flask, request, jsonify
import requests
from geopy.distance import geodesic
from flask_cors import CORS
import pandas as pd
import temp


app = Flask(__name__)
CORS(app)
GOOGLE_MAPS_API_KEY = "AIzaSyABXrzOdYntmVFt7vHZPMHEtAnvZLr7N-s"


@app.route('/get-safe-paths', methods = ['POST'])
def get_safe_paths():
    data = request.json
    source = data['source']
    destination = data['destination']
    print(source, destination)

    if not source or not destination:
        return jsonify({"error": "Source and destination are not present"}), 400
    
    routes = temp.get_routes(source, destination)   
    return jsonify({'routes': routes})

if __name__ == '__main__':
    app.run(debug=True)