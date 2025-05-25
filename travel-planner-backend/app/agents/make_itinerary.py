from . import flights
from . import hotels
import random
from . import hotel_agent
from . import trip_planner_agent
import json
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

def process_date(date):
    return date[:10]

def format_day_activities(activities_data):
    formatted = {}

    for day_key, day_content in activities_data.items():
        day_number = int(day_key.split("_")[1])
        activity_summaries = []

        for activity in day_content['activities']:
            name = activity['name']
            duration = activity['duration']
            price = activity['price']
            website = activity['website']

            summary = f"{name} ({duration.lower()}"
            if price and price != "Free":
                summary += f", price: {price}"
            elif price == "Free":
                summary += ", free"
            if website:
                summary += f", website: {website}"
            summary += ")"
            activity_summaries.append(summary)


        for meal in day_content['meals']:
            name = meal['name']
            duration = meal['duration']
            website = meal['website'] if activity['website'] else "N/A"

            summary = f"{name} ({duration.lower()}"
            if website:
                summary += f", website: {website}"
            summary += ")"
            activity_summaries.append(summary)

        if activity_summaries:
            formatted["Day " + str(day_number)] = "\n".join(activity_summaries)
        else:
            pass

    return formatted


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

    start_date = process_date(user_input['start_date'])
    end_date = process_date(user_input['end_date'])

    access_token = flights.get_access_token(os.getenv("AMADEUS_API_KEY"), os.getenv("AMADEUS_API_SECRET"))

    flight_data = flights.get_flight_json_data(from_airport, to_airport, start_date, access_token)
    depart = condense_data(flight_data, from_airport, to_airport, start_date)
    return_flight = flights.get_flight_json_data(to_airport, from_airport, end_date, access_token)
    return_flight = condense_data(return_flight, to_airport, from_airport, end_date)

    return depart, return_flight

def process_hotel_data(user_input):
    return hotels.use_agent_to_calc_dist(user_input['to'])

def format(data):
    return data


def format(data):
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
        return output

    
    full_data = {
        "0": choose_one_flight_and_hotel(),
        "1": choose_one_flight_and_hotel(),
        "2": choose_one_flight_and_hotel()
    }
    activities = format_day_activities(data['Activities'])
    full_data['0'].update(activities)
    full_data['1'].update(activities)
    full_data['2'].update(activities)
    return full_data



        

def make_itinerary(user_input):
    complete_data = {}
    departing_flight, return_flight = process_flight_data(user_input)

    hotel_data = process_hotel_data(user_input)

    planner = trip_planner_agent.TripPlannerAgent()

    start_date = datetime.fromisoformat(user_input['start_date'][:-1] + '+00:00')
    end_date = datetime.fromisoformat(user_input['end_date'][:-1] + '+00:00')

    # Calculate duration in days
    duration = (end_date - start_date).days
    trip = planner.plan_trip(
        user_input=user_input['from'] + " " + user_input['additionalInfo'],
        destination=user_input['to'],
        start_date=start_date.strftime("%Y-%m-%d"),
        duration=duration
    )

    trip = planner.format_itinerary(trip)

    activities = json.dumps(trip, cls=trip_planner_agent.DateTimeEncoder)

    complete_data['flight_depart'] = departing_flight
    complete_data['return_flight'] = return_flight
    complete_data['hotel_data'] = hotel_data
    complete_data['Activities'] = json.loads(activities)
    print(complete_data)
    return format(complete_data)
