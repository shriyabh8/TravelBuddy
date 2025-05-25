import json
import logging
import google.generativeai as genai
from dotenv import load_dotenv
import requests

logger = logging.getLogger(__name__)
load_dotenv()
import os

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

genai.configure(api_key=api_key)


class GoalAgent:
    """
    Goal Understanding Agent that extracts structured travel preferences from user input.

    Uses Google Gemini API to parse user preferences while place and date are handled by selection menus.
    """

    def __init__(self):
        """
        Initialize the GoalAgent with Gemini API.
        """
        # Load environment variables
        # change this later
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        genai.configure(api_key=api_key)
        self.gemini = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")

        # Define response schemas
        self.response_schemas = [
            "budget",
            "accommodation",
            "dietary",
            "activities",
            "constraints",
            "city_codes"  # changed from "city codes" to "city_codes" (underscore preferred)
        ]

        # Update system prompt to include city_codes field
        self.system_prompt = """
                You are a travel preferences parser. The user will provide a sentence or paragraph describing their travel plans.
                Extract only the primary, major international airport codes (IATA 3-letter codes) closest to any city or region mentioned. Do not include regional, domestic, or secondary airports.
                Return your answer as a Python list of strings, for example: ["LHR"].
                Follow these rules:
                Only include airports that are the largest and most commonly used international gateways for the city or metro area mentioned.
                If the city has multiple major airports (e.g. New York), include all relevant primary ones: ["JFK", "EWR", "LGA"].
                If only one is dominant (e.g. London → LHR, not LGW or STN), return only that one.
                If the city is ambiguous or has no well-known airport, return an empty list: [].
                Examples:
                “I want to go to London.” → ["LHR"]
                “Let's fly to Paris!” → ["CDG"]
                “I’m headed to San Francisco.” → ["SFO"]
                “Planning a trip to New York.” → ["JFK", "EWR", "LGA"]
                “Vacation in Tokyo” → ["HND", "NRT"]
                “Visiting Dallas” → ["DFW"]
                “Going to Oakland” → ["OAK"]
                """

    def extract(self, user_input: str):
        response = self.gemini.generate_content(str(self.system_prompt) + str(user_input)).text
        response = response.strip().strip('`')
        airport_list = json.loads(response)

        # Get lat/lon for each airport code
        airport_coords = self.get_lat_lon_for_airports(airport_list)
        return airport_coords

    @staticmethod
    def get_lat_lon_for_airports(codes):
        coords = {}
        url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": "notWU49gJl5MUZs5Wij73gxQX0RCj9EI",
            "client_secret": "5WGFoGbZy57N1eUp",
        }
        response = requests.post(url, data=data)
        response.raise_for_status()
        token = response.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}
        url = "https://test.api.amadeus.com/v1/reference-data/locations"

        for code in codes:
            params = {
                "subType": "AIRPORT",
                "keyword": code
            }
            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                continue

            data = response.json()
            if data["data"]:
                # Usually the first result matches
                airport = data["data"][0]
                lat = float(airport["geoCode"]["latitude"])
                lon = float(airport["geoCode"]["longitude"])
                coords[code] = {"lat": lat, "lon": lon}
            else:
                print(f"No data found for {code}")
        return coords

if __name__ == "__main__":
    goal_agent = GoalAgent()

    # Example user input
    user_input = "Take me to San Diego for 3 days and show me the available activities."

    # Extract and normalize preferences
    goal_data = goal_agent.extract(user_input)

    data = json.dumps(goal_data, indent=2)
    # data contains the json data of the airport code + the latitude + longitude
    print(data)