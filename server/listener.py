import json

def main():
    try:
        with open('form-data.txt', 'r') as f_in:
            lines = f_in.readlines()

        processed_data = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                # Here you can modify 'data' if you want before saving
                processed_data.append(data)
            except json.JSONDecodeError:
                # Handle invalid JSON line if needed
                continue

        with open('itinerary-data.txt', 'w') as f_out:
            for item in processed_data:
                json.dump(item, f_out)
                f_out.write('\n')

    except Exception as e:
        print(f"Error processing data: {e}")

if __name__ == "__main__":
    main()