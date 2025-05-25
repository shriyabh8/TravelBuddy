import json
import requests
import os
import dotenv

dotenv.load_dotenv()

# Get user input here to get the location (testing purposes

def get_input():
    print("Enter the location you would like to visit: ")
    location = input()
    print("Enter the radius of your travel")
    radius = input()
    return location, radius

# integrating opencage geocoder api to find the latitude and longitude of any given location

def get_lat_lng_opencage(location):
    api_key = os.getenv("ORS_API_KEY")
    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {
        "q": location,
        "key": api_key
    }
    response = requests.get(url, params=params).json()
    if response["results"]:
        lat = response["results"][0]["geometry"]["lat"]
        lng = response["results"][0]["geometry"]["lng"]
        return lat, lng
    else:
        return None

# Getting data of the best locations to visit and their activities

def get_access_token(client_id: str, client_secret: str) -> str:
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()['access_token']

def get_tours_and_activities(access_token: str, latitude: float, longitude: float, radius: int = 1):
    url = "https://test.api.amadeus.com/v1/shopping/activities"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "radius": radius
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    print(json.dumps(response.json(), indent=4))
    return response.json()

def get_data(latitude, longitude, radius):
    """Gets and returns all the data of the activities in a given location."""
    client_id = os.getenv("AMADEUS_API_KEY")
    client_secret = os.getenv("AMADEUS_API_SECRET")

    access_token = get_access_token(client_id, client_secret)

    activities = get_tours_and_activities(access_token, latitude, longitude, radius)
    return json.dumps(activities, indent=2)

def sort_activities_by_rating_ascending(data):
    activity_ratings = {}
    non_rated_activities = []
    for activity in data["data"]:
        name = activity.get("name", "Unknown")
        rating_str = activity.get("rating")
        if rating_str:
            try:
                rating = float(rating_str)
                activity_ratings[name] = rating
            except ValueError:
                continue
        else:
            non_rated_activities.append(name)

    filtered_activities = {name: rating for name, rating in activity_ratings.items() if isinstance(rating, float)}

    sorted_activities = dict(sorted(filtered_activities.items(), key=lambda item: item[1], reverse=True))
    return sorted_activities, non_rated_activities


def parse_data():
    """Parses through the activity data and sorts it based off of the rating. Sets the nonrated activities
    at the end. """
    location, radius = get_input()
    latitude, longitude = get_lat_lng_opencage(location)

    data = get_data(latitude, longitude, radius)
    data = json.loads(data)

    # modify this sort and write more sort functions later for dealing with the kind of sort that the user wants
    sorted_activities, non_rated_activities = sort_activities_by_rating_ascending(data)

    for name, rating in sorted_activities.items():
        print(f"{name}: {rating}")

    print('\nOther popular activities:\n')
    for name in non_rated_activities:
        print(name)


def main():
    parse_data()

main()
