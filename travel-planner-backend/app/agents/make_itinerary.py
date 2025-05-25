import flights
import hotels
import random
import hotel_agent

def process_date(date):
    return date[:10]

def condense_data(data, origin, destination, depart):
    result = {}
    result['Flight offer'] = f"Depart from {origin} to {destination} on {depart}:\n"
    result['Offers'] = []

    for offer in data.get('data', []):
        offer_details = {}
        price = offer['price']['total']
        offer_details['Price'] = f"${price}"
        offer_details['Segments'] = []

        for itinerary in offer.get('itineraries', []):
            for segment in itinerary.get('segments', []):
                dep = segment['departure']
                arr = segment['arrival']
                carrier = segment['carrierCode']
                flight_number = segment['number']
                segment_details = (
                    f"Flight {carrier}{flight_number}: "
                    f"{dep['iataCode']} at {dep['at']} -> "
                    f"{arr['iataCode']} at {arr['at']}"
                )
                offer_details['Segments'].append(segment_details)

        result['Offers'].append(offer_details)

    return result

def process_flight_data(user_input):
    depart_from = user_input['from']
    depart_to = user_input['to']

    # convert the from and to values into airports

    goal_agent = hotel_agent.GoalAgent()

    depart_from = goal_agent.extract(depart_from)
    depart_to = goal_agent.extract(depart_to)

    from_airport = random.choice(list(depart_from.keys()))
    to_airport = random.choice(list(depart_to.keys()))

    start_date = process_date(user_input['startDate'])
    end_date = process_date(user_input['endDate'])

    access_token = flights.get_access_token("notWU49gJl5MUZs5Wij73gxQX0RCj9EI",  "5WGFoGbZy57N1eUp")

    flight_data = flights.get_flight_json_data(from_airport, to_airport, start_date, access_token)
    depart = condense_data(flight_data, from_airport, to_airport, start_date)
    return_flight = flights.get_flight_json_data(to_airport, from_airport, end_date, access_token)
    return_flight = condense_data(return_flight, to_airport, from_airport, end_date)

    return depart, return_flight

def process_hotel_data(user_input):
    return hotels.use_agent_to_calc_dist(user_input)


def make_itinerary(user_input):
    complete_data = {}
    departing_flight, return_flight = process_flight_data(user_input)

    hotel_data = process_hotel_data(user_input)

    complete_data['flight_depart'] = departing_flight
    complete_data['return_flight'] = return_flight
    complete_data['hotel_data'] = hotel_data
    return complete_data

data = {"from":"San Francisco", "to":"London, UK","startDate":"2025-06-16T07:00:00.000Z","endDate":"2025-05-31T07:00:00.000Z","people":"4","additionalInfo":"I want to go to museums and Buckhingam Palace. I want a luxury hotel and Indian restaurants."}
print(make_itinerary(data))



