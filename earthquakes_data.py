import requests
import pandas as pd

def fetch_earthquake_data():
    # USGS Earthquake API endpoint for data from the past week
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_week.geojson"
    
    # Send a GET request to the API
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        print("Data fetched successfully!")
        return response.json()  # Return the data as a JSON object
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return None

def process_earthquake_data(data):
    # Extract the relevant fields from the JSON data
    earthquakes = data['features']
    
    # Create a list to hold earthquake information
    earthquake_list = []
    
    for quake in earthquakes:
        # Extract necessary details
        properties = quake['properties']
        coordinates = quake['geometry']['coordinates']
        
        earthquake_info = {
            'Time': properties['time'],
            'Location': properties['place'],
            'Magnitude': properties['mag'],
            'Longitude': coordinates[0],
            'Latitude': coordinates[1],
            'Depth': coordinates[2],
        }
        
        # Append to the list
        earthquake_list.append(earthquake_info)
    
    # Convert the list to a DataFrame
    earthquake_df = pd.DataFrame(earthquake_list)
    
    # Convert the 'Time' from Unix timestamp to readable date-time format
    earthquake_df['Time'] = pd.to_datetime(earthquake_df['Time'], unit='ms')
    
    return earthquake_df

def save_to_csv(df, filename="earthquake_data.csv"):
    # Save the DataFrame to a CSV file
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

def main():
    # Step 1: Fetch the data from the API
    data = fetch_earthquake_data()
    
    if data:
        # Step 2: Process the data
        earthquake_df = process_earthquake_data(data)
        
        # Step 3: Save the data to a CSV file
        save_to_csv(earthquake_df)

# Execute the main function
if __name__ == "__main__":
    main()