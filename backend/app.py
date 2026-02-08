from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import pandas as pd
import temp
import get_routes
import polyline
from twilio.rest import Client
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)
@app.route("/")
def home():
    return "TouristBuddy Backend is Running Successfully"


# Load credentials from .env
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
TO_WHATSAPP_NUMBER = os.getenv("TO_WHATSAPP_NUMBER")

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


# ========================
# CRIME LOCATIONS
# ========================
@app.route('/get-crime-locations', methods=['POST'])
def get_crime_locationss():

    filtered_df = temp.get_crime_locations()

    filtered_df['Time'] = filtered_df['Time'].apply(
        lambda t: t.strftime('%H:%M')
    )

    return jsonify({
        "status": "success",
        "data": filtered_df.to_dict(orient='records')
    })


# ========================
# COMMUNITY CENTERS
# ========================
@app.route('/get-community-centers', methods=["POST"])
def get_nearby_places():

    payload = request.get_json()

    user_lat = payload.get("lat")
    user_lng = payload.get("lng")

    radius = 3000

    if not user_lat or not user_lng:

        return jsonify({
            "status": "error",
            "message": "Missing coordinates"
        }), 400

    all_places = []

    place_types = ["hospital", "police"]

    for place_type in place_types:

        url = (
            "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            f"?location={user_lat},{user_lng}"
            f"&radius={radius}"
            f"&type={place_type}"
            f"&key={GOOGLE_MAPS_API_KEY}"
        )

        response = requests.get(url)

        results = response.json()

        if results.get("status") == "OK":

            for result in results.get("results", []):

                all_places.append({

                    "name": result.get("name"),

                    "type": place_type,

                    "lat": float(result["geometry"]["location"]["lat"]),

                    "lng": float(result["geometry"]["location"]["lng"]),

                    "address": result.get("vicinity"),

                    "rating": result.get("rating", "N/A")

                })

    return jsonify({
        "status": "success",
        "places": all_places
    })


# ========================
# SAFE PATHS
# ========================
@app.route('/get-safe-paths', methods=['POST'])
def get_safe_paths():

    data = request.json

    source_lat = data.get('source_lat')
    source_lng = data.get('source_lng')
    dest_lat = data.get('dest_lat')
    dest_lng = data.get('dest_lng')

    if None in [source_lat, source_lng, dest_lat, dest_lng]:

        return jsonify({
            "error": "Source and destination required"
        }), 400

    routes = get_routes.get_routes(
        (source_lat, source_lng),
        (dest_lat, dest_lng)
    )

    return jsonify({
        'routes': routes
    })


# ========================
# SOS MESSAGE
# ========================
@app.route('/send-sos-message', methods=["POST"])
def send_whatsapp_message():

    try:

        data = request.json

        userLatitude = data['lat']
        userLongitude = data['lng']
        username = data['username']

        loclink = f"https://www.google.com/maps?q={userLatitude},{userLongitude}"

        msg = (
            f"SOS Alert! Please help!\n\n"
            f"{username} is at this location:\n"
            f"{loclink}"
        )

        client = Client(
            TWILIO_ACCOUNT_SID,
            TWILIO_AUTH_TOKEN
        )

        message = client.messages.create(

            from_=TWILIO_WHATSAPP_NUMBER,

            body=msg,

            to=TO_WHATSAPP_NUMBER

        )

        print("SOS SENT:", message.sid)

        return jsonify({

            "status": "success",

            "sid": message.sid

        })

    except Exception as e:

        print("SOS ERROR:", str(e))

        return jsonify({

            "status": "error",

            "message": str(e)

        }), 500


# ========================
# MAIN
# ========================
if __name__ == '__main__':

    print("TouristBuddy backend running...")

    import os
    port = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port)
