import sys
import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from .agents.trip_planner_agent import TripPlannerAgent
from .agents.make_itinerary import make_itinerary
from .agents.chatbot import edit_itinerary
import random


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
# Configure CORS with additional options
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

trip_planner = TripPlannerAgent()

# Simple in-memory store (replace with Redis/db later)
trip_data_store = {}

@app.route('/')
def index():
    return jsonify({
        "status": "TravelBuddy API is running",
        "endpoints": ["/submit_trip_data (POST)", "/generate_itinerary (GET)"]
    })

@app.route('/submit_trip_data', methods=['POST'])
def submit_trip_data():
    try:
        data = request.get_json()
        logger.info(f"Trip data received: {data}")

        # Validate input
        required = ['start_date', 'end_date', 'from', 'to', 'additionalInfo', 'people']
        if not all(field in data for field in required):
            return jsonify({"error": "Missing required fields"}), 400
        # Use global keyword to modify the global variable
        global trip_data_store
        # Generate itinerary and store it with a key
        itinerary_data = make_itinerary(data)
        trip_data_store["here"] = itinerary_data
        
        return jsonify({"message": "Trip data stored"})
    except Exception as e:
        logger.error(f"Error in /submit_trip_data: {str(e)}")
        return jsonify({"error": str(e)}), 500
    

@app.route('/generate_itinerary/<itinerary_key>', methods=['GET'])
def generate_itinerary(itinerary_key):
    try:
        return jsonify(trip_data_store["here"][itinerary_key])
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    except Exception as e:
        logger.error(f"Error in /generate_itinerary: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/chatbot/<itinerary_key>', methods=['POST'])
def chatbot_edit(itinerary_key):
    print("this is before", trip_data_store["here"])
    trip_data_store["here"][itinerary_key]=json.loads(edit_itinerary(trip_data_store["here"][itinerary_key], json.dumps(request.get_json()), []))
    print("this is  after the edit", trip_data_store["here"])
    return jsonify({"message": "Chatbot response generated"})


if __name__ == '__main__':
    app.run(debug=True, port=5001)
