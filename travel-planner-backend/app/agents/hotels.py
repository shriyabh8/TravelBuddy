import requests
from . import hotel_agent
import math
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AMADEUS_API_KEY")
API_SECRET = os.getenv("AMADEUS_API_SECRET")

TOKEN_CACHE = None

def get_access_token_cached(api_key, api_secret):
    global TOKEN_CACHE
    if TOKEN_CACHE is None:
        TOKEN_CACHE = get_access_token(api_key, api_secret)
    return TOKEN_CACHE

def get_access_token(api_key, api_secret):
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"  # test token URL
    payload = {
        'grant_type': 'client_credentials',
        'client_id': api_key,
        'client_secret': api_secret
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, data=payload, headers=headers)
    response.raise_for_status()
    return response.json()['access_token']


def get_hotels_by_city(city_code, access_token):
    url = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"  # test hotel data URL
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    params = {
        "cityCode": city_code
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def get_hotels(city_code, API_KEY, API_SECRET):
    access_token = get_access_token_cached(API_KEY, API_SECRET)

    hotels_response = get_hotels_by_city(city_code, access_token)
    hotels = hotels_response.get('data', [])

    return hotels

def haversine(coord1, coord2):
    # Coordinates in decimal degrees (e.g. 51.47, -0.4543)
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))

    # Radius of Earth in kilometers: use 3958.8 for miles
    r = 6371
    return c * r

import random

def add_price_to_hotel(hotel_data):
    for hotel in hotel_data:
        hotel['price'] = random.randint(153, 302)
    return hotel_data

def get_hotel_json_data(user_input):
    json_data = []
    agent = hotel_agent.GoalAgent()
    goal_data = agent.extract(user_input)
    for code in goal_data.items():
        hotel_list = get_hotels(code[0], API_KEY, API_SECRET)
        hotel_list = add_price_to_hotel(hotel_list)
        json_data.append(hotel_list)
    return json_data

def use_agent_to_calc_dist(user_input):
    agent = hotel_agent.GoalAgent()
    hotels = []
    main_data = {}
    # Extract and normalize preferences
    goal_data = agent.extract(user_input)
    for code in goal_data.items():
        lat_lon = code[1]
        lat = lat_lon['lat']
        lon = lat_lon['lon']
        hotel_list = get_hotels(code[0], API_KEY, API_SECRET)
        hotel_list = add_price_to_hotel(hotel_list)
        count = 0
        # hotel list contains a list of json data :)
        for hotel in hotel_list:
            name = hotel.get('name')
            price = hotel.get('price')
            latitude = hotel.get('geoCode', {}).get('latitude')
            longitude = hotel.get('geoCode', {}).get('longitude')
            distance = haversine((latitude, longitude), (lat, lon))
            #print(f"Hotel: {name}\n  Price: ${price}\n  Location: ({latitude}, {longitude})\n  Distance from Airport: {distance}\n")
            main_data['name'] = name
            main_data['price'] = price
            main_data['Distance from Airport'] = distance
            hotels.append(main_data.copy())
            if count >= 3:
                break
            count += 1
    return hotels

def main():
    user_input = "Take me to New York for 3 days and show me the available activities."
    use_agent_to_calc_dist(user_input)

    print(get_hotel_json_data(user_input))



if __name__ == "__main__":
    main()