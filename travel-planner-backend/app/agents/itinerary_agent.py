from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from math import radians, cos, sin, sqrt, atan2, asin
import random
import logging
from app.utils.api_wrappers import fetch_places, get_location_coordinates
from app.agents.poi_agent import POI

logger = logging.getLogger(__name__)

class ItineraryAgent:
    def __init__(self):
        self.day_start_hour = 9
        self.day_end_hour = 21
        self.buffer_time = 30
        self.max_activities_per_day = 5
        self.default_walking_speed = 5.0  # km/h
        self.default_driving_speed = 40.0  # km/h

    def generate_itinerary(self, duration: int, start_date: datetime, activities_poi: List[POI], food_poi: List[POI], hotel_info: Dict[str, Any], user_tags: List[List[str]] = None) -> Dict[str, Any]:
        hotel_location = hotel_info['location']
        activities = self._schedule_activities(activities_poi, hotel_location, duration, user_tags)
        print("Activities:", activities )
        meals = self._schedule_meals(food_poi, hotel_location, duration)
        print("Meals:", meals)
        
        itinerary = []
        for day in range(duration):
            daily_activities = activities[day]
            daily_meals = meals[day]
            
            # Calculate daily summary
            daily_summary = {
                'total_activities': len(daily_activities),
                'total_meals': len(daily_meals),
                'total_travel_time': 0,  # We'll calculate this later
                'total_activity_time': sum(item.duration for item in daily_activities),
                'total_meal_time': sum(item.duration for item in daily_meals)
            }
            
            # Create daily itinerary
            daily_itinerary = {
                'day': day + 1,
                'date': start_date + timedelta(days=day),
                'hotel': hotel_info,
                'activities': daily_activities,
                'meals': daily_meals,
                'daily_summary': daily_summary
            }
            
            # Calculate travel times between activities
            for i in range(len(daily_activities) - 1):
                current = daily_activities[i]
                next_activity = daily_activities[i + 1]
                travel_time = self._estimate_travel_time(current.location, next_activity.location)
                current['time_to_next'] = travel_time
                next_activity['gap_until_next'] = 10 + travel_time
                daily_summary['total_travel_time'] += travel_time
            
            # Calculate travel times between meals
            for i in range(len(daily_meals) - 1):
                current = daily_meals[i]
                next_meal = daily_meals[i + 1]
                travel_time = self._estimate_travel_time(current.location, next_meal.location)
                current['time_to_next'] = travel_time
                next_meal['gap_until_next'] = 10 + travel_time
                daily_summary['total_travel_time'] += travel_time
            
            itinerary.append(daily_itinerary)
        
        # Calculate overall summary
        total_activities = sum(day['daily_summary']['total_activities'] for day in itinerary)
        total_meals = sum(day['daily_summary']['total_meals'] for day in itinerary)
        total_travel_time = sum(day['daily_summary']['total_travel_time'] for day in itinerary)
        total_activity_time = sum(day['daily_summary']['total_activity_time'] for day in itinerary)
        total_meal_time = sum(day['daily_summary']['total_meal_time'] for day in itinerary)
        
        return {
            'itinerary': itinerary,
            'summary': f'Your {duration}-day itinerary has been generated with optimized travel times and well-distributed timing.',
            'total_activities': total_activities,
            'total_meals': total_meals,
            'total_travel_time': total_travel_time,
            'total_activity_time': total_activity_time,
            'total_meal_time': total_meal_time
        }

    def _haversine_distance(self, loc1: Tuple[float, float], loc2: Tuple[float, float]) -> float:
        """Calculate the distance between two locations in kilometers using the Haversine formula."""
        from decimal import Decimal
        
        # Convert coordinates to float if they're Decimal
        lat1, lon1 = (float(loc1[0]), float(loc1[1])) if isinstance(loc1[0], Decimal) else loc1
        lat2, lon2 = (float(loc2[0]), float(loc2[1])) if isinstance(loc2[0], Decimal) else loc2
        
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Earth radius in kilometers
        return c * r

    def _choose_mode(self, from_location: Tuple[float, float], to_location: Tuple[float, float]) -> str:
        distance_km = self._haversine_distance(from_location, to_location)
        return "foot-walking" if distance_km < 2.0 else "driving-car"

    def _estimate_travel_time(self, from_location: Tuple[float, float], to_location: Tuple[float, float]) -> int:
        """Estimate travel time between two points using average speeds."""
        distance_km = self._haversine_distance(from_location, to_location)
        mode = self._choose_mode(from_location, to_location)
        
        if mode == "foot-walking":
            speed_kmph = self.default_walking_speed
        else:
            speed_kmph = self.default_driving_speed
            
        travel_time_minutes = (distance_km / speed_kmph) * 60
        return int(travel_time_minutes)

    def _calculate_duration(self, poi: POI) -> int:
        """Calculate the duration for visiting a POI based on its type and popularity."""
        base_durations = {
            "museum": 120,
            "attraction": 90,
            "shopping": 90,
            "park": 120,
            "architecture": 90,
            "entertainment": 120,
            "culture": 120,
            "sports": 90,
            "nature": 120,
            "adventure": 120
        }
        poi_type = poi.type.lower()
        base_duration = base_durations.get(poi_type, 90)
        # Use theme_score as a proxy for popularity
        popularity = poi.theme_score
        return int(base_duration * (1 + 0.2 * (popularity - 0.5)))

    def _schedule_activities(self, pois: List[POI], hotel_location: Tuple[float, float], days: int, user_tags: List[List[str]]) -> List[List[Dict[str, Any]]]:
        """
        Schedule non-food activities with detailed timing and travel information.
        
        Args:
            pois: List of points of interest (POI objects)
            hotel_location: Location of the hotel
            days: Number of days for the trip
            user_tags: List of OSM tags from user preferences
            
        Returns:
            List of daily activity schedules with detailed information
        """
        daily_activities = []
        
        # Filter POIs based on user tags
        relevant_pois = []
        for poi in pois:
            # Skip food-related POIs
            if poi.type.lower() in ['restaurant', 'cafe', 'bar', 'food', 'fast_food', 'pub', 'bistro', 'diner']:
                continue
            
            # Check if POI matches any user tags
            poi_tags = set([tuple(tag) for tag in poi.tags])
            user_tag_set = set([tuple(tag) for tag in user_tags])
            
            if poi_tags.intersection(user_tag_set):
                relevant_pois.append(poi)
        
        # If no relevant POIs found, use all non-food POIs
        if not relevant_pois:
            relevant_pois = [poi for poi in pois if poi.type.lower() not in 
                           ['restaurant', 'cafe', 'bar', 'food', 'fast_food', 'pub', 'bistro', 'diner']]
        
        # Sort POIs by relevance score
        relevant_pois = sorted(relevant_pois, key=lambda p: p.relevance_score, reverse=True)
        
        # Track used POIs across days
        used_pois = set()
        
        for day in range(days):
            schedule = []
            current_time = self.day_start_hour * 60  # Start at 9:00 AM
            activities_count = 0
            last_location = hotel_location
            
            # Try to schedule at least one activity per day
            for poi in relevant_pois:
                if poi.osm_id in used_pois:
                    continue
                
                duration = self._calculate_duration(poi)
                travel_time = self._estimate_travel_time(last_location, poi.location)
                start_time = current_time + travel_time
                end_time = start_time + duration
                
                # Skip if activity would end too late
                if end_time > self.day_end_hour * 60:
                    continue
                
                # Create activity dictionary
                activity = {
                    "name": poi.name,
                    "description": poi.description,
                    "location": poi.location,
                    "type": poi.type,
                    "tags": poi.tags,
                    "osm_id": poi.osm_id,
                    "osm_type": poi.osm_type,
                    "relevance_score": poi.relevance_score,
                    "theme_score": poi.theme_score,
                    "tag_score": poi.tag_score,
                    "matched_theme": poi.matched_theme,
                    "start_time": start_time // 60,
                    "end_time": end_time // 60,
                    "duration": duration,
                    "travel_time": travel_time,
                    "time_to_next": 0,  # Will be updated later
                    "distance_from_last": self._haversine_distance(last_location, poi.location),
                    "distance_to_next": 0,  # Will be updated later
                    "gap_until_next": 10 + travel_time
                }
                
                schedule.append(activity)
                current_time = end_time + self.buffer_time
                last_location = poi.location
                activities_count += 1
                used_pois.add(poi.osm_id)
                
                # Stop if we've reached max activities for the day
                if activities_count >= self.max_activities_per_day:
                    break
            
            # If no activities were scheduled, try to find any available POI
            if not schedule:
                for poi in pois:
                    if poi.osm_id in used_pois or poi.type.lower() in ['restaurant', 'cafe', 'bar', 'food', 'fast_food', 'pub', 'bistro', 'diner']:
                        continue
                        
                    duration = self._calculate_duration(poi)
                    travel_time = self._estimate_travel_time(last_location, poi.location)
                    start_time = current_time + travel_time
                    end_time = start_time + duration
                    
                    # Skip if activity would end too late
                    if end_time > self.day_end_hour * 60:
                        continue
                    
                    # Create activity dictionary
                    activity = {
                        "name": poi.name,
                        "description": poi.description,
                        "location": poi.location,
                        "type": poi.type,
                        "tags": poi.tags,
                        "osm_id": poi.osm_id,
                        "osm_type": poi.osm_type,
                        "relevance_score": poi.relevance_score,
                        "theme_score": poi.theme_score,
                        "tag_score": poi.tag_score,
                        "matched_theme": poi.matched_theme,
                        "start_time": start_time // 60,
                        "end_time": end_time // 60,
                        "duration": duration,
                        "travel_time": travel_time,
                        "time_to_next": 0,
                        "distance_from_last": self._haversine_distance(last_location, poi.location),
                        "distance_to_next": 0,
                        "gap_until_next": 10 + travel_time
                    }
                    
                    schedule.append(activity)
                    current_time = end_time + self.buffer_time
                    last_location = poi.location
                    activities_count += 1
                    used_pois.add(poi.osm_id)
                    break
            
            daily_activities.append(schedule)
        
        return daily_activities
        
        # Sort each group by relevance score
        for poi_type in poi_groups:
            poi_groups[poi_type] = sorted(poi_groups[poi_type], key=lambda p: p.relevance_score, reverse=True)
        
        # Track used POIs across days by osm_id
        used_pois = set()

        for day in range(days):
            schedule = []
            current_time = self.day_start_hour * 60  # Start at 9:00 AM
            activities_count = 0
            last_location = hotel_location
            scheduled_meals = {8 * 60, 13 * 60, 19 * 60}  # Avoid meal hours

            # Try different POI types in order of preference
            activity_types = [
                "park", "museum", "attraction", "shopping",
                "architecture", "entertainment", "culture",
                "sports", "nature", "adventure"
            ]
            
            for poi_type in activity_types:
                if poi_type not in poi_groups or not poi_groups[poi_type]:
                    continue

                # Get available POIs of this type that haven't been used
                available_pois = [p for p in poi_groups[poi_type] if p.osm_id not in used_pois]
                if not available_pois:
                    continue

                # Select the most relevant available POI
                poi = available_pois[0]
                duration = self._calculate_duration(poi)
                travel_time = self._estimate_travel_time(last_location, poi.location)
                start_time = current_time + travel_time
                end_time = start_time + duration

                # Skip if activity would end too late
                if end_time > self.day_end_hour * 60:
                    continue

                # Calculate time to next activity if it exists
                next_poi = None
                for next_type in activity_types:
                    if next_type != poi_type and next_type in poi_groups:
                        next_poi = poi_groups[next_type][0] if poi_groups[next_type] else None
                        break
                time_to_next = self._estimate_travel_time(poi.location, next_poi.location) if next_poi else 0

                # Create activity dictionary
                activity = {
                    "name": poi.name,
                    "description": poi.description,
                    "location": poi.location,
                    "type": poi.type,
                    "tags": poi.tags,
                    "osm_id": poi.osm_id,
                    "osm_type": poi.osm_type,
                    "relevance_score": poi.relevance_score,
                    "theme_score": poi.theme_score,
                    "tag_score": poi.tag_score,
                    "matched_theme": poi.matched_theme,
                    "start_time": start_time // 60,
                    "end_time": end_time // 60,
                    "duration": duration,
                    "travel_time": travel_time,
                    "time_to_next": time_to_next,
                    "distance_from_last": self._haversine_distance(last_location, poi.location),
                    "distance_to_next": self._haversine_distance(poi.location, next_poi.location) if next_poi else 0,
                    "gap_until_next": 10 + travel_time
                }
                
                schedule.append(activity)
                current_time = end_time + self.buffer_time
                last_location = poi.location
                activities_count += 1
                used_pois.add(poi.osm_id)

                # Remove used POI from its group
                poi_groups[poi_type].remove(poi)

                # Stop if we've reached max activities for the day
                if activities_count >= self.max_activities_per_day:
                    break

            daily_activities.append(schedule)

        return daily_activities
        
        # Group POIs by type and sort each group
        poi_groups = {}
        for poi in pois:
            poi_type = poi.type.lower()
            if poi_type not in poi_groups:
                poi_groups[poi_type] = []
            poi_groups[poi_type].append(poi)
        
        # Sort each group by relevance score
        for poi_type in poi_groups:
            poi_groups[poi_type] = sorted(poi_groups[poi_type], key=lambda p: p.relevance_score, reverse=True)
        
        # Track used POIs across days by osm_id
        used_pois = set()

        for day in range(days):
            schedule = []
            current_time = self.day_start_hour * 60  # Start at 9:00 AM
            activities_count = 0
            last_location = hotel_location
            scheduled_meals = {8 * 60, 13 * 60, 19 * 60}  # Avoid meal hours

            # Try different POI types in order of preference
            activity_types = [
                "park", "museum", "attraction", "shopping",
                "architecture", "entertainment", "culture",
                "sports", "nature", "adventure"
            ]
            
            for poi_type in activity_types:
                if poi_type not in poi_groups or not poi_groups[poi_type]:
                    continue

                # Get available POIs of this type that haven't been used
                available_pois = [p for p in poi_groups[poi_type] if p.osm_id not in used_pois]
                if not available_pois:
                    continue

                # Select the most relevant available POI
                poi = available_pois[0]
                duration = self._calculate_duration(poi)
                travel_time = self._estimate_travel_time(last_location, poi.location)
                start_time = current_time + travel_time
                end_time = start_time + duration

                # Skip if activity would end too late
                if end_time > self.day_end_hour * 60:
                    continue

                # Calculate time to next activity if it exists
                next_poi = None
                for next_type in activity_types:
                    if next_type != poi_type and next_type in poi_groups:
                        next_poi = poi_groups[next_type][0] if poi_groups[next_type] else None
                        break
                time_to_next = self._estimate_travel_time(poi.location, next_poi.location) if next_poi else 0

                # Create a new POI object with scheduled information
                activity_info = POI(
                    name=poi.name,
                    description=poi.description,
                    location=poi.location,
                    type=poi.type,
                    tags=poi.tags,
                    osm_id=poi.osm_id,
                    osm_type=poi.osm_type,
                    relevance_score=poi.relevance_score,
                    theme_score=poi.theme_score,
                    tag_score=poi.tag_score,
                    matched_theme=poi.matched_theme,
                    start_time=start_time // 60,
                    end_time=end_time // 60,
                    duration=duration,
                    travel_time=travel_time,
                    time_to_next=time_to_next,
                    distance_from_last=self._haversine_distance(last_location, poi.location),
                    distance_to_next=self._haversine_distance(poi.location, next_poi.location) if next_poi else 0,
                    gap_until_next=10 + travel_time  # 10 minutes buffer plus travel time
                )
                
                schedule.append(activity_info)
                current_time = end_time + self.buffer_time
                last_location = poi.location
                activities_count += 1
                used_pois.add(poi.osm_id)

                # Remove used POI from its group
                poi_groups[poi_type].remove(poi)

                # Stop if we've reached max activities for the day
                if activities_count >= self.max_activities_per_day:
                    break

            daily_activities.append(schedule)

        return daily_activities

    def _schedule_meals(self, restaurants: List[POI], hotel_location: Tuple[float, float], days: int) -> List[List[Dict[str, Any]]]:
        """
        Schedule meals with detailed timing information.
        
        Args:
            restaurants: List of restaurant POIs
            hotel_location: Location of the hotel
            days: Number of days for the trip
            
        Returns:
            List of daily meal schedules with detailed information
        """
        meal_times = {
            "breakfast": 8 * 60,
            "lunch": 13 * 60,
            "dinner": 19 * 60
        }
        brunch_time = 11 * 60  # 11:00 AM for brunch
        daily_meals = []  # Initialize the list here
        
        for day in range(days):
            day_meals = []
            
            # Separate brunch and other meals
            brunch_restaurants = [r for r in restaurants if any(tag[1] == "brunch" for tag in r.tags)]
            other_restaurants = [r for r in restaurants if not any(tag[1] == "brunch" for tag in r.tags)]
            
            # If we have brunch options, use brunch instead of breakfast
            if brunch_restaurants:
                # Select a brunch restaurant
                brunch_restaurant = random.choice(brunch_restaurants)
                brunch_restaurants.remove(brunch_restaurant)
                
                # Create brunch info
                brunch_info = POI(
                    name=brunch_restaurant.name,
                    description=brunch_restaurant.description,
                    location=brunch_restaurant.location,
                    type=brunch_restaurant.type,
                    tags=brunch_restaurant.tags,
                    osm_id=brunch_restaurant.osm_id,
                    osm_type=brunch_restaurant.osm_type,
                    relevance_score=brunch_restaurant.relevance_score,
                    theme_score=brunch_restaurant.theme_score,
                    tag_score=brunch_restaurant.tag_score,
                    matched_theme=brunch_restaurant.matched_theme,
                    start_time=brunch_time // 60,
                    end_time=(brunch_time + 90) // 60,  # Slightly longer duration for brunch
                    duration=90,
                    travel_time=0,
                    distance_from_hotel=self._haversine_distance(hotel_location, brunch_restaurant.location)
                )
                day_meals.append(brunch_info)
                
                # Skip breakfast since we have brunch
                meal_times.pop("breakfast", None)
            
            # Schedule remaining meals
            for meal_type, meal_time in meal_times.items():
                if not other_restaurants:
                    break
                    
                # Select a restaurant
                restaurant = random.choice(other_restaurants)
                other_restaurants.remove(restaurant)
                
                # Create meal info
                meal_info = POI(
                    name=restaurant.name,
                    description=restaurant.description,
                    location=restaurant.location,
                    type=restaurant.type,
                    tags=restaurant.tags,
                    osm_id=restaurant.osm_id,
                    osm_type=restaurant.osm_type,
                    relevance_score=restaurant.relevance_score,
                    theme_score=restaurant.theme_score,
                    tag_score=restaurant.tag_score,
                    matched_theme=restaurant.matched_theme,
                    start_time=meal_time // 60,
                    end_time=(meal_time + 60) // 60,
                    duration=60,
                    travel_time=0,
                    distance_from_hotel=self._haversine_distance(hotel_location, restaurant.location)
                )
                day_meals.append(meal_info)
            
            daily_meals.append(day_meals)
        
        return daily_meals

    def generate_itinerary(self, duration: int, start_date: datetime, activities_poi: List[POI], food_poi: List[POI], hotel_info: Dict[str, Any], user_tags: List[List[str]] = None) -> Dict[str, Any]:
        hotel_location = hotel_info['location']
        
        # Schedule activities and meals separately
        activities = self._schedule_activities(activities_poi, hotel_location, duration, user_tags)
        meals = self._schedule_meals(food_poi, hotel_location, duration)
        
        # Combine activities and meals into daily itineraries
        itinerary = []
        for day in range(duration):
            daily_activities = activities[day]
            daily_meals = meals[day]
            
            # Calculate daily summary
            daily_summary = {
                'total_activities': len(daily_activities),
                'total_meals': len(daily_meals),
                'total_travel_time': 0,  # We'll calculate this later
                'total_activity_time': sum(item.duration for item in daily_activities),
                'total_meal_time': sum(item.duration for item in daily_meals)
            }
            
            # Create daily itinerary
            daily_itinerary = {
                'day': day + 1,
                'date': start_date + timedelta(days=day),
                'hotel': hotel_info,
                'activities': daily_activities,
                'meals': daily_meals,
                'daily_summary': daily_summary
            }
            
            # Calculate travel times between activities
            for i in range(len(daily_activities) - 1):
                current = daily_activities[i]
                next_activity = daily_activities[i + 1]
                travel_time = self._estimate_travel_time(current.location, next_activity.location)
                current.time_to_next = travel_time
                next_activity.gap_until_next = 10 + travel_time
                daily_summary['total_travel_time'] += travel_time
            
            # Calculate travel times between meals
            for i in range(len(daily_meals) - 1):
                current = daily_meals[i]
                next_meal = daily_meals[i + 1]
                travel_time = self._estimate_travel_time(current.location, next_meal.location)
                current.time_to_next = travel_time
                next_meal.gap_until_next = 10 + travel_time
                daily_summary['total_travel_time'] += travel_time
            
            itinerary.append(daily_itinerary)
        
        # Calculate overall summary
        total_activities = sum(day['daily_summary']['total_activities'] for day in itinerary)
        total_meals = sum(day['daily_summary']['total_meals'] for day in itinerary)
        total_travel_time = sum(day['daily_summary']['total_travel_time'] for day in itinerary)
        total_activity_time = sum(day['daily_summary']['total_activity_time'] for day in itinerary)
        total_meal_time = sum(day['daily_summary']['total_meal_time'] for day in itinerary)
        
        return {
            'itinerary': itinerary,
            'summary': f'Your {duration}-day itinerary has been generated with optimized travel times and well-distributed timing.',
            'total_activities': total_activities,
            'total_meals': total_meals,
            'total_travel_time': total_travel_time,
            'total_activity_time': total_activity_time,
            'total_meal_time': total_meal_time
        }


