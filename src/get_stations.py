from bs4 import BeautifulSoup
import urllib.request
import sqlite3
import logging

URL = "https://w1.weather.gov/xml/current_obs/index.xml"
logging.basicConfig(filename="logs/app.log", format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
STATION = "KTOL"

if __name__=="__main__":
	
	# Create database and table if they do not already exist
	try:
		con = sqlite3.connect(f"databases/stations.db")
	except:
		raise Exception(f"Was not able to connect to the stations database")
	

	cur = con.cursor()
	cur.execute("""create table if not exists station('id', 'state', 'name', 'latitude', 'longitude', constraint unq unique (id))""")
	

	req = urllib.request.urlopen(URL)
	soup = BeautifulSoup(req, 'xml')

	station_table = soup.find_all('station')
	station_data = []
	for station in station_table:
		station_data.append([station.station_id.string, station.state.string, station.station_name.string, station.latitude.string, station.longitude.string])
	
	# Send the data to the database
	cur.executemany("""insert or replace into station values (?, ?, ?, ?, ?)""", station_data)
	
	# Remove Canadian and American territory stations (no data available)
	cur.execute("""delete from station where substr(id, 0, 2) <> 'K'""")
	con.commit()

	# Print the data (make sure it worked)
	#for row in cur.execute("""select * from station"""):
	#	print(row)
