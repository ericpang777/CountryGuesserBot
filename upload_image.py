import requests
from CountryGuesserBot.point_generator import PointGenerator

import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

street_view_metadata_url = "https://maps.googleapis.com/maps/api/streetview/metadata"
street_view_url = "https://maps.googleapis.com/maps/api/streetview"

shapefile_folder = os.path.join(os.curdir, "data/shapefiles")
files = [f for f in os.listdir(shapefile_folder)]

num_points = 100
for f in files:
    country_name = f[:-4]
    pg = PointGenerator(country_name)
    points = pg.get_random_points(num_points)
    for i in range(num_points):
        lon, lat = points[i]
        metadata_response = requests.get(street_view_metadata_url, params={"location": f"{lat},{lon}", "key": API_KEY, "radius": 1000})
        metadata_response_json = metadata_response.json()

        if metadata_response_json["status"] == "OK":
            image_response = requests.get(street_view_url, params={"location": f"{lat},{lon}", "size": "1280x720", "key": API_KEY, "radius": 1000, "fov": 120})
            if image_response.status_code == 200:
                lat_actual = metadata_response_json["location"]["lat"]
                lon_actual = metadata_response_json["location"]["lng"]
                with open(f"data/images/{country_name}_{lat_actual}_{lon_actual}.jpg", "wb") as outfile:
                    outfile.write(image_response.content)