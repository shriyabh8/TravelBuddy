import json

def main():
    read()
    write()

def read():
    try:
        last_line = None
        with open('form-data.txt', 'r') as f_in:
            for line in f_in:
                last_line = line.strip()

        if last_line:
            try:
                return json.loads(last_line)
                with open('itinerary-data.txt', 'w') as f_out:
                    #mock data
                    f_out.write('{"Flights": "Flight To: INSERTFlight Back: INSERT", "Hotels": "hotel name and other information", "people": "3", "additionalInfo": "4"}\n')
                    f_out.write('{"location": "5", "dates": "6", "people": "7", "additionalInfo": "8"}\n')
                    f_out.write('{"location": "9", "dates": "0", "people": "1", "additionalInfo": "2"}\n')
            except json.JSONDecodeError:
                pass

    except Exception as e:
        print(f"Error processing data: {e}")

def write():
    try:
        with open('itinerary-data.txt', 'w') as f_out:
            f_out.write('{\n  "1": ')
            f_out.write(json.dumps(choose_one_flight_and_hotel({'flight_data': {'Flight offer': 'Depart from SFO to LHR on 2025-06-16:\n', 'Offers': [{'Price': '$431.66', 'Segments': ['Flight TP238: SFO at 2025-06-16T16:20:00 -> LIS at 2025-06-17T11:35:00', 'Flight TP1350: LIS at 2025-06-17T15:00:00 -> LHR at 2025-06-17T17:45:00']}, {'Price': '$431.66', 'Segments': ['Flight TP238: SFO at 2025-06-16T16:20:00 -> LIS at 2025-06-17T11:35:00', 'Flight TP1364: LIS at 2025-06-17T16:05:00 -> LHR at 2025-06-17T18:50:00']}, {'Price': '$472.14', 'Segments': ['Flight WS1509: SFO at 2025-06-16T12:50:00 -> YYC at 2025-06-16T16:34:00', 'Flight WS18: YYC at 2025-06-16T20:35:00 -> LHR at 2025-06-17T12:05:00']}, {'Price': '$472.14', 'Segments': ['Flight WS1521: SFO at 2025-06-16T07:30:00 -> YYC at 2025-06-16T11:13:00', 'Flight WS18: YYC at 2025-06-16T20:35:00 -> LHR at 2025-06-17T12:05:00']}, {'Price': '$530.22', 'Segments': ['Flight B6434: SFO at 2025-06-16T06:05:00 -> BOS at 2025-06-16T14:50:00', 'Flight B61620: BOS at 2025-06-16T18:40:00 -> LHR at 2025-06-17T06:30:00']}]}, 'hotel_data': [{'name': 'HOTEL BOHEME', 'price': 278, 'Distance from Airport': 20.26081910997812}, {'name': 'SIR FRANCIS DRAKE HTL KIMPTON', 'price': 191, 'Distance from Airport': 19.126873290849105}, {'name': 'HOJO SAN FRANCISCO MARINA DIST', 'price': 261, 'Distance from Airport': 20.837350834953963}, {'name': 'CAVALLO POINT SAUSALITO', 'price': 164, 'Distance from Airport': 25.83574608295254}, {'name': 'SOFITEL LONDON HEATHROW', 'price': 187, 'Distance from Airport': 2.1329314513943785}, {'name': 'PREMIER INN HEATHROW AIRPORT', 'price': 248, 'Distance from Airport': 1.5264972519510054}, {'name': 'THAMES RIVIERA HOTEL', 'price': 188, 'Distance from Airport': 18.282807419139083}, {'name': 'MANOR HOUSE HOTEL   SPA', 'price': 235, 'Distance from Airport': 27.396695445839242}]})));
            f_out.write('\n, "0": {"Flights": "...", "Hotels": "..."}\n, "2": {"Flights": "...", "Hotels": "..."}\n}')

    except Exception as e:
        print(f"Error processing data: {e}")


def choose_one_flight_and_hotel(data):
    chosen_flight = data['flight_data']['Offers'][0]
    
    chosen_hotel = min(data['hotel_data'], key=lambda h: h['Distance from Airport'])
    
    output = {}

    flight_data = ""
    flight_data += data['flight_data']['Flight offer'].strip()
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

if __name__ == "__main__":
    main()