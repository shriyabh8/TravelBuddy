from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from .goal_agent import GoalAgent
from .poi_agent import POIAgent
from .itinerary_agent import ItineraryAgent
import logging

logger = logging.getLogger(__name__)

class TripPlannerAgent:
    def __init__(self):
        self.goal_agent = GoalAgent()
        self.poi_agent_activities = None
        self.poi_agent_food = None
        self.itinerary_agent = ItineraryAgent()

        self.mock_hotel = {
            "name": "The Park Hyderabad",
            "location": (17.3850, 78.4867),
            "rating": 4.8,
            "address": "1-3-1209, Road No. 1, Banjara Hills, Hyderabad, Telangana 500034, India",
            "amenities": [
                "Free WiFi", "24-hour front desk", "Restaurant", "Bar",
                "Spa", "Fitness center", "Swimming pool", "Airport shuttle"
            ],
            "price": 4500.00,
            "currency": "INR"
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
        print(f"Activities POI count: {len(activities_pois)}")
        print(f"Food POI count: {len(food_pois)}")
        hotel_info = self.mock_hotel
        start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")

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
        summary.append(f"Total Travel Time: {trip_plan['itinerary']['total_travel_time']} minutes")

        for day in trip_plan['itinerary']['itinerary']:
            summary.append(f"\nDay {day['day']}: {day['date'].strftime('%A, %B %d')}")
            summary.append("\nActivities:")
            if day['activities']:
                for activity in day['activities']:
                    summary.append(f"- {activity.name} ({activity.type})")
                    summary.append(f"  Time: {activity.start_time} to {activity.end_time}")
                    summary.append(f"  Duration: {activity.duration} minutes")
            else:
                summary.append("  No activities scheduled for this day")

            summary.append("\nMeals:")
            if day['meals']:
                for meal in day['meals']:
                    summary.append(f"- {meal.name} ({meal.type})")
                    summary.append(f"  Time: {meal.start_time} to {meal.end_time}")
                    summary.append(f"  Duration: {meal.duration} minutes")
                    summary.append(f"  Rating: {meal.rating if meal.rating is not None else 'N/A'}★")
            else:
                summary.append("  No meals scheduled for this day")

        return "\n".join(summary)



if __name__ == "__main__":
    # Example usage
    planner = TripPlannerAgent()
    
    # Example trip planning
    trip = planner.plan_trip(
        user_input="I want to visit historical places and shopping malls in Hyderabad",
        destination="Hyderabad",
        start_date="2025-05-25",
        duration=3
    )
    
    # Display the trip summary

    print(planner.get_trip_summary(trip))
