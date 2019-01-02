import os
import sys
import time
import datetime
import urllib.request
import logging
import sqlite3
from bs4 import BeautifulSoup

logging.basicConfig(filename="logs/app.log", format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
STATION = "KTOL"

def stations_list():
	con = sqlite3.connect("databases/stations.db")
	cur = con.cursor()
	
	for station in cur.execute("select * from station"):
		yield station[0]

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
		if not os.path.isfile("databases/observations.db"):
			raise Exception("Observations database does not exist!")
		else:
			con = sqlite3.connect("databases/observations.db")
	except:
		raise Exception("Was not able to connect to the observations database")

	logging.info("Successfully connected to the observations database.")
	
	cur = con.cursor()
	
	counter = 1
	for station in stations_list():
		# Create a table for the station
		try:
			cur.execute(f"""create table if not exists {station}({','.join('"{0}"'.format(w) for w in forecast_elements)}, constraint unq unique (date, time))""")
			logging.info(f"Created table for {station}")
		except sqlite3.OperationalError:
			pass
	
		url = urllib.request.urlopen("https://w1.weather.gov/data/obhistory/" + station + ".html")
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
		logging.info(f"Data for {station} inserted into observations database.")
		print(f"{station} table updated. {counter} stations complete. {'{0:.4f}'.format(time.time() - start_time)} seconds elapsed.")
		counter += 1

	con.commit()
	con.close()

if __name__=='__main__':
	main()