if __name__ == "__main__":
    agent = ItineraryAgent()

    start_date = datetime(2025, 6, 1)
    hotel = {
        "name": "Shangri-La Paris",
        "location": (48.8647, 2.2938),
        "rating": 5.0
    }
    activities = [
        POI(
            name="Eiffel Tower",
            description="Iconic iron lattice tower",
            location=(48.8584, 2.2945),
            type="attraction",
            tags=[("tourism", "attraction")],
            osm_id=1,
            osm_type="node",
            relevance_score=1.0,
            rating=5.0
        ),
        POI(
            name="Louvre Museum",
            description="World's largest art museum",
            location=(48.8606, 2.3376),
            type="museum",
            tags=[("tourism", "museum")],
            osm_id=2,
            osm_type="node",
            relevance_score=1.0,
            rating=5.0
        ),
        POI(
            name="Notre-Dame Cathedral",
            description="Historic Catholic cathedral",
            location=(48.8530, 2.3499),
            type="attraction",
            tags=[("tourism", "cathedral")],
            osm_id=3,
            osm_type="node",
            relevance_score=1.0,
            rating=5.0
        ),
        POI(
            name="Montmartre",
            description="Artistic hilltop district",
            location=(48.8867, 2.3431),
            type="park",
            tags=[("leisure", "park")],
            osm_id=4,
            osm_type="node",
            relevance_score=1.0,
            rating=4.5
        ),
        POI(
            name="Galeries Lafayette",
            description="Luxury department store",
            location=(48.8738, 2.3320),
            type="shopping",
            tags=[("shop", "department_store")],
            osm_id=5,
            osm_type="node",
            relevance_score=1.0,
            rating=4.5
        )
    ]
    restaurants = [
        # Fine dining restaurants
        POI(
            name="Le Jules Verne",
            description="Fine dining restaurant at Eiffel Tower",
            location=(48.8584, 2.2945),
            type="restaurant",
            tags=[("cuisine", "french")],
            osm_id=6,
            osm_type="node",
            relevance_score=1.0,
            rating=4.9
        ),
        POI(
            name="Le Meurice",
            description="Luxury hotel restaurant",
            location=(48.8655, 2.3266),
            type="restaurant",
            tags=[("cuisine", "french")],
            osm_id=7,
            osm_type="node",
            relevance_score=1.0,
            rating=4.8
        ),
        POI(
            name="Le Cinq",
            description="Michelin-starred restaurant",
            location=(48.8665, 2.3190),
            type="restaurant",
            tags=[("cuisine", "french")],
            osm_id=8,
            osm_type="node",
            relevance_score=1.0,
            rating=4.9
        ),
        # Brunch cafes
        POI(
            name="Angelina",
            description="Famous Parisian cafe with excellent brunch",
            location=(48.8611, 2.3361),
            type="cafe",
            tags=[("cuisine", "french"), ("meal_type", "brunch")],
            osm_id=9,
            osm_type="node",
            relevance_score=1.0,
            rating=4.7
        ),
        POI(
            name="Café Constant",
            description="Charming cafe with great brunch options",
            location=(48.8633, 2.3317),
            type="cafe",
            tags=[("cuisine", "french"), ("meal_type", "brunch")],
            osm_id=10,
            osm_type="node",
            relevance_score=1.0,
            rating=4.6
        ),
        POI(
            name="Café Kitsuné",
            description="Modern cafe with international brunch menu",
            location=(48.8648, 2.3361),
            type="cafe",
            tags=[("cuisine", "international"), ("meal_type", "brunch")],
            osm_id=11,
            osm_type="node",
            relevance_score=1.0,
            rating=4.5
        )
    ]

    result = agent.generate_itinerary(
        duration=2,
        start_date=start_date,
        activities_poi=activities,
        food_poi=restaurants,
        hotel_info=hotel
    )
    print(result)

