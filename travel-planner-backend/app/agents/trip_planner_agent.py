from typing import Dict, List, Any, Optional
from datetime import datetime
from .goal_agent import GoalAgent
from .poi_agent import POIAgent
from .itinerary_agent import ItineraryAgent
import logging
from app.utils.api_wrappers import get_location_coordinates 
import json
from flask import Flask, request, jsonify

app = Flask(__name__, instance_relative_config=True)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d")
        return super().default(obj)

class TripPlannerAgent:
    def __init__(self):
        self.goal_agent = GoalAgent()
        self.poi_agent_activities = None
        self.poi_agent_food = None
        self.itinerary_agent = ItineraryAgent()

        self.mock_hotel = {
            "name": "The Ritz-Carlton San Francisco",
            "location": (37.7896, -122.4073),  # Coordinates for Nob Hill
            "rating": 5.0,
            "address": "600 Stockton St, San Francisco, CA 94108, USA",
            "amenities": [
                "Free WiFi", "24-hour front desk", "Restaurant", "Bar",
                "Spa", "Fitness center", "Indoor pool", "Airport shuttle",
                "Business center", "Meeting rooms", "Concierge service",
                "Luxury suites", "Butler service", "Valet parking",
                "Executive lounge", "Complimentary breakfast",
                "In-room dining", "Pet-friendly"
            ],
            "price": 550.00,
            "currency": "USD"
        }

    def plan_trip(self, user_input: str, destination: str, start_date: str, duration: int) -> Dict[str, Any]:
        preferences = self.goal_agent.extract(user_input)

        food_tags = [["amenity", "restaurant"], ["amenity", "cafe"], ["amenity", "bar"]]
        food_keys = {"restaurant", "cafe", "bar", "food", "fast_food", "pub", "bistro", "diner"}

        activity_tags = []
        for tag in preferences['osm_tags']:
            if tag[0] == "amenity" and tag[1] in food_keys:
                continue
            activity_tags.append(tag)
            if tag[0] == "building" and tag[1] in ["church", "mosque", "temple"]:
                activity_tags.extend([["building", "historical"], ["historic", "monument"]])
            elif tag[0] == "shop" and tag[1] in ["mall", "retail"]:
                activity_tags.extend([["building", "retail"], ["building", "shopping_centre"]])
            elif tag[0] == "leisure" and tag[1] in ["park", "sports_centre", "stadium"]:
                activity_tags.extend([["natural", "wood"], ["natural", "water"]])
            elif tag[0] == "tourism" and tag[1] == "attraction":
                activity_tags.extend([["leisure", "park"], ["natural", "peak"]])

        user_input_lower = user_input.lower()
        if "mall" in user_input_lower or "shopping" in user_input_lower:
            activity_tags.extend([["shop", "mall"], ["shop", "retail"], ["building", "retail"], ["building", "shopping_centre"]])
        if "architecture" in user_input_lower or "building" in user_input_lower:
            activity_tags.extend([["building", "cathedral"], ["building", "church"], ["building", "mosque"], ["building", "temple"],
                                  ["historic", "monument"], ["building", "palace"], ["building", "castle"]])
        if "park" in user_input_lower or "nature" in user_input_lower:
            activity_tags.extend([["leisure", "park"], ["natural", "wood"], ["natural", "water"], ["leisure", "garden"]])

        seen = set()
        activity_tags = [x for x in activity_tags if not (tuple(x) in seen or seen.add(tuple(x)))]
        self.poi_agent_activities = POIAgent(location=destination, osm_tags=activity_tags, budget=preferences.get("budget"))
        self.poi_agent_food = POIAgent(location=destination, osm_tags=food_tags, budget=preferences.get("budget"))

        activities_pois = self.poi_agent_activities.get_pois(max_results=20)
        food_pois = self.poi_agent_food.get_pois(max_results=20)
        hotel_info = self.mock_hotel
        start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")

        # import pdb; pdb.set_trace()
        itinerary = self.itinerary_agent.generate_itinerary(
            duration=duration,
            start_date=start_date_dt,
            activities_poi=activities_pois,
            food_poi=food_pois,
            hotel_info=hotel_info,
            user_tags=preferences['osm_tags']
        )
        return {
            "destination": destination,
            "start_date": start_date,
            "duration": duration,
            "preferences": preferences,
            "itinerary": itinerary
        }

    def get_trip_summary(self, trip_plan: Dict[str, Any]) -> str:
        summary = []
        summary.append(f"Trip Summary for {trip_plan['destination']}")
        summary.append(f"Duration: {trip_plan['duration']} days")
        summary.append(f"Start Date: {trip_plan['start_date']}")
        summary.append("\nPreferences:")

        preferences = trip_plan['preferences']
        for key, value in preferences.items():
            if value:
                summary.append(f"- {key.capitalize()}: {value}")

        summary.append("\nItinerary Overview:")
        summary.append(f"Total Activities: {trip_plan['itinerary']['total_activities']}")
        summary.append(f"Total Meals: {trip_plan['itinerary']['total_meals']}")

        for day in trip_plan['itinerary']['itinerary']:
            summary.append(f"\nDay {day['day']}: {day['date'].strftime('%A, %B %d')}")
            summary.append("\nActivities:")
            if day['activities']:
                for activity in day['activities']:
                    summary.append(f"- {activity['name']} ({activity['type']})")
                    summary.append(f"  Time: {activity['start_time']} to {activity['end_time']}")
                    summary.append(f"  Duration: {activity['duration']} minutes")
            else:
                summary.append("  No activities scheduled for this day")

            summary.append("\nMeals:")
            if day['meals']:
                for meal in day['meals']:
                    summary.append(f"- {meal['name']} ({meal['type']})")
                    summary.append(f"  Time: {meal['start_time']} to {meal['end_time']}")
                    summary.append(f"  Duration: {meal['duration']} minutes")
                    summary.append(f"  Rating: {meal['rating'] if meal['rating'] is not None else 'N/A'}★")
            else:
                summary.append("  No meals scheduled for this day")

        return "\n".join(summary)

