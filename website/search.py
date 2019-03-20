import numpy as np
import pandas as pd


def get_zip_coords(zipcode):
    df = pd.read_csv('data/zipcodes.csv')
    entry = df[df.Zipcode == zipcode].get_values()
    return entry.item(5), entry.item(6)


def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # radius of earth

    def rad(x):
        return np.radians(x)
    d_phi = rad(lat2) - rad(lat1)
    d_lam = rad(lon2) - rad(lon1)

    a = (np.sin(d_phi/2)**2) + np.cos(rad(lat1)) * \
        np.cos(rad(lat2)) * np.sin(d_lam/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R * c


def get_closest_station(zipcode):
    zip_lat, zip_lon = get_zip_coords(zipcode)
    stations = pd.read_csv('data/stations.csv', sep=',',
                           quotechar='|').get_values()
    closest_distance, closest_station = np.inf, ""

    for station in stations:
        station_lat, station_lon = station[3], station[4]
        distance = haversine(zip_lat, zip_lon, station_lat, station_lon)
        if distance < closest_distance:
            closest_distance = distance
            closest_station = station[0]

    return closest_station, closest_distance