def display_itinerary(itinerary: Dict[str, Any]) -> None:
    """
    Display the itinerary in a readable format.
    
    Args:
        itinerary: Complete itinerary with detailed information
    """
    print("=== TRAVEL BUDDY ITINERARY ===\n")
    
    for day in itinerary['itinerary']:
        print(f"\nDay {day['day']} - {day['date'].strftime('%A, %B %d')}")
        print(f"\nHotel: {day['hotel']['name']}")
        print("\n=== ACTIVITIES ===\n")
        
        for activity in day['activities']:
            print(f"{activity.name} ({activity.type})")
            print(f"Time: {activity.start_time:02d}:{activity.end_time:02d}")
            print(f"Duration: {activity.duration} minutes")
            print(f"Travel Time: {activity.travel_time} minutes")
            print(f"Distance from Last: {activity.distance_from_last:.2f} km" if activity.distance_from_last is not None else "Distance from Last: N/A")
            print(f"Distance to Next: {activity.distance_to_next:.2f} km" if activity.distance_to_next is not None else "Distance to Next: N/A")
            print(f"Gap Until Next: {activity.gap_until_next} minutes" if activity.gap_until_next is not None else "Gap Until Next: N/A")
            print(f"Rating: {activity.rating:.1f}" if activity.rating is not None else "Rating: N/A")
            print()  # Empty line between activities
        
        print("\n=== MEALS ===\n")
        for meal in day['meals']:
            print(f"{meal.name} ({meal.type})")
            print(f"Time: {meal.start_time:02d}:{meal.end_time:02d}")
            print(f"Duration: {meal.duration} minutes")
            print(f"Travel Time: {meal.travel_time} minutes")
            print(f"Distance from Last: {meal.distance_from_last:.2f} km" if meal.distance_from_last is not None else "Distance from Last: N/A")
            print(f"Distance to Next: {meal.distance_to_next:.2f} km" if meal.distance_to_next is not None else "Distance to Next: N/A")
            print(f"Gap Until Next: {meal.gap_until_next} minutes" if meal.gap_until_next is not None else "Gap Until Next: N/A")
            print(f"Rating: {meal.rating:.1f}" if meal.rating is not None else "Rating: N/A")
            print()  # Empty line between meals
    
    print("\n=== ITINERARY SUMMARY ===")
    print(f"Total Activities: {itinerary['total_activities']}")
    print(f"Total Meals: {itinerary['total_meals']}")
    print(f"Total Travel Time: {itinerary['total_travel_time']} minutes")
    print(f"Total Activity Time: {itinerary['total_activity_time']} minutes")
    print(f"Total Meal Time: {itinerary['total_meal_time']} minutes")


