from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from math import radians, cos, sin, sqrt, atan2, asin
import random
from app.utils.api_wrappers import fetch_places, get_location_coordinates
from app.agents.poi_agent import POI


def overlaps(start1, end1, start2, end2):
    return max(start1, start2) < min(end1, end2)


class ItineraryAgent:
    def __init__(self):
        self.day_start_hour = 9
        self.day_end_hour = 21
        self.buffer_time = 30
        self.max_activities_per_day = 4
        self.default_walking_speed = 5.0  # km/h
        self.default_driving_speed = 40.0  # km/h

    def generate_itinerary(self, duration: int, start_date: datetime, activities_poi: List[POI], food_poi: List[POI], hotel_info: Dict[str, Any], user_tags: List[List[str]] = None) -> Dict[str, Any]:
        hotel_location = hotel_info['location']
        booked_slots_per_day = [[] for _ in range(duration)]

        activities = self._schedule_activities(activities_poi, hotel_location, duration, user_tags, booked_slots_per_day)
        meals = self._schedule_meals(food_poi, hotel_location, duration, booked_slots_per_day)

        itinerary = []
        for day in range(duration):
            daily_activities = activities[day]
            daily_meals = meals[day]

            daily_summary = {
                'total_activities': len(daily_activities),
                'total_meals': len(daily_meals),
                'total_activity_time': sum(item['duration'] for item in daily_activities),
                'total_meal_time': sum(item['duration'] for item in daily_meals)
            }

            daily_itinerary = {
                'day': day + 1,
                'date': start_date + timedelta(days=day),
                'hotel': hotel_info,
                'activities': daily_activities,
                'meals': daily_meals,
                'daily_summary': daily_summary
            }

            itinerary.append(daily_itinerary)

        total_activities = sum(day['daily_summary']['total_activities'] for day in itinerary)
        total_meals = sum(day['daily_summary']['total_meals'] for day in itinerary)
        total_activity_time = sum(day['daily_summary']['total_activity_time'] for day in itinerary)
        total_meal_time = sum(day['daily_summary']['total_meal_time'] for day in itinerary)

        return {
            'itinerary': itinerary,
            'summary': f'Your {duration}-day itinerary has been generated with optimized travel times and well-distributed timing.',
            'total_activities': total_activities,
            'total_meals': total_meals,
            'total_activity_time': total_activity_time,
            'total_meal_time': total_meal_time
        }

    def _calculate_duration(self, poi: POI) -> int:
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
        popularity = poi.theme_score
        return int(base_duration * (1 + 0.2 * (popularity - 0.5)))

    def _schedule_activities(self, pois: List[POI], hotel_location: Tuple[float, float], days: int, user_tags: List[List[str]], booked_slots_per_day: List[List[Tuple[int, int]]]) -> List[List[Dict[str, Any]]]:
        user_tag_set = set(tuple(tag) for tag in user_tags)
        relevant_pois = [poi for poi in pois if set(tuple(tag) for tag in poi.tags).intersection(user_tag_set)]
        if not relevant_pois:
            relevant_pois = pois[:]
        relevant_pois.sort(key=lambda p: p.relevance_score, reverse=True)
        used_pois = set()
        daily_activities = []

        for day_index in range(days):
            schedule = []
            current_time = self.day_start_hour * 60
            last_location = hotel_location
            activities_count = 0
            booked_slots = booked_slots_per_day[day_index]

            for poi in relevant_pois:
                if poi.name in used_pois:
                    continue

                duration = self._calculate_duration(poi)
                start_time = current_time + self.buffer_time
                end_time = start_time + duration

                if any(overlaps(start_time, end_time, b[0], b[1]) for b in booked_slots):
                    continue

                activity = {
                    "name": poi.name,
                    "description": poi.description,
                    "location": poi.location,
                    "type": poi.type,
                    "tags": poi.tags,
                    "price": poi.price,
                    "luxury_level": poi.luxury_level,
                    "osm_id": poi.osm_id,
                    "osm_type": poi.osm_type,
                    "relevance_score": poi.relevance_score,
                    "theme_score": poi.theme_score,
                    "tag_score": poi.tag_score,
                    "matched_theme": poi.matched_theme,
                    "start_time": start_time // 60,
                    "end_time": end_time // 60,
                    "duration": duration,
                    "rating": poi.rating
                }

                schedule.append(activity)
                booked_slots.append((start_time, end_time))
                current_time = end_time + self.buffer_time
                last_location = poi.location
                used_pois.add(poi.name)
                activities_count += 1

                if activities_count >= self.max_activities_per_day:
                    break

            daily_activities.append(schedule)
        return daily_activities

    def _schedule_meals(self, restaurants: List[POI], hotel_location: Tuple[float, float], days: int, booked_slots_per_day: List[List[Tuple[int, int]]]) -> List[List[Dict[str, Any]]]:
        if restaurants:
            default_meal_times = {
                "lunch": 13 * 60,
                "dinner": 19 * 60
            }
            brunch_time = 11 * 60
            fixed_breakfast_time = 8 * 60
            daily_meals = []

            for day_index in range(days):
                day_meals = []
                booked_slots = booked_slots_per_day[day_index]

                # 🥐 Add Fixed Breakfast from 8:00–9:00 AM
                breakfast_restaurants = [r for r in restaurants if "breakfast" in r.description.lower()]
                breakfast_restaurant = random.choice(breakfast_restaurants) if breakfast_restaurants else random.choice(restaurants)

                breakfast_info = {
                    "name": breakfast_restaurant.name + " (Fixed Breakfast)",
                    "description": breakfast_restaurant.description,
                    "location": breakfast_restaurant.location,
                    "type": breakfast_restaurant.type,
                    "tags": breakfast_restaurant.tags,
                    "price": breakfast_restaurant.price,
                    "luxury_level": breakfast_restaurant.luxury_level,
                    "osm_id": breakfast_restaurant.osm_id,
                    "osm_type": breakfast_restaurant.osm_type,
                    "relevance_score": breakfast_restaurant.relevance_score,
                    "theme_score": breakfast_restaurant.theme_score,
                    "tag_score": breakfast_restaurant.tag_score,
                    "matched_theme": breakfast_restaurant.matched_theme,
                    "start_time": fixed_breakfast_time // 60,
                    "end_time": (fixed_breakfast_time + 60) // 60,
                    "duration": 60,
                    "rating": breakfast_restaurant.rating
                }
                day_meals.append(breakfast_info)
                booked_slots.append((fixed_breakfast_time, fixed_breakfast_time + 60))

                # ☕ Try brunch if available
                brunch_restaurants = [r for r in restaurants if any(tag[1] == "brunch" for tag in r.tags)]
                other_restaurants = [r for r in restaurants if not any(tag[1] == "brunch" for tag in r.tags)]

                if brunch_restaurants:
                    brunch_restaurant = random.choice(brunch_restaurants)
                    brunch_duration = 90
                    brunch_start = self.find_nearest_available_slot(brunch_time, brunch_duration, booked_slots)

                    if brunch_start is not None:
                        brunch_info = {
                            "name": brunch_restaurant.name,
                            "description": brunch_restaurant.description,
                            "location": brunch_restaurant.location,
                            "type": brunch_restaurant.type,
                            "tags": brunch_restaurant.tags,
                            "osm_id": brunch_restaurant.osm_id,
                            "osm_type": brunch_restaurant.osm_type,
                            "relevance_score": brunch_restaurant.relevance_score,
                            "theme_score": brunch_restaurant.theme_score,
                            "tag_score": brunch_restaurant.tag_score,
                            "matched_theme": brunch_restaurant.matched_theme,
                            "start_time": brunch_start // 60,
                            "end_time": (brunch_start + brunch_duration) // 60,
                            "duration": brunch_duration,
                            "rating": brunch_restaurant.rating
                        }
                        day_meals.append(brunch_info)
                        booked_slots.append((brunch_start, brunch_start + brunch_duration))

                # 🍽 Schedule lunch and dinner
                for meal_type, target_time in default_meal_times.items():
                    if not other_restaurants:
                        break

                    duration = 60
                    start_time = self.find_nearest_available_slot(target_time, duration, booked_slots)
                    if start_time is None:
                        continue

                    restaurant = random.choice(other_restaurants)
                    other_restaurants.remove(restaurant)

                    meal_info = {
                        "name": restaurant.name,
                        "description": restaurant.description,
                        "location": restaurant.location,
                        "type": restaurant.type,
                        "tags": restaurant.tags,
                        "osm_id": restaurant.osm_id,
                        "osm_type": restaurant.osm_type,
                        "relevance_score": restaurant.relevance_score,
                        "theme_score": restaurant.theme_score,
                        "tag_score": restaurant.tag_score,
                        "matched_theme": restaurant.matched_theme,
                        "start_time": start_time // 60,
                        "end_time": (start_time + duration) // 60,
                        "duration": duration,
                        "rating": restaurant.rating
                    }
                    day_meals.append(meal_info)
                    booked_slots.append((start_time, start_time + duration))

                daily_meals.append(day_meals)
            return daily_meals
        return {day: [] for day in range(days)}



    def find_nearest_available_slot(self, desired_time: int, duration: int, booked_slots: List[Tuple[int, int]], window: int = 90) -> Optional[int]:
        """
        Find the closest available `duration`-minute slot to `desired_time`, within ±window minutes.
        Returns the starting minute of the slot, or None if none is found.
        """
        for offset in range(window + 1):
            for direction in [-1, 1]:
                trial_start = desired_time + direction * offset
                trial_end = trial_start + duration
                if trial_start < self.day_start_hour * 60 or trial_end > self.day_end_hour * 60:
                    continue
                if all(not overlaps(trial_start, trial_end, b[0], b[1]) for b in booked_slots):
                    return trial_start
        return None

