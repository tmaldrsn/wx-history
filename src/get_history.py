import sys
import datetime
import urllib.request
import logging
import sqlite3
from bs4 import BeautifulSoup

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
STATION = "KTOL"

def main(station=STATION):
	url = urllib.request.urlopen("https://w1.weather.gov/data/obhistory/" + station + ".html")
	soup = BeautifulSoup(url, 'html.parser')

	forecast_table = soup.find_all('table')[3]	
	forecast_rows = forecast_table.find_all('tr')[3:-3]

	forecast_elements = [
		"Date", 
		"Time", 
		"Wind", 
		"Visibility", 
		"Weather", 
		"Sky Condition", 
		"Air Temperature", 
		"Dew Point", 
		"6HR Max", 
		"6HR Min", 
		"Humidty", 
		"Wind Chill", 
		"Heat Index", 
		"Altimeter Pressure", 
		"Sea Level Pressure", 
		"1HR Precip", 
		"3HR Precip", 
		"6HR Precip"
	]

	# Create a database
	try:
		con = sqlite3.connect(f"databases/{STATION}.db")
	except:
		raise Exception(f"Was not able to connect to the {STATION} database")
	
	logging.info(f"Successfully connected to {STATION}.db")
	
	cur = con.cursor()

	# Create the forecast table
	# cur.execute(f"""create table if not exists observations({','.join('"{0}"'.format(w) for w in forecast_elements)}, constraint unq unique (date, time))""")
	
	try:
		cur.execute(f"""create table observations({','.join('"{0}"'.format(w) for w in forecast_elements)}, constraint unq unique (date, time))""")
		logging.info(f"Created observations table for {STATION}")
	except sqlite3.OperationalError:
		pass

	data_rows = [[datetime.date.today().strftime(f"%m/{row.find_all('td')[0].string}/%Y")] + [element.string for element in row.find_all('td')[1:]] for row in forecast_rows]
	
	# Insert data into forecast table
	cur.executemany(f"""insert or replace into observations values ({','.join(['?' for i in range(len(forecast_elements))])})""", data_rows)
	logging.info("Current data added to database")

	con.commit()
	con.close()

if __name__=="__main__":
	main()	
