import requests

API_KEY = "notWU49gJl5MUZs5Wij73gxQX0RCj9EI"
API_SECRET = "5WGFoGbZy57N1eUp"

def get_access_token(api_key, api_secret):
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    payload = {
        'grant_type': 'client_credentials',
        'client_id': api_key,
        'client_secret': api_secret
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, data=payload, headers=headers)
    response.raise_for_status()
    token = response.json()['access_token']
    return token

def search_flights(origin, destination, departure_date, access_token):
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": departure_date,
        "adults": 1,
        "max": 5  # limit results for demo
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def get_flight_json_data(origin, destination, departure_date, access_token):
    return search_flights(origin, destination, departure_date, access_token)


def main():
    """Main method used for testing parsing through json file & data"""
    access_token = get_access_token(API_KEY, API_SECRET)
    origin = "LAX"
    destination = "CDG"
    departure_date = "2025-06-12"

    # flight offers is the main data
    flight_offers = get_flight_json_data(origin, destination, departure_date, access_token)
    print(flight_offers)

    print(f"Flight offers from {origin} to {destination} on {departure_date}:\n")
    for offer in flight_offers.get('data', []):
        price = offer['price']['total']
        itinerary = offer['itineraries'][0]
        segments = itinerary['segments']

        print(f"Price: ${price}")
        for segment in segments:
            dep = segment['departure']
            arr = segment['arrival']
            carrier = segment['carrierCode']
            flight_number = segment['number']

            print(f"Flight {carrier}{flight_number}: {dep['iataCode']} at {dep['at']} -> {arr['iataCode']} at {arr['at']}")
        print("-" * 50)

if __name__ == "__main__":
    main()