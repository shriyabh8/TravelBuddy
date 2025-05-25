import json

def main():
    try:
        last_line = None
        with open('form-data.txt', 'r') as f_in:
            for line in f_in:
                last_line = line.strip()

        if last_line:
            try:
                data = json.loads(last_line)
                with open('itinerary-data.txt', 'w') as f_out:
                    #mock data
                    f_out.write('{"Flights": "Flight To: INSERTFlight Back: INSERT", "Hotels": "hotel name and other information", "people": "3", "additionalInfo": "4"}\n')
                    f_out.write('{"location": "5", "dates": "6", "people": "7", "additionalInfo": "8"}\n')
                    f_out.write('{"location": "9", "dates": "0", "people": "1", "additionalInfo": "2"}\n')

            except json.JSONDecodeError:
                pass

    except Exception as e:
        print(f"Error processing data: {e}")

if __name__ == "__main__":
    main()