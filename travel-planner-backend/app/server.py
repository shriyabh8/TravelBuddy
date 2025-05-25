import sys
import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from .agents.trip_planner_agent import TripPlannerAgent
from .agents.make_itinerary import make_itinerary
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
CORS(app, origins=["http://localhost:3001"])

trip_planner = TripPlannerAgent()

# Simple in-memory store (replace with Redis/db later)
trip_data_store = {}

@app.route('/')
def index():
    return jsonify({
        "status": "TravelBuddy API is running",
        "endpoints": ["/submit_trip_data (POST)", "/generate_itinerary (GET)"]
    })

def format(data):
    data = make_itinerary(data)
    def choose_one_flight_and_hotel():
        chosen_flight = random.choice(data['flight_depart']['Offers'])
        
        chosen_hotel = random.choice(data['hotel_data'])
        
        output = {}

        flight_data = ""
        flight_data += data['flight_depart']['Flight offer'].strip()
        flight_data += f"\nPrice: {chosen_flight['Price']}"
        flight_data += "\nSegments:"
        for segment in chosen_flight['Segments']:
            flight_data += f"\n  - {segment}"

        output['Flights'] = flight_data

        hotel_data = ""
        hotel_data += f"\nName: {chosen_hotel['name']}"
        hotel_data += f"\nPrice per night: ${chosen_hotel['price']}"
        hotel_data += f"\nDistance from airport: {chosen_hotel['Distance from Airport']:.2f} km"
        
        output['Hotels'] = hotel_data
        print(output)
        return output

    
    try:
        full_data = {
            "1": choose_one_flight_and_hotel(),
            "2": choose_one_flight_and_hotel(),
            "3": choose_one_flight_and_hotel()
        }
        return full_data
    except Exception as e:
        print(f"Error processing write data: {e}")

@app.route('/submit_trip_data', methods=['POST'])
def submit_trip_data():
    try:
        data = request.get_json()
        logger.info(f"Trip data received: {data}")

        # Validate input
        required = ['start_date', 'end_date', 'from', 'to', 'additionalInfo', 'people']
        if not all(field in data for field in required):
            return jsonify({"error": "Missing required fields"}), 400

        key = f"{data['to']}-{data['start_date']}"
        trip_data_store[key] = data

        logger.info(f"Stored trip under key: {key}")
        return jsonify({"message": "Trip data stored", "key": key})
    except Exception as e:
        logger.error(f"Error in /submit_trip_data: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate_itinerary/<key>', methods=['GET'])
def generate_itinerary(key):
    try:
        if not key or key not in trip_data_store:
            return jsonify({"error": "Missing or invalid key"}), 400

        data = format(trip_data_store)[key]
        logger.info(data)

        # Get dates from data - they should already be in YYYY-MM-DD format
        start_date = data['start_date']
        end_date = data['end_date']
        duration = (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days

        
        

        # Log the trip plan
        logger.info(f"Generated trip plan for {data['to']}")

        formatted = trip_planner.format_itinerary(trip)
        return jsonify(formatted)

    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    except Exception as e:
        logger.error(f"Error in /generate_itinerary: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)
