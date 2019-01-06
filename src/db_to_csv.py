import sqlite3
import csv

con = sqlite3.connect("observations.db")
cur = con.cursor()

station_query = "select * from station"

station_list = list(cur.execute(station_query))

with open('observations.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    
    for station in station_list:
        writer.writerow(station)

    for station in station_list:
        st = station[0]
        obs_query = f"select * from {st} order by substr(date, 7, 4), substr(date, 1, 2), substr(date, 4, 2), time"
        observations = list(cur.execute(obs_query))

        for obs in observations:
            writer.writerow(tuple([st] + list(obs)))