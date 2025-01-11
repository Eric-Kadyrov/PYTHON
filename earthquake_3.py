import requests
import folium
from folium.plugins import MarkerCluster
import pandas as pd
import os

# Fetch earthquake data from USGS API
url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_week.geojson'
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()
else:
    print("Failed to retrieve data.")
    exit()

# Extract earthquake information
earthquakes = data['features']

# Create a map centered on the world
map_center = [20, 0]  # Latitude and longitude of the center of the world
mymap = folium.Map(location=map_center, zoom_start=2)

# Create a marker cluster to group nearby earthquakes
marker_cluster = MarkerCluster().add_to(mymap)

# Prepare data for CSV
earthquake_data = []
for earthquake in earthquakes:
    coordinates = earthquake['geometry']['coordinates']
    latitude = coordinates[1]
    longitude = coordinates[0]
    magnitude = earthquake['properties']['mag']
    place = earthquake['properties']['place']
    
    # Add a marker for each earthquake
    folium.Marker(
        location=[latitude, longitude],
        popup=f"Magnitude: {magnitude}<br>Location: {place}",
        icon=folium.Icon(color="red" if magnitude >= 5 else "blue")
    ).add_to(marker_cluster)
    
    # Store earthquake data for CSV
    earthquake_data.append({
        'Latitude': latitude,
        'Longitude': longitude,
        'Magnitude': magnitude,
        'Place': place
    })

# Save the map to an HTML file
mymap.save("earthquake_map.html")

# Save earthquake data to a CSV file
earthquake_df = pd.DataFrame(earthquake_data)
csv_file_path = "earthquake_data.csv"
earthquake_df.to_csv(csv_file_path, index=False)

# Optionally display a message
print("Map has been saved as 'earthquake_map.html'. Open this file to view the interactive map.")
print(f"The map has been saved at: {os.path.abspath('earthquake_map.html')}")

# Print the CSV file path
print(f"Earthquake data has been saved as '{csv_file_path}'.")
print(f"The CSV file has been saved at: {os.path.abspath(csv_file_path)}")