if __name__ == "__main__":
    agent = ItineraryAgent()
    
    start_date = datetime(2025, 6, 1)
    hotel = {
        "name": "Shangri-La Paris",
        "location": (48.8647, 2.2938),
        "rating": 5.0
    }
    
    # Create POI objects for activities
    activities = [
        POI(
            name="Eiffel Tower",
            description="Iconic iron lattice tower overlooking Paris",
            location=(48.8584, 2.2945),
            type="attraction",
            tags=[("tourism", "yes"), ("attraction", "yes")],
            osm_id=12345,
            osm_type="node",
            relevance_score=0.9,
            theme_score=0.8,
            tag_score=0.7,
            matched_theme="architecture",
            price=50.0,
            luxury_level="premium",
            rating=4.9,
            amenities=["elevator", "wheelchair_access", "audio_guide"]
        ),
        POI(
            name="Louvre Museum",
            description="World's largest art museum and historic monument",
            location=(48.8606, 2.3376),
            type="museum",
            tags=[("tourism", "yes"), ("museum", "yes")],
            osm_id=12346,
            osm_type="node",
            relevance_score=0.8,
            theme_score=0.7,
            tag_score=0.6,
            matched_theme="art",
            price=17.0,
            luxury_level="premium",
            rating=4.8,
            amenities=["audio_guide", "wheelchair_access", "lockers"]
        ),
        POI(
            name="Notre-Dame Cathedral",
            description="Medieval Catholic cathedral on the Île de la Cité",
            location=(48.853, 2.3499),
            type="attraction",
            tags=[("tourism", "yes"), ("cathedral", "yes")],
            osm_id=12347,
            osm_type="node",
            relevance_score=0.7,
            theme_score=0.6,
            tag_score=0.5,
            matched_theme="history",
            price=0.0,
            luxury_level="standard",
            rating=4.7,
            amenities=["wheelchair_access", "audio_guide"]
        ),
        POI(
            name="Montmartre",
            description="Hill in Paris with artistic history and views",
            location=(48.8867, 2.3431),
            type="park",
            tags=[("tourism", "yes"), ("park", "yes")],
            osm_id=12348,
            osm_type="node",
            relevance_score=0.6,
            theme_score=0.5,
            tag_score=0.4,
            matched_theme="art",
            price=0.0,
            luxury_level="standard",
            rating=4.5,
            amenities=["picnic_areas", "playground", "viewpoints"]
        ),
        POI(
            name="Galeries Lafayette",
            description="Luxury department store in Paris",
            location=(48.8738, 2.332),
            type="shopping",
            tags=[("amenity", "shop"), ("luxury", "yes")],
            osm_id=12349,
            osm_type="node",
            relevance_score=0.5,
            theme_score=0.4,
            tag_score=0.3,
            matched_theme="shopping",
            price=100.0,
            luxury_level="premium",
            rating=4.6,
            amenities=["vip_services", "free_wifi", "restrooms"]
        )
    ]
    
    # Create POI objects for meals
    meals = [
        POI(
            name="Le Jules Verne",
            description="Fine dining restaurant in the Eiffel Tower",
            location=(48.8584, 2.2945),
            type="restaurant",
            tags=[("amenity", "restaurant"), ("cuisine", "french"), ("luxury", "yes")],
            osm_id=23456,
            osm_type="node",
            relevance_score=0.9,
            theme_score=0.8,
            tag_score=0.7,
            matched_theme="food",
            price=250.0,
            luxury_level="premium",
            rating=4.9,
            amenities=["private_rooms", "wine_list", "vegetarian_options"]
        ),
        POI(
            name="Le Coq Rico",
            description="Traditional French bistro in Montmartre",
            location=(48.8867, 2.3431),
            type="restaurant",
            tags=[("amenity", "restaurant"), ("cuisine", "french")],
            osm_id=23457,
            osm_type="node",
            relevance_score=0.8,
            theme_score=0.7,
            tag_score=0.6,
            matched_theme="food",
            price=80.0,
            luxury_level="standard",
            rating=4.7,
            amenities=["outdoor_seating", "wifi", "vegetarian_options"]
        )
    ]

    try:
        result = agent.generate_itinerary(2, start_date, activities, meals, hotel)
        display_itinerary(result)
    except Exception as e:
        print(f"Error generating itinerary: {str(e)}")