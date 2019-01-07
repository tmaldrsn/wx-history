import os
import sys
import random
import time
import datetime
import urllib.request
import logging
import sqlite3
from bs4 import BeautifulSoup

logging.basicConfig(filename="logs/get_observations.log", format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
DB = "observations.db"


def main():
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

	start_time = time.time()
	# Create a database
	try:
		if not os.path.isfile(DB):
			raise Exception("Observations database does not exist!")
		else:
			con = sqlite3.connect(DB)
	except:
		raise Exception("Was not able to connect to the observations database")

	logging.info("Successfully connected to the observations database.")
	
	cur = con.cursor()

	# In order to combat poor internet connection, so not only first databases get updated constantly	
	if random.random() <= 0.5:
		stations = list(cur.execute("select * from station"))
	else:
		stations = list(reversed(list(cur.execute("select * from station"))))

	counter = 1
	for station in stations:
		station = station[0]
		# Create a table for the station
		try:
			cur.execute(f"""create table if not exists {station} ({','.join('"{0}"'.format(w) for w in forecast_elements)}, constraint unq unique (date, time))""")
			logging.debug(f"Created table for {station}")
		except sqlite3.OperationalError:
			logging.info(f"Table not created for {station}")
			print(f"table not created for {station}")
			pass
	
		with urllib.request.urlopen("https://w1.weather.gov/data/obhistory/" + station + ".html") as url:
			soup = BeautifulSoup(url, 'html.parser')
	
		try:
			forecast_table = soup.find_all('table')[3]	
			forecast_rows = forecast_table.find_all('tr')[3:-3]
		except IndexError:
			logging.info(f"Station {station} data not available.")
			return
	
		data_rows = [[datetime.datetime.today().strftime(f"%m/{row.find_all('td')[0].string}/%Y {row.find_all('td')[1].string}")] + [element.string for element in row.find_all('td')[1:]] for row in forecast_rows]
		for i in range(1, len(data_rows)):
			init_date = datetime.datetime.strptime(data_rows[i-1][0], "%m/%d/%Y %H:%M")
			next_date = datetime.datetime.strptime(data_rows[i][0], "%m/%d/%Y %H:%M")
			if init_date != next_date:
				data_rows[i][0] = datetime.datetime.strftime(init_date - datetime.timedelta(hours=1), "%m/%d/%Y %H:%M")
		
		for i in range(len(data_rows)):
			data_rows[i][0] = data_rows[i][0][:10]
	
		# Insert data into forecast table
		cur.executemany(f"""insert or replace into {station} values ({','.join(['?' for i in range(len(forecast_elements))])})""", data_rows)
		logging.debug(f"Data for {station} inserted into observations database.")
		print(f"{station} table updated. {counter} stations complete. {'{0:.4f}'.format(time.time() - start_time)} seconds elapsed.")
		counter += 1

	con.commit()
	logging.info("Observations update complete.")
	con.close()

if __name__=='__main__':
	main()