def format_itinerary(trip_data):
    formatted_itinerary = {}
    
    # Helper function to extract website from tags
    def get_website(tags):
        website_tags = [tag[1] for tag in tags if tag[0] == 'website' or tag[0] == 'contact:website']
        return website_tags[0] if website_tags else None
    
    # Iterate through each day's activities and meals
    for day in trip_data['itinerary']['itinerary']:
        day_number = f"day_{day['day']}"
        formatted_itinerary[day_number] = {
            "activities": [],
            "meals": []
        }
        
        # Format activities
        for activity in day['activities']:
            website = get_website(activity.get('tags', []))
            formatted_activity = {
                "name": activity['name'],
                "price": activity.get('price', 'Free'),
                "duration": f"{activity['duration']} minutes",
                "website": website,
                "description": activity.get('description', ''),
                "amenities": activity.get('amenities', []),
                "rating": activity.get('rating'),
                "location": activity.get('location')
            }
            formatted_itinerary[day_number]["activities"].append(formatted_activity)
        
        # Format meals
        for meal in day['meals']:
            website = get_website(meal.get('tags', []))
            formatted_meal = {
                "name": meal['name'],
                "price": meal.get('price', 'Free'),
                "duration": f"{meal['duration']} minutes",
                "website": website,
                "description": meal.get('description', ''),
                "amenities": meal.get('amenities', []),
                "rating": meal.get('rating'),
                "location": meal.get('location')
            }
            formatted_itinerary[day_number]["meals"].append(formatted_meal)
    
    return formatted_itinerary

#@app.route('/plan_trip', methods=['POST'])
def main():
    planner = TripPlannerAgent()
    
    # Example trip planning
    trip = planner.plan_trip(
        user_input="I want to go to SFO and explore the city.",
        destination="San Francisco, CA",
        start_date="2025-05-25",
        duration=3
    )

    trip = format_itinerary(trip)

    json_trip = json.dumps(trip, cls=DateTimeEncoder)
    print(json_trip)

if __name__ == '__main__':
    main()
