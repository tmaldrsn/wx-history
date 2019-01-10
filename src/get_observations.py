import os
import sys
import random
import time
import datetime
import urllib.request
from urllib.error import URLError
import logging
import sqlite3
from bs4 import BeautifulSoup

from connect import get_db_cursor

logging.basicConfig(filename="logs/get_observations.log", format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
DB = "observations.db"
TIMEOUT = 3

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

	stations = list(cur.execute("select * from station"))

	timed_out = []
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
		
		try:	
			req = urllib.request.urlopen(f"https://w1.weather.gov/data/obhistory/{station}.html", timeout=TIMEOUT)
			soup = BeautifulSoup(req, 'html.parser')
		except (OSError, URLError):
			logging.warning(f"Station {station} request timed out!!")
			print(f"Station {station} request timed out!")
			timed_out.append(station)
			continue

		try:
			forecast_table = soup.find_all('table')[3]	
			forecast_rows = forecast_table.find_all('tr')[3:-3]
		except IndexError:
			logging.warning(f"Station {station} data not available.")
			continue
	
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
	logging.info("Initial observations update complete, now checking for timed out stations...")
	logging.info(f"{len(timed_out)} stations timed out during first round.")
#	print(f"{len(timed_out)} stations timed out during first round: {timed_out}")

	current_round = 1
	while len(timed_out) > 0:
		current_round += 1
		for i in range(len(timed_out)):
			station = timed_out[i]
			try:	
				req = urllib.request.urlopen(f"https://w1.weather.gov/data/obhistory/{station}.html", timeout=5)
				soup = BeautifulSoup(req, 'html.parser')
			except (OSError, URLError):
				logging.warning(f"Station {station} request timed out again.. this time in round {current_round}")
#				print(f"Station {station} request timed out again.. this time in round {current_round}")
				continue

			data_rows = [[datetime.datetime.today().strftime(f"%m/{row.find_all('td')[0].string}/%Y {row.find_all('td')[1].string}")] + [element.string for element in row.find_all('td')[1:]] for row in forecast_rows]
			for j in range(1, len(data_rows)):
				init_date = datetime.datetime.strptime(data_rows[j-1][0], "%m/%d/%Y %H:%M")
				next_date = datetime.datetime.strptime(data_rows[j][0], "%m/%d/%Y %H:%M")
				if init_date != next_date:
					data_rows[j][0] = datetime.datetime.strftime(init_date - datetime.timedelta(hours=1), "%m/%d/%Y %H:%M")
			
			for k in range(len(data_rows)):
				data_rows[k][0] = data_rows[k][0][:10]
		
			# Insert data into forecast table
			cur.executemany(f"""insert or replace into {station} values ({','.join(['?' for i in range(len(forecast_elements))])})""", data_rows)
			logging.debug(f"Data for {station} inserted into observations database.")
			print(f"{station} table updated. {counter} stations complete. {'{0:.4f}'.format(time.time() - start_time)} seconds elapsed.")
			counter += 1
			timed_out[i] = ''

		timed_out = list(filter(lambda x: x != '', timed_out))
		if len(timed_out) != 0:
			print(f"Round {current_round} complete. Stations left: {len(timed_out)}: {timed_out}")
			logging.info(f"Round {current_round} of re-requesting timed out URLs complete. {len(timed_out)} stations still need updated.")
		else:
			print(f"Observations update complete after {current_round} rounds.")
			logging.info(f"Observations update complete after {current_round} rounds.")

	con.commit()
	con.close()

if __name__=='__main__':
	main()

